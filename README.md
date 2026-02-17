# dental-appointment-automation

flowchart TD
  A[User message in Claude Desktop] --> B{Intent detected}
  
  B -->|Book appointment| C[Extract date + time]
  B -->|Cancel appointment| D[Extract date + name info]
  B -->|Reschedule appointment| E[Extract old date + new date/time + name info]
  B -->|Check availability| F[Extract date + time]
  B -->|Suggest times| G[Extract date only]

  %% ---------------- BOOK FLOW ----------------
  C --> H[Tool: check_availability(start_time)]
  H --> I{Available?}
  I -->|No| J[Tool: suggest_slots(date)]
  J --> K[Show open times + ask user to pick one]
  K --> C

  I -->|Yes| L[Ask patient details]
  L --> L1[Collect: first name + last name]
  L1 --> L2[Collect: phone number]
  L2 --> L3[Collect: reason for visit]
  L3 --> L4[Optional: patient email]
  L4 --> M[Confirm summary with user]
  M --> N{User confirms?}
  N -->|No| L
  N -->|Yes| O[Tool: create_appointment(...)]

  O --> P[Tool: patch_event(description with name phone reason)]
  P --> Q[Generate booking code]
  Q --> R[Send confirmation email via Gmail API]
  R --> S[Done: return event link + booking code]

  %% ---------------- CANCEL FLOW ----------------
  D --> T[Tool: find_appointments(date, first, last, phone?)]
  T --> U{Matches found?}
  U -->|No| U1[Reply: no appointment found]
  U -->|Yes 1 match| V[Confirm cancel intent]
  U -->|Multiple matches| W[Ask for full name]
  W --> T
  T --> X{Still multiple?}
  X -->|Yes| Y[Ask for phone number]
  Y --> T

  V --> Z[Tool: get_event(event_id)]
  Z --> AA[Tool: delete_event(event_id)]
  AA --> AB[Send cancellation email]
  AB --> AC[Done]

  %% ---------------- RESCHEDULE FLOW ----------------
  E --> AD[Tool: find_appointments(old_date, first, last, phone?)]
  AD --> AE{Matches found?}
  AE -->|No| AE1[Reply: no appointment found]
  AE -->|Multiple| AE2[Ask name then phone]
  AE2 --> AD
  AE -->|Yes 1 match| AF[Tool: check_availability(new_start)]
  AF --> AG{New time available?}
  AG -->|No| AH[Tool: suggest_slots(new_date)]
  AH --> AI[Show times + ask user to pick]
  AI --> AF

  AG -->|Yes| AJ[Tool: get_event(old_event_id)]
  AJ --> AK[Tool: delete_event(old_event_id)]
  AK --> AL[Tool: create_appointment(new...)]
  AL --> AM[Tool: patch_event(new description)]
  AM --> AN[Send reschedule email with new details]
  AN --> AO[Done]

  %% ---------------- SAFETY ----------------
  subgraph Safety_Guards [Safety & Validation]
    SG1[Validate clinic open days Mon Tue Thu Fri]
    SG2[Validate hours 8 to 6]
    SG3[Validate only on-the-hour slots]
    SG4[Validate future times only]
    SG5[Staged filtering to avoid wrong patient]
    SG6[Do not reveal any patient info to another user]
  end
