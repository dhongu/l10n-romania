## Retragerea `l10n_ro_net_weight`

Modulul există doar pentru a ascunde câmpul `l10n_ro_net_weight`, definit de `l10n_ro_stock_base`
(înainte, de modulul OCA `l10n_ro_stock`).

1. Se păstrează cât timp `l10n_ro_stock_base` definește câmpul.
2. Dacă câmpul este scos din `l10n_ro_stock_base`, vederile ascunse nu mai au țintă: modulul se declară
   învechit și se elimină (inclusiv din `depends` ale proiectelor care îl folosesc).
3. Ascunderea nu golește valorile: `l10n_ro_etransport_enhancement` calculează greutatea netă a liniilor
   de greutăți la expediere din `l10n_ro_net_weight`, când câmpul există.
