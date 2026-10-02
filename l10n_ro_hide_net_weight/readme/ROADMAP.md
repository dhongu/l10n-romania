## Retragerea `l10n_ro_net_weight`

Modulul există doar pentru a ascunde câmpul `l10n_ro_net_weight` din `l10n_ro_stock`.

1. Se păstrează cât timp `l10n_ro_stock` definește câmpul.
2. Când câmpul este scos din `l10n_ro_stock` (vezi ROADMAP-ul acelui modul), vederile ascunse nu mai au
   țintă: modulul se declară învechit și se elimină (inclusiv din `depends` ale proiectelor care îl folosesc).
3. Până atunci nu se adaugă logică nouă pe `l10n_ro_net_weight`; e-Transport folosește
   `product.weight` (vezi `l10n_ro_edi_stock` și `l10n_ro_etransport_enhancement`).
