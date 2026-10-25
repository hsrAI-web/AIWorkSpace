---
name: Generated browser API typing
description: TypeScript lib requirement for Orval-generated browser fetch code.
---

When generated API client code uses `Headers.entries()`, the API client TypeScript `lib` list must include `dom.iterable` alongside `dom`.

**Why:** The generator emits header-iteration code that typechecks only when the iterable DOM declarations are included.

**How to apply:** If API codegen succeeds but `typecheck:libs` reports that `Headers.entries` does not exist, check `lib/api-client-react/tsconfig.json` for `dom.iterable` before changing generated output.
