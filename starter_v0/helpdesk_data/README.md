# Fictional Helpdesk Data

All records in this folder are synthetic and deterministic. They exist only for
the lab and contain no real employee or company data.

- `assets.json`: 9 mock assets across laptops, desktop, mobile, printer, and meeting room.
- `users.json`: 10 mock employees with varied account/MFA states and assigned assets.
- `service_status.json`: mock shared-service status page.
- `approved_software.json`: mock approved-software catalog by version and operating system.
- `ticket_status.json`: 3 read-only mock ticket records.
- `maintenance_windows.json`: planned mock maintenance windows for shared services.
- `knowledge_base/`: 11 troubleshooting articles, including one safe prompt-injection fixture.

Students may extend this data when they build a new tool, but they must document
their contract and add eval cases for the behavior they introduce.
