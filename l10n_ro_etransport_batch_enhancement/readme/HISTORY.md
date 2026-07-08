## 18.0.0.1.2 (2026-07-08)

- **Fixed missing label on "Custom Shipping Weights" checkbox.** Same
  nested-group issue as `l10n_ro_etransport_enhancement`: the `weights` group
  on the batch form's eTransport tab nested a plain `<group>` (holding
  `total_net_weight`/`total_gross_weight`), which flips the whole outer group
  into Odoo's "OuterGroup" rendering and silently drops automatic labels for
  every plain field in it. The nested group was removed so `weights` renders
  as a normal InnerGroup with labels.
