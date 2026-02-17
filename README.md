# dental-appointment-automation

## Workflow Diagram (Mermaid)

```mermaid
flowchart TD
  A[User message in Claude Desktop or Chat UI] --> B{Intent detected}

  %% ---------------- INTENT ROUTING ----------------
  B -->|Book appointment| C[Extract date + time]
  B -->|Check availability| F[Extract date + time]
  B -->|Suggest times| G[Extract date only]
  B -->|Cancel appointment| D[Extract date + patient info]
  B -->|Reschedule appointment| E[Extract old date + new date time + patient info]

  %% ---------------- AVAILABILITY ONLY ----------------
  F --> F1[Tool check_availability(start_time)]
  F1 --> F2{Available?}
  F2 -->|Yes| F3[Reply Available with start end]
  F2 -->|No| F4[Reply Not available + reason]
  F4 --> F5[Optional Tool suggest_slots(date)]
  F5 --> F6[Reply with open slots]

  %% ---------------- SUGGEST TIMES ONLY ----------------
  G --> G1[Tool suggest_slots(date)]
  G1 --> G2{Clinic closed?}
  G2 -->|Yes| G3[Reply Clinic closed suggest another day]
  G2 -->|No| G4[Reply list of available 60 min start times]

  %% ---------------- BOOK FLOW ----------------
  C --> H[Tool check_availability(start_time)]
  H --> I{Available?}
  I -->|No| J[Tool suggest_slots(date)]
  J --> K[Show open times + ask user to pick one]
  K --> C

  I -->|Yes| L[Ask patient details]
  L --> L1[Collect first name + last name]
  L1 --> L2[Collect phone number]
  L2 --> L3[Collect reason for visit]
  L3 --> L4[Optional collect patient email]
  L4 --> M[Confirm summary with user]
  M --> N{User confirms?}
  N -->|No edit| L
  N -->|Yes| O[Tool create_appointment(name time phone reason email)]
  O --> P[Tool patch_event(add PatientFirst PatientLast Phone Reason)]
  P --> Q[Generate booking code]
  Q --> R[Send confirmation email via Gmail API]
  R --> S[Done return event link + booking code]

  %% ---------------- FIND APPOINTMENTS (USED BY CANCEL + RESCHEDULE) ----------------
  D --> T[Tool find_appointments(date first last phone)]
  E --> T
  T --> U{Matches found?}
  U -->|No| U1[Reply no appointment found ask for correct date]
  U -->|Yes one match| V[Show match and ask confirm]
  U -->|Multiple matches| W{Have full name?}
  W -->|No| W1[Ask first + last name]
  W -->|Yes| X{Have phone number?}
  X -->|No| X1[Ask phone number]
  X -->|Yes but still multiple| X2[Ask user to pick time from list]

  %% ---------------- CANCEL FLOW ----------------
  V --> Vc{Cancel requested?}
  Vc -->|Cancel| Y[Tool cancel_appointment(event_id)]
  Y --> Y1[Send cancellation email via Gmail API]
  Y1 --> Y2[Done cancellation confirmed]
  Vc -->|Not cancel| Vn[Stop]

  %% ---------------- RESCHEDULE FLOW ----------------
  E --> E1[Ask for new desired date + time]
  E1 --> E2[Tool check_availability(new_start_time)]
  E2 --> E3{New time available?}
  E3 -->|No| E4[Tool suggest_slots(new_date)]
  E4 --> E5[Show slots ask user to pick one]
  E5 --> E1
  E3 -->|Yes| E6[Confirm reschedule summary]
  E6 --> E7{User confirms?}
  E7 -->|No| E1
  E7 -->|Yes| E8[Delete old event]
  E8 --> E9[Create new appointment]
  E9 --> E10[Send reschedule email via Gmail API]
  E10 --> E11[Done return new link + booking code]

  %% ---------------- SAFETY + GUARDRAILS (ALWAYS ON) ----------------
  S --> Z[Safety do not reveal other patients info]
  Y2 --> Z
  E11 --> Z
  Z --> Z1[If multiple matches show only times not names]
  Z1 --> Z2[Require staged confirmation name then phone]
  Z2 --> Z3[Validate clinic hours Mon Tue Thu Fri 8 to 6]
  Z3 --> Z4[Reject past times and Sundays]
