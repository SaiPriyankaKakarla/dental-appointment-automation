from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build


class CalendarService:
    def __init__(self, service_account_file: str, calendar_id: str):
        # Store the calendar id we will book appointments into
        self.calendar_id = calendar_id

        # Permission scope for reading / writing calendar events
        scopes = ["https://www.googleapis.com/auth/calendar"]

        # Load service account credentials from the json file
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=scopes,
        )

        # Build the Google Calendar API client
        self.client = build("calendar", "v3", credentials=creds)

    def _to_rfc3339(self, dt: datetime) -> str:
        # Google expects RFC3339 like 2026-02-16T10:00:00-08:00
        return dt.isoformat()

    def list_overlapping_events(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """
        Return all events that overlap a time window.
        Used for availability checks.
        """
        resp = (
            self.client.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=self._to_rfc3339(start),
                timeMax=self._to_rfc3339(end),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return resp.get("items", [])

    def is_available(self, start: datetime, end: datetime) -> bool:
        """
        Returns True if no events overlap [start, end).
        """
        events = self.list_overlapping_events(start, end)
        return len(events) == 0

    def create_appointment(
        self,
        start: datetime,
        patient_name: str,
        patient_email: str | None = None,
        duration_minutes: int = 60,
    ) -> Dict[str, Any]:
        """
        Creates an appointment event starting at `start` for `duration_minutes`.
        Optionally adds the patient as an attendee if patient_email is provided.
        """
        end = start + timedelta(minutes=duration_minutes)

        event: Dict[str, Any] = {
            "summary": f"Dental Appointment - {patient_name}",
            "start": {"dateTime": self._to_rfc3339(start)},
            "end": {"dateTime": self._to_rfc3339(end)},
        }

        # Optional email invite to the patient (Google Calendar attendee)
        if patient_email:
            event["attendees"] = [{"email": patient_email}]

        created = (
            self.client.events()
            .insert(
                calendarId=self.calendar_id,
                body=event,
                sendUpdates="all" if patient_email else "none",
            )
            .execute()
        )
        return created

    def list_events_in_range(
        self,
        start: datetime,
        end: datetime,
        query: Optional[str] = None,
        max_results: int = 250,
    ) -> List[Dict[str, Any]]:
        """
        List events in a time range.
        query searches inside event title and description.
        """
        kwargs: Dict[str, Any] = {
            "calendarId": self.calendar_id,
            "timeMin": self._to_rfc3339(start),
            "timeMax": self._to_rfc3339(end),
            "singleEvents": True,
            "orderBy": "startTime",
            "maxResults": max_results,
        }

        if query:
            kwargs["q"] = query

        resp = self.client.events().list(**kwargs).execute()
        return resp.get("items", [])

    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Fetch a single event by id.
        Useful before cancel/reschedule so you can email details.
        """
        return (
            self.client.events()
            .get(
                calendarId=self.calendar_id,
                eventId=event_id,
            )
            .execute()
        )

    def delete_event(self, event_id: str) -> None:
        """
        Delete an event by id.
        """
        self.client.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id,
            sendUpdates="none",
        ).execute()

    def patch_event(self, event_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update part of an event by id.
        Example body {"description": "..."}
        """
        return (
            self.client.events()
            .patch(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=body,
                sendUpdates="none",
            )
            .execute()
        )
