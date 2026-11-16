## 19.0.1.0.1 (2026-11-16)

- Am pus înapoi `__init__.py` gol: uneltele OCA (manifestoo, oca-checks-odoo-module) nu
  recunosc un modul fără el, așa că pica CI-ul suitelor care depind de acest modul.
  Modulul tot nu are cod Python și se importă în continuare pe Odoo Online.
- Marcaj Odoo Online explicit: `"online": true` în `static/description/banner.json`
  (bannerul nu îl mai deduce din lipsa fișierelor `.py`).

## 19.0.1.0.0

- Prima versiune: varianta fără Python a modulului `l10n_ro_picking_report`, importabilă pe Odoo
  Online. Calculul liniilor și al totalurilor din rapoarte (prețuri în unitatea documentului, TVA,
  preț de vânzare, adaos) este scris în QWeb și dă aceleași valori ca modelele Python ale modulului
  clasic (verificat linie cu linie). Câmpurile sunt manuale (`x_l10n_ro_*`), setările sunt pe firmă,
  iar delegatul, prețul de vânzare la recepție și referința furnizorului sunt automatizări.
- Corecturi față de modulul clasic: rapoartele de recepție tipăresc doar recepțiile; gestionarul și
  capitalul social se tipăresc doar când sunt completate; starea *Ciornă* se vede pe documente;
  totalul bonului de consum e aliniat la dreapta; traducerile „Recepție fără TVA”, „Semnătura”,
  „Din locația”, „Document sursă”, „recepționarea mărfurilor”.
