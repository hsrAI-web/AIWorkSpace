---
name: Salesforce metadata field access
description: Why successful custom-field deployment can still hide fields from REST calls.
---

Verify both Metadata API deployment results and REST describe access before
seeding records. Optional custom fields deployed through Metadata API may exist
in Tooling API while remaining absent from REST describe until explicit
field-level permissions are assigned, even for the connected administrator.
Required custom fields can already be visible, masking the permission gap.

**Why:** A demo seed transaction failed with "No such column" for successfully
deployed optional fields. A narrow field-permission set resolved access; adding
or recreating the fields was unnecessary.

**How to apply:** Compare Tooling definitions with REST describe before changing
schema again. Grant only the necessary field access to the intended user, and
recheck access. Use all-or-nothing seed transactions to avoid partial datasets.
