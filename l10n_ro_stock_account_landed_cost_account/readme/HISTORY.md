# Changelog

## 18.0.1.1.0

- Added a **Landed Cost Class 6 Method** company selector (Accounting / Romania
  settings) that makes the behaviour explicit and configurable per company:
  - **Standard** (default): native Odoo behaviour (`stock valuation = class 6`);
  - **Through intermediary account**: routes the class 6 credit through the
    intermediary account, producing two clean balanced notes for the SAGA export.
  The intermediary account is now shown and required only for the intermediary
  method, and the selector — not the mere presence of the account — controls the
  behaviour. Existing companies default to **Standard**, so behaviour is unchanged
  on upgrade unless the method is explicitly switched.

## 18.0.1.0.0

- Added an optional **Landed Cost Intermediary Account** company setting (Accounting /
  Romania settings). This is the technical intermediary account (e.g. `482.99`)
  used to transfer service costs into products on landed cost validation. When set,
  a landed cost entry that would credit a class 6 (expense) account is routed
  through this account, producing two clean balanced notes
  (`stock valuation = intermediary account` and `intermediary account = class 6`) instead
  of a direct `stock valuation = class 6` entry. This keeps the notes acceptable
  for the SAGA export. Class `609` is never rerouted. When the setting is empty,
  the standard behaviour is unchanged.
- Added dependency on `l10n_ro_config` (Romania settings block).
