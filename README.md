## Project Overview

This project is an AI-powered **dental appointment automation** built with an **MCP server** that connects a chat experience (Claude Desktop / chat UI) to real clinic workflows.

It supports:
- **Book appointments** (checks availability, collects patient details, confirms, then creates the calendar event)
- **Suggest available slots** for a selected date
- **Cancel appointments** with staged confirmation (name → phone if needed)
- **Reschedule appointments** safely (checks new slot first, then moves the booking)
- **Email notifications** via Gmail API for confirmations, cancellations, and reschedules

Key integrations:
- **Google Calendar API** (service account) for scheduling and conflict checks
- **Gmail API** (OAuth) for sending patient emails
- **Safety precautions**: avoids leaking other patient info, staged filtering for duplicates, validates clinic hours and rejects invalid times

**Please refer Workflow Chat.png for an overview**
