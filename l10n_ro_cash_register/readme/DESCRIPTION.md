Registrul de casă ca **document numerotat**, cod 14-4-7A (OMFP 2634/2015).

**Funcționalități:**

- un document per (casierie, zi), cu numerotare proprie prin secvență, unic pe dată și jurnal;
- sold inițial preluat automat din ziua precedentă și sold final calculat;
- mișcările zilei — încasări, plăți, explicația operațiunii și partenerul;
- chatter și activități pe document, pentru urmărire și responsabil;
- tipărire în forma cerută de formular.

Soldurile și mișcările se citesc din notele contabile postate de pe contul de casă al
jurnalului (`default_account_id`, ex. 5311).

## Care variantă alegeți

Suita oferă două forme de registru de casă, cu **aceleași cifre**, citite din aceleași linii
contabile. Diferă ce puteți face cu ele:

- **acest modul** produce **documentul**: numerotat, cu o filă per zi, arhivabil și tipăribil în
  forma formularului. Este varianta pentru evidența care se păstrează și se prezintă la control.
  Merge pe Odoo Community.
- **`l10n_ro_cash_register_report`** (suita `l10n_ro_ent`) produce **raportul**: interval de mai
  multe zile, filtru de jurnale, derulare pe niveluri, drill-down la nota contabilă și export
  PDF/XLSX. Este varianta pentru verificare și analiză, dar **nu numerotează** nimic. Cere
  Odoo Enterprise (`account_reports`).

Cele două nu se exclud și pot fi instalate împreună. Când sunt amândouă, folosiți documentul de
aici pentru evidența oficială și raportul pentru verificări pe perioade.
