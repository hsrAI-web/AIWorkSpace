# Salesforce deal-registration schema

This directory contains the user-approved Metadata API package for a dedicated
`Deal_Registration__c` object. It links registrations to partner Accounts and
Opportunities and keeps registration status separate from Opportunity stage.

## Deployment status

The approved object and six fields are deployed in the connected **Developer
Edition** org. The previous Starter org failed check-only validation with
`reached maximum number of custom objects`; no custom object was created there.

Use Metadata API with `singlePackage=true`, `rollbackOnError=true`, and
`RunLocalTests` for this org. Validate with `checkOnly=true` before deployment.
Deploy only the named components in `package.xml`, not a wildcard package.
Optional custom fields also need field-level security: the targeted permission
set in this package was assigned to the connected administrator so the approved
seed records could include all fields. It grants no system permissions and was
not assigned to other users.

## Quotes

The user selected native Salesforce Quotes, not a custom quote object.
The connected org did not expose the standard Quote object during discovery.
Quote examples must remain explicitly synthetic until native Quote access is
available and verified.

## Sample records

The Developer Edition contains four `DEMO ONLY` Accounts, three Opportunities,
three explicitly created OpportunityPartner links, and these registrations:

| Registration | Partner | Registration status | Opportunity stage |
| --- | --- | --- | --- |
| DR-0001 | Red Valley | In Review | Qualify |
| DR-0002 | Bluewater | Needs Information | Propose |
| DR-0003 | Red Valley | Approved | Closed Won |

The initial all-or-nothing record batch rolled back because the optional fields
were not visible before field-level security was assigned. The successful retry
created the rows above without duplicates.

## Application access

The Express API uses the Replit connectors SDK with server-managed credentials.
It checks the approved Developer Edition org identity and queries only the three
allowlisted registrations and two partner Accounts. It exposes no arbitrary SOQL
and no Salesforce write endpoints. Actual administrator names are not returned
to the public demo.

The UI polls every minute, permits manual refresh, and displays source and
freshness. Each agent request reads a fresh, partner-scoped snapshot server-side
and passes it to the Python LangGraph tools. Missing Salesforce data is never
replaced with local examples for a Salesforce partner.

The four older local example partners remain available for synthetic quote and
registration examples. Native Quotes are not exposed by the connected org and
are not represented by Opportunity stages.

If switching orgs, stop and update the approved org/record allowlist after
verification. Salesforce IDs are org-specific. Query existing demo records
before inserting again.

Application access should be read-only. Do not put OAuth tokens, passwords, or
other credentials in this directory.
