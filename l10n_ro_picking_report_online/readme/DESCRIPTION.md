Documentele de stoc românești, și pe **Odoo Online**: modulul nu conține cod Python și se importă ca
arhivă zip (Aplicații > Importați modulul). Este varianta fără Python a modulului
`l10n_ro_picking_report`, pentru bazele în care codul Python propriu nu poate rula. Are nevoie de
`l10n_ro_invoice_report_online` (și, prin el, de `l10n_ro_report_common_online`), importate înainte.

Rapoarte, din meniul **Tipăriți** al transferului:

- **Recepție (NIR)**, **Recepție fără TVA** și **Recepție cu preț de vânzare** (tipăresc doar
  recepțiile): preț unitar, valoare,
  TVA, preț de vânzare, adaos în procente; cantitățile și prețurile în unitatea de pe document
  (o cutie de 13 kg rămâne cutie), prețul din comanda de achiziție sau din valoarea mișcării.
- **Aviz** și **Aviz cu preț** (livrarea): prețul din comanda de vânzare (cu discount, cu TVA inclus
  sau nu); pe livrările fără comandă, prețul din lista de prețuri a clientului, altfel prețul de listă.
- **Aviz de însoțire a mărfii** (14-3-6A): livrarea bifată *Aviz de însoțire* se tipărește cu acest
  titlu; celelalte au titlul *Livrare*.
- **Bon de consum** și **Transfer intern** (cu prețuri de vânzare când locația e magazin).

Pe documente: datele firmei și conturile bancare, gestionarul locației, delegatul și mijlocul de
transport, numărul AWB (când e instalat modulul de curierat), semnăturile.

**Setări**, pe firmă, în fila *Factură România*, grupul *Documente de stoc*: ascunde TVA pe NIR,
ascunde băncile pe documentele de stoc. Pe locație: lista de prețuri a magazinului, gestionarul,
*Este locație de tip magazin*.

**Automatizări** (în locul codului Python): delegatul aduce mijlocul de transport; prețul de vânzare
se fixează pe mișcare la validarea recepției; recepția din comanda de achiziție primește ca document
sursă referința furnizorului.

Ce nu face, față de `l10n_ro_picking_report`: rapoartele cumulative pe perioadă, butonul *Tipăriți*
care alege singur raportul, facturarea din livrare cu delegatul și atașarea livrării semnate.

### Odoo Online

Modulul nu conține Python: se poate importa pe Odoo Online (planul Custom) din Aplicații > Importați
modulul. Nu se poate instala împreună cu `l10n_ro_picking_report` (manifestul îl exclude, iar importul
zip este refuzat cât timp acel modul e instalat): cele două țin aceleași date în câmpuri diferite.
