---
name: Artifact command working directories
description: Working-directory differences when invoking shared scripts from managed artifact services.
---

Managed artifact development commands run from the artifact directory, while this project's production commands run from the repository root.

**Why:** A repository-root-relative shell script command passed validation but failed at development startup because the artifact workflow resolved it from its own directory. The previous production Node command had already demonstrated repository-root execution.

**How to apply:** Use artifact-relative paths for development commands and repository-root paths for production commands. Shared scripts should resolve and change to their own repository root before launching child processes. Schema validation alone does not verify the command's working directory.
