---
name: GitHub publishing
description: Repository layout and the distinction between connector readiness and native Git authentication.
---

Publish this project in `partner-operations-copilot/` within
`hsrAI-web/AIWorkSpace`, preserving the repository's other projects and history.
Do not force-push this workspace's root history onto that repository.

**Why:** The destination already contained independent Analyzer Suite and Claim
Preparation Assistant projects, with no shared history with this workspace.

**How to apply:** Synchronize the current project snapshot into its existing
subdirectory on top of the latest destination branch. Confirm that changes stay
inside that directory and use a normal, non-forced push.

Native Git authentication and the GitHub API connector have separate readiness.
An unavailable connector does not establish that native Git push is unavailable.

**Why:** The connector kept reporting an attachment-needed state after successful
authorization, while a direct Git push dry-run authenticated successfully.

**How to apply:** For repository pushes, verify native Git access safely rather
than repeatedly asking the user to reconnect the API connector. Keep credentials
inside the configured Git authentication mechanism.
