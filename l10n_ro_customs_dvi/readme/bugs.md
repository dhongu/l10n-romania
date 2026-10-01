# Identified bugs

Reviewed: 2026-10-01
Target version: Odoo 20.0
Scope: Source review and isolated method validation. Integration-test results are reported separately below when available.

## [P1] Customs wizard uses the active company instead of the invoice company

**Status:** Open — documented, not fixed.

**Location:** `wizard/account_dvi.py:73, :116–122 and :140–176`. Line numbers refer to the reviewed source and may change.

### Cause

Default taxes, customs payable account and wizard currency are taken from env.company. The created stock.landed.cost values omit company_id, so its core default also uses env.company even though the selected invoice journal and pickings can belong to another allowed company.

### Impact

When company A is active and an invoice from allowed company B is selected, the DVI can be initialized with A tax/accounts/currency and created under A with B journal/pickings. Validation or posting can fail, or the draft can belong to the wrong company.

### Reproduction

Allow companies A and B, keep A active, and open the DVI wizard from a B vendor bill. Inspect default tax/currency and the company of the generated landed cost.

### Recommended correction

Run the workflow in invoice.company_id, explicitly set company_id on the landed cost, and select taxes/accounts/product company-dependent properties in that same company.

### Validation

The wizard defaults, account lookup and created values were compared with the core stock.landed.cost.company_id default. No DVI or journal entry was created during this review.
