---
name: Salesforce data model boundaries
description: User-approved distinction between registrations, Opportunities, and Quotes.
---

Use a dedicated Deal_Registration__c object linked to partner Accounts and
Opportunities. Use native Salesforce Quotes when available, not an unapproved
custom quote object. Keep registration status, Opportunity stage, and quote
status distinct.

**Why:** The user explicitly selected and approved this model. A sales stage does
not establish a partner registration's approval status.

**How to apply:** Check capabilities in the currently connected org. If the
approved object cannot be created or native Quotes are unavailable, explain the
limitation and ask before substituting a different model. Do not label synthetic
quote data as live Salesforce data.
