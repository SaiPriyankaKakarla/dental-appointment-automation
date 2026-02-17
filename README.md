User message
  |
  +-- Book appointment
  |     |
  |     +-- check_availability(date/time)
  |     |      |
  |     |      +-- Not available --> suggest_slots(date) --> user picks --> check again
  |     |      |
  |     |      +-- Available --> ask details (name, phone, reason, optional email)
  |     |                      --> confirm summary
  |     |                      --> create_appointment
  |     |                      --> patch_event(description)
  |     |                      --> generate booking code
  |     |                      --> send confirmation email
  |     |
  |     +-- End
  |
  +-- Cancel appointment
  |     |
  |     +-- find_appointments(date, name)
  |             |
  |             +-- No matches --> tell user none found
  |             +-- Multiple matches --> ask full name --> still multiple --> ask phone
  |             +-- One match --> confirm cancel --> get_event --> delete_event --> send cancel email
  |
  +-- Reschedule appointment
        |
        +-- find_appointments(old date, name)
               |
               +-- No matches --> tell user none found
               +-- Multiple matches --> ask full name --> still multiple --> ask phone
               +-- One match --> check_availability(new time)
                                |
                                +-- Not available --> suggest_slots(new date) --> user picks --> check again
                                +-- Available --> get_event(old) --> delete_event(old)
                                               --> create_appointment(new) --> patch_event(new)
                                               --> send reschedule email
