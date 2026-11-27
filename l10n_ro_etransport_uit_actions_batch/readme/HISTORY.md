## 20.0.1.1.0 (2026-11-27)

**Changed**

- Migrated to Odoo 20. The eTransport notification of a batch comes from `l10n_ro_edi_stock`, because
  `l10n_ro_edi_stock_batch` was merged into it; the batch form is `stock.stock_picking_batch_form`
  (`stock_picking_batch` was merged into `stock`).
- The event XML is stored as raw bytes (Odoo 20 `Binary` fields), no longer base64.

## 19.0.1.1.0 (2026-11-27)

**Added**

- *Cancel* on a batch with a valid UIT opens the deletion wizard (DEL); the batch is cancelled as soon as
  ANAF receives the deletion.

## 19.0.1.0.4 (2026-11-16)

**Changed**

- Apps Store page (`static/description/index.html`) regenerated with the Terrabit template.

## 19.0.1.0.3 (2026-10-22)

- Listed on Odoo Apps as *e-Transport UIT Actions for Batches* (was *eTransport UIT Actions - Batch*). The technical name `l10n_ro_etransport_uit_actions_batch` does not change.

## 19.0.1.0.2 (2026-10-09)

- Odoo Apps banner (`static/description/main_screenshot.png`), generated from `banner.json`.

## 19.0.1.0.1 (2026-09-30)

- Own module icon in the flat style of the Terrabit modules, instead of the missing or generic one.

## 19.0.1.0.0 (2026-09-10)

- Initial release.
