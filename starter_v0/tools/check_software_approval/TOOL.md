---
name: check_software_approval
track: bonus
kind: local_inventory
provider: mock_approved_software_catalog
requires_env: []
inputs: [software_name, version, operating_system]
outputs: [status, matched_product, requested_version, approved_versions, recommendation, source]
side_effect: false
---
# check_software_approval

Checks whether a named software version is approved for a fictional managed
operating system. It reads only the local mock catalog and never installs,
updates, or removes software. A software name, version, and operating system
are all required; missing or unknown inputs return explicit errors.
