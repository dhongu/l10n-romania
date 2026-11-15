### Configurare

1. Importați, în ordine, `l10n_ro_report_common_online`, `l10n_ro_invoice_report_online` și acest
   modul din **Aplicații → Importați Modulul** (mod dezvoltator), după instalarea limbii române.
2. În **Setări → Utilizatori & Companii → Companii**, pe firmă, fila **Factură România**, grupul
   **Documente de stoc**: bifați, după caz, **Ascunde TVA pe NIR** și **Ascunde băncile pe documentele
   de stoc**.

   ![Fila Factură România a firmei, cu grupul Documente de stoc și cele două bife evidențiate](static/description/01_setari_firma.png)

3. În **Inventar → Configurare → Locații**, pe fiecare gestiune: **Listă de prețuri a magazinului**,
   **Gestionar** și, la magazine, **Este locație de tip magazin**.

   ![Locația TEST Magazin, cu lista de prețuri, gestionarul și bifa de magazin evidențiate](static/description/02_locatie_gestionar.png)

4. Pe comanda de achiziție, completați **Referința furnizorului** înainte de confirmare: devine
   documentul sursă al recepției și numărul „conform documentului" de pe NIR.

### Utilizare

1. Pe transfer, fila **Informații suplimentare**: alegeți **Delegat** (mijlocul de transport vine din
   fișa lui), verificați **Mijloc transport** și, pe livrările facturate ulterior, bifați **Aviz de
   însoțire**. Validați transferul.

   ![Livrarea cu Delegat, Mijloc transport și Aviz de însoțire evidențiate](static/description/03_livrare_delegat_aviz.png)

2. Din roata dințată → **Tipăriți**, alegeți documentul: **Recepție (NIR)**, **Recepție fără TVA**,
   **Recepție cu preț de vânzare**, **Aviz**, **Aviz cu preț**, **Bon de Consum** sau **Notă de
   Transfer**.

   ![Meniul Tipăriți cu cele șapte rapoarte ale modulului](static/description/04_meniu_tiparire.png)

3. **NIR-ul** are prețul din comanda de achiziție sau, fără comandă, din valoarea mișcării, în
   unitatea de pe document (o cutie de 13 kg rămâne cutie).

   ![NIR pe recepția din comanda de achiziție](static/description/05_nir.png)

   ![NIR pe recepția fără comandă, în cutii de 13 kg](static/description/06_nir_cutii.png)

4. **NIR-ul cu preț de vânzare** folosește prețul fixat la validarea recepției, din lista de prețuri a
   magazinului sau din prețul produsului; coloana *Valoare vânzare* este cu TVA.

   ![NIR cu preț de vânzare, marjă și totaluri la preț de vânzare](static/description/07_nir_pret_vanzare.png)

5. Livrarea bifată **Aviz de însoțire** se tipărește ca **Aviz de însoțire a mărfii**, cu delegatul și
   mijlocul de transport; prețul vine din comanda de vânzare sau, fără comandă, din lista de prețuri a
   clientului.

   ![Avizul de însoțire a mărfii, cu prețuri, delegat și mijloc de transport](static/description/08_aviz_insotire.png)

   ![Livrarea fără comandă, cu prețuri din lista clientului](static/description/09_livrare_fara_comanda.png)

6. **Bonul de consum** arată valoarea de cost a mișcării; **nota de transfer** către un magazin arată și
   prețurile de vânzare. Între două locații interne, Odoo nu valorizează mișcarea și valoarea iese 0,00.

   ![Bonul de consum către o locație de consum](static/description/10_bon_consum.png)

   ![Nota de transfer către locația de tip magazin](static/description/11_transfer_intern.png)
