# M13 — Finance, HR & Legal Ops

**Scope:** billing, accounting, payroll, e-signature, contract lifecycle

## Servers

| # | MCP Server | Purpose | Used by squads | Auth | Transport | Criticality |
|---|---|---|---|---|---|---|
| 1 | Stripe | Billing, subscriptions, and payment processing | S07, S16, S22, S30 | API key | HTTP/SSE | Critical |
| 2 | NetSuite | General ledger, accounting, and financial reporting | S16, S22, S35 | OAuth2 | HTTP | Critical |
| 3 | QuickBooks | Bookkeeping for small entities and subsidiaries | S16, S35 | OAuth2 | HTTP/SSE | High |
| 4 | Workday | HR, headcount, and finance master data | S12, S16, S24 | Service account | HTTP | Critical |
| 5 | BambooHR | HR records, time off, and employee lifecycle | S24, S26 | API key | HTTP | High |
| 6 | Gusto | Payroll processing and benefits administration | S24, S26 | OAuth2 | HTTP/SSE | High |
| 7 | DocuSign | E-signature and envelope workflow automation | S22, S24, S27 | OAuth2 | HTTP/SSE | High |
| 8 | Ironclad | Contract lifecycle management and negotiation | S22, S27 | API key | HTTP | High |
| 9 | Greenhouse | Recruiting, requisitions, and hiring pipeline | S24, S26 | API key | HTTP/SSE | Medium |
| 10 | Avalara | Sales tax calculation and compliance | S16, S22 | API key | HTTP | Medium |
| 11 | Bill.com | Accounts payable, invoicing, and payments | S16, S35 | OAuth2 | HTTP/SSE | High |
| 12 | Expensify | Expense capture, approval, and reimbursement | S16, S24 | Token | HTTP/SSE | Medium |
| 13 | Coupa | Procurement, spend, and vendor management | S16, S35 | OAuth2 | HTTP | Medium |

## Notes

| # | Note |
|---|---|
| 1 | Stripe, NetSuite, and Workday are foundational; billing, accounting, and HR operations depend on them across multiple squads. |
| 2 | E-signature and contract servers (DocuSign, Ironclad) are tightly coupled — contract approvals depend on both, so they should be rolled out together. |
| 3 | These servers handle financial and personal data; adoption requires least-privilege scopes and access reviews before rollout. |
| 4 | Payroll and tax servers are compliance-sensitive and change on regulatory cycles, so they are maintained centrally rather than per squad. |
