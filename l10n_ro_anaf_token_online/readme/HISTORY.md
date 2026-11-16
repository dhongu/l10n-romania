## 20.0.1.0.1 (2026-11-16)

- Am pus înapoi `__init__.py` gol: uneltele OCA (manifestoo, oca-checks-odoo-module) nu
  recunosc un modul fără el, așa că pica CI-ul suitelor care depind de acest modul.
  Modulul tot nu are cod Python și se importă în continuare pe Odoo Online.
- Marcaj Odoo Online explicit: `"online": true` în `static/description/banner.json`
  (bannerul nu îl mai deduce din lipsa fișierelor `.py`).

## 20.0.1.0.0

- Portare pe 20.0 (din 19.0.1.0.0, dhongu/l10n-romania#809). Necesită `deltatech_iap_online`
  20.0.1.2.0 sau mai nou (cererea creată *Done* nu e trimisă la server și apare în *Consum credite*)
  și `terrabit_iap_server_anaf` 19.0.1.5.0 pe server (serverul Terrabit rămâne pe 19.0).

## 19.0.1.0.0

- Prima versiune: varianta fără Python a modulului `terrabit_iap_anaf`, importabilă pe Odoo Online.
  Tokenul vine de la serverul Terrabit pe o automatizare *On webhook* (în locul rutei
  `/iap/anaf_token_response`), care oprește și acțiunea programată de reînnoire e-Factura; butonul
  Generează token (Terrabit) trimite adresa acestui webhook în linkul de autorizare. O autorizare
  costă 1 credit și apare în *Consum credite*. Acțiunea programată, comună tuturor firmelor, se
  oprește doar când toate firmele cu token ANAF îl primesc de la Terrabit. Necesită `terrabit_iap_server_anaf` 19.0.1.5.0 pe
  server și `deltatech_iap_online` 19.0.1.2.0.
