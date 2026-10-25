---
name: Nebius model availability
description: Avoid confusing stale model examples with invalid provider credentials.
---

Use the authenticated provider model catalog to confirm model availability rather than assuming model IDs in documentation examples remain available.

**Why:** A documented embedding model returned model_not_found even while the same configured credential successfully ran chat completions; the live catalog exposed a different embedding model.

**How to apply:** When a model returns model_not_found, check the live catalog before requesting replacement credentials or changing providers.
