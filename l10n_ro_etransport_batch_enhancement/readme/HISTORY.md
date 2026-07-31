## 19.0.0.3.1

**Corecție** — la fel ca în `l10n_ro_etransport_enhancement`, documentele însoțitoare
declarate pe lot fără observație generau `observatii=""` în XML, respins de ANAF
(`Str200`, minLength=1). Atributul este acum omis când observația lipsește.
