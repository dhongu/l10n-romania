# Changelog

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
