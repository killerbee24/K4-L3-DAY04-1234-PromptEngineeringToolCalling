---
name: check_maintenance_window
track: bonus
kind: local_status
provider: mock_maintenance_calendar
requires_env: []
inputs: [service, environment]
outputs: [status, windows, snapshot_at, timezone, source]
side_effect: false
---
# check_maintenance_window

Returns planned maintenance windows for one fictional shared service and
environment. It is separate from current service health and does not schedule,
cancel, or authorize maintenance. Missing or invalid inputs return clear errors.
