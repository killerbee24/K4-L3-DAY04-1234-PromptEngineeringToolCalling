---
name: lookup_ticket_status
track: bonus
kind: local_status
provider: mock_ticket_status_store
requires_env: []
inputs: [ticket_id]
outputs: [ticket, snapshot_at, source]
side_effect: false
---
# lookup_ticket_status

Looks up one fictional support ticket by its exact ticket ID. It is read-only,
returns only support-safe mock fields, and never searches real ticket systems.
Unknown IDs return a deterministic `ticket_not_found` error.
