**Înainte**: compania are CIF și este conectată la SPV (*Facturare > Configurare > Setări*, blocul
**E-Factura România**), iar modulul `l10n_ro_message_spv_online` este instalat.

1. Deschideți *Facturare > Mesaje SPV (vedere împărțită)*. Mesajele apar ca carduri (partener, total,
   număr, stare, direcția *Primit* / *Trimis*); comutați pe listă din colțul din dreapta sus.

2. Faceți clic pe un card sau pe un rând: în dreapta se deschide panoul cu datele mesajului și, sub
   ele, factura desenată din XML: furnizorul (sau clientul), factura și firma noastră, liniile și
   totalurile. Săgețile din colțul panoului trec la mesajul anterior / următor; dublu clic deschide
   formularul complet.

   ![Panoul lateral cu factura TID 4521 desenată din XML: caseta furnizorului cu CUI, caseta facturii, firma noastră, liniile și totalurile](static/description/en/01_vedere_impartita.png)

3. Pentru o factură trimisă și încă în așteptare, butonul **Preia starea** din panou întreabă ANAF.
   Descărcarea XML, semnătura și PDF-ul rămân în câmpul de fișiere al formularului complet.

Panoul nu are **Acceptă**, **Respinge** sau **Creează factura**: pentru ele folosiți modulul cu Python
`l10n_ro_message_spv_side_panel`, pe o instalare care îl poate rula.
