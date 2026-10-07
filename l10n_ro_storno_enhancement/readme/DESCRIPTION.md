This module provides enhancements for handling "storno" (negative/red) accounting entries according to Romanian accounting standards.

**Key Features:**

- **Negative (Red) Accounting Entries:**
  Automatically calculates debit and credit values as negative numbers for storno lines, ensuring correct ledger reporting in the Romanian localization.
- **Account Usage Configuration:**
  Adds a "Usage" field to General Ledger accounts (Debit, Credit, or Bivalent), allowing for automatic redirection of amounts to the correct column based on Romanian accounting rules.
- **Improved Storno Logic:**
  Extends the default Odoo reversal logic to mark moves and lines as "storno," ensuring that balances are correctly decreased rather than increased on the opposite side.
- **Company-level Activation:**
  The storno behavior is controlled by a company-level setting, allowing for flexibility across different entities.
