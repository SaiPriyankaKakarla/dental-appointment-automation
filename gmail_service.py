from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Optional

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GmailService:
    """
    Sends emails using Gmail API (OAuth).
    Uses:
      - GMAIL_OAUTH_CLIENT_FILE: your OAuth client json file (downloaded from Google Cloud)
      - GMAIL_TOKEN_FILE: token json created after first login
      - CLINIC_EMAIL_FROM: the gmail address that sends the email (must be the logged in account)
    """

    def __init__(self, oauth_client_file: str, token_file: str, from_email: str):
        self.oauth_client_file = oauth_client_file
        self.token_file = token_file
        self.from_email = from_email
        self.scopes = ["https://www.googleapis.com/auth/gmail.send"]
        self.client = build("gmail", "v1", credentials=self._load_creds())

    def _load_creds(self) -> Credentials:
        creds: Optional[Credentials] = None

        try:
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        except Exception:
            creds = None

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(self.token_file, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
            return creds

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.oauth_client_file, self.scopes)
            creds = flow.run_local_server(port=0)
            with open(self.token_file, "w", encoding="utf-8") as f:
                f.write(creds.to_json())

        return creds

    def send_email(self, to_email: str, subject: str, body_text: str) -> dict:
        msg = EmailMessage()
        msg["To"] = to_email
        msg["From"] = self.from_email
        msg["Subject"] = subject
        msg.set_content(body_text)

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        resp = self.client.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"ok": True, "message_id": resp.get("id")}
