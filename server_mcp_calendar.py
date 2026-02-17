from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build


class CalendarService:
    def __init__(self, service_account_file: str, calendar_id: str):
        # Save calendar id we will read/write appointments to
        self.calendar_id = calendar_id

        # Full calendar read/write scope
        scopes = ["https://www.googleapis.com/auth/calendar"]

        # Load service account credentials from json file
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=scopes,
        )

        # Build Google Calendar API client
        self.client = build("calendar", "v3", credentials=creds)

    def _to_rfc3339(self, dt: datetime) -> str:
        # Google expects RFC3339 like 2026-02-16T10:00:00-08:00
        return dt.isoformat()

    def list_overlapping_events(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        # Safety check so we don’t call Google with a bad window
        if end <= start:
            return []

        # List events that overlap the given time window
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
        # Returns True if there are no overlapping events
        events = self.list_overlapping_events(start, end)
        return len(events) == 0

    def create_appointment(
        self,
        start: datetime,
        patient_name: str,
        patient_email: str | None = None,
        duration_minutes: int = 60,
    ) -> Dict[str, Any]:
        # Basic safety checks
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be > 0")

        patient_name = (patient_name or "").strip()
        if not patient_name:
            patient_name = "Patient"

        # Compute end time
        end = start + timedelta(minutes=duration_minutes)

        # Build event payload
        event: Dict[str, Any] = {
            "summary": f"Dental Appointment - {patient_name}",
            "start": {"dateTime": self._to_rfc3339(start)},
            "end": {"dateTime": self._to_rfc3339(end)},
        }

        # Optional attendee invite
        if patient_email:
            event["attendees"] = [{"email": patient_email.strip()}]

        # Insert event into calendar
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
        if end <= start:
            return []

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

    # ✅ NEW
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get one event by event_id.
        Useful for cancel/reschedule emails (read details before deleting).
        """
        if not event_id or not event_id.strip():
            raise ValueError("event_id is required")

        return (
            self.client.events()
            .get(
                calendarId=self.calendar_id,
                eventId=event_id.strip(),
            )
            .execute()
        )

    def delete_event(self, event_id: str) -> None:
        """
        Delete an event by id.
        """
        if not event_id or not event_id.strip():
            raise ValueError("event_id is required")

        self.client.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id.strip(),
            sendUpdates="none",
        ).execute()

    def patch_event(self, event_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update part of an event by id.
        Example body {"description": "..."}
        """
        if not event_id or not event_id.strip():
            raise ValueError("event_id is required")

        if not isinstance(body, dict) or not body:
            raise ValueError("body must be a non-empty dict")

        return (
            self.client.events()
            .patch(
                calendarId=self.calendar_id,
                eventId=event_id.strip(),
                body=body,
                sendUpdates="none",
            )
            .execute()
        )
