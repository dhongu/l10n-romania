## 19.0.1.2.0 (2026-11-27)

**Added**

- *Cancel* on a transfer with a valid UIT opens the deletion wizard (DEL) instead of cancelling directly;
  the transfer is cancelled as soon as ANAF receives the deletion. A transfer can no longer be cancelled
  while its UIT stays valid at ANAF.
- If ANAF later refuses the deletion of a cancelled transfer's UIT, a warning activity is scheduled on the
  transfer so the UIT is deleted again.

## 19.0.1.1.4 (2026-11-16)

**Changed**

- Apps Store page (`static/description/index.html`) regenerated with the Terrabit template.

## 19.0.1.1.3 (2026-10-22)

- Listed on Odoo Apps as *e-Transport UIT Actions* (was *eTransport UIT Actions*). The technical name `l10n_ro_etransport_uit_actions` does not change.

## 19.0.1.1.2 (2026-10-09)

- Odoo Apps banner regenerated in the current Terrabit style, with the module icon.

## 19.0.1.1.1 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

## 19.0.1.0.0 (2026-09-10)

- Initial release: delete, confirm and change-vehicle events for an existing UIT, with status polling.

## 19.0.1.1.0 (2026-09-10)

- Extension point `_get_parent()` on the event and the wizard, so the batch module can attach
  events to a transfer batch without duplicating the logic.
