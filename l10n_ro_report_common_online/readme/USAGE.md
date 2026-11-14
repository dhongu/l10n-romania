Activate the Romanian language before importing the module (Apps > Import Module, in developer
mode), so that its labels are translated. The module needs `l10n_ro`; the NRC printed in the
header is the **NRC** field of the company contact.

1. Open **Settings > Users & Companies > Companies**, open the company and fill in
   **Share Capital** under **Company ID**. It is printed without decimals.

   ![Company form, General Information tab: VAT RO18547290, Company ID 18547290 and the highlighted Share Capital field set to 200.00, above Currency RON](static/description/en/01_capital_social.png)

2. Open **Contacts > Configuration > Bank Accounts > Bank Accounts**, open the company account and tick
   **Romania - Print in Report**. Only the accounts in the currency of the document are
   printed, at most 3. In Odoo 20 a bank account has no currency of its own: its currency is
   the **Currency** of the linked bank journal, else the company currency.

   ![Bank account form RO49BTRL01301202K12345XX at Banca Transilvania, currency RON, with the highlighted Romania - Print in Report checkbox ticked](static/description/en/02_cont_bancar.png)

3. The **Romania - Print in Report** column of the bank account list shows which accounts are
   printed.

   ![Bank Accounts list with the highlighted Romania - Print in Report column: RO49BTRL01301202K12345XX is ticked, RO66BTRL01302202K12345XX is not](static/description/en/03_lista_conturi_bancare.png)

4. The module has no report of its own: the result shows on the reports that call its
   templates (`report_address_company`, `banks`, `amount_in_words`). Below, a test rendering of
   the company block and of the amount in words.

   ![Test rendering: company TEST Exemplu Distribuție SRL with address, bank account RO49BTRL01301202K12345XX, VAT, NRC J12/1234/2020, Share Capital 200, and a table of RON amounts in Romanian words such as douăsprezece mii de lei and un leu și un ban](static/description/en/04_antet_raport.png)
