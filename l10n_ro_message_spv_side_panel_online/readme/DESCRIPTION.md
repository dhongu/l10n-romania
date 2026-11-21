Vedere împărțită pentru mesajele e-Factura (SPV) și pe **Odoo Online**: lista sau cardurile
mesajelor în stânga, iar în dreapta, într-un panou, factura așa cum e în XML. Modulul nu are cod
Python și se importă ca arhivă zip (*Aplicații > Importă modul*); funcționează peste registrul
`l10n_ro_message_spv_online` și peste panoul lateral `deltatech_web_side_panel`, deci peste modulul
standard `l10n_ro_edi`.

- **Meniul „Mesaje SPV (vedere împărțită)”** din Facturare (Contabilitate): vizualizări kanban și
  listă pe mesajele SPV (`l10n_ro_edi.document`), cu aceleași filtre ca registrul.
- **Panoul din dreapta**: partenerul, factura, totalul, starea, mesajul ANAF, fișierele mesajului și
  documentul facturii, desenat în browser din XML-ul factură: casete cu cealaltă parte (furnizorul
  la factura primită, clientul la cea trimisă), factura și firma noastră, apoi liniile și totalurile.
  CUI-ul din XML se citește tot în browser.
- **Sursa XML-ului**: pentru o factură trimisă și încă în așteptare, XML-ul trimis; altfel, fișierul
  XML atașat facturii (factura de furnizor descărcată din SPV). Dacă XML-ul nu e disponibil
  (factură trimisă deja validată, la care modulul standard păstrează doar semnătura ANAF), panoul spune
  acest lucru.

Ce nu face, față de varianta cu Python `l10n_ro_message_spv_side_panel` (suita OCA
`l10n_ro_message_spv`): nu creează factura din mesaj, nu are butoanele **Acceptă** / **Respinge** și
nu potrivește produsele după codul furnizorului. Cele două module nu se instalează împreună.
