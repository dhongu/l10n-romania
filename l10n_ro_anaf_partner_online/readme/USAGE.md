**Activate the service** (administrator, once)

1. Go to *Contacts > Configuration*: the **ANAF** group holds **ANAF Service** and **ANAF
   Requests** (administrators only).

   ![The Configuration menu of Contacts, open, with ANAF Service and ANAF Requests highlighted in the ANAF group](static/description/en/01_meniu_anaf.png)

2. Open **ANAF Service** and click **Activate**. The account token comes back by itself in a few
   seconds, with free trial lookups. Once active, the header shows **Activate Again**, **Refresh
   Credits** and **Buy Credits**, and **Credits Left** shows the lookups left on the Terrabit
   account (updated by **Refresh Credits** and by every queued answer). One credit is used per
   ANAF answer (company found or not found); an invalid CUI or ANAF not answering is free.

   ![The ANAF Service form, active: Activate Again, Refresh Credits and Buy Credits in the header, Service Code anaf_partner_online and Credits Left highlighted](static/description/en/02_serviciu_anaf.png)

**Fill in a new partner**

3. Create a contact, choose **Company** and type the CUI in **VAT** (with or without `RO`). Press
   Tab so that the suggestion list of the field closes, then click **ANAF** next to it. The button is
   hidden on the contacts of a company.

   ![A new company contact with 14399840 in VAT and the ANAF button highlighted next to it](static/description/en/03_buton_anaf.png)

4. The form is filled in at once, before you save: name, **VAT** with `RO` only for VAT payers, the
   address of the registered office (in Bucharest, the city is the sector) and the phone, if ANAF has
   it. A notification shows the lookups left. Check the data, then save. If the browser cannot reach
   the service, the partner is saved and the lookup is queued instead.

   ![The form filled in from ANAF before saving: DANTE INTERNATIONAL SA, VAT RO14399840, the address in Sector 6, Bucharest, and the notification Filled in from ANAF with the lookups left](static/description/en/04_partener_completat.png)

5. After saving, the **ANAF** tab shows **VAT Payer (ANAF)**, **Fiscally Inactive (ANAF)**,
   **Struck Off (ANAF)**, **Trade Register No.** and **Last ANAF Check**. The tab appears once the
   partner has been checked at ANAF.

   ![The ANAF tab of the partner: VAT Payer ticked, Fiscally Inactive and Struck Off not ticked, the trade register number and the date of the last check](static/description/en/05_tab_anaf.png)

**Update many partners**

6. In the list of contacts, select the partners and click *Actions > Update from ANAF* (also in the
   *Actions* menu of the partner form). Partners without a VAT number are skipped.

   ![The list of contacts with three partners selected and Update from ANAF highlighted in the Actions menu](static/description/en/06_actiune_actualizare.png)

7. A notification tells how many requests were sent; the partners are updated in a few seconds.

   ![The notification ANAF (Terrabit): 2 request(s) sent, over the list with three partners selected](static/description/en/07_cereri_trimise.png)

8. Each partner found gets the ANAF data and the note *Partner data updated from ANAF (Terrabit
   service).* in the chatter, with the tracked changes. The answer is written only if the user who
   sent the request may edit the partner and the partner still has the same CUI.

   ![The partner OMV PETROM SA updated from ANAF, with the tracked changes of name, VAT and address and the note in the chatter](static/description/en/08_nota_chatter.png)

**Follow the requests** (administrator)

9. *Contacts > Configuration > ANAF > ANAF Requests* lists every request with its **Request Type**,
   **Name** (the CUI looked up), **Status** and **Error**; the requests in error are red (for
   example `Invalid CUI`). A request still without answer after 10 minutes is sent once more.

   ![The ANAF Requests list: a request Done and a red request in Error with Invalid CUI](static/description/en/09_cereri_anaf.png)
