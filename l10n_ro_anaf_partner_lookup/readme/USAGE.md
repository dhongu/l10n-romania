Before you start: the module needs no setup, but you can adjust the lookup services and their
waiting times, see *Configuration*.

The module has no menu, screen or button of its own. It is a shared service: the operator types a
Romanian tax code (CUI) or an EU VAT number in a module that uses it (automatic partner completion,
the Point of Sale customer search, the website cart). The module checks the code, asks ANAF or VIES,
and the calling module fills in the partner with the values received.

**Step 1 — Lookup parameters (optional, administrator)**

Activate developer mode and go to **Settings → Technical → Parameters → System Parameters**, then
search for `l10n_ro_anaf_partner_lookup`. By default the list is empty and the module uses the
default ANAF service and a 10-second wait. Add the keys with **New** only if you need to change a
service address or a waiting time, for ANAF or for VIES. Keep the waiting time short and a positive
whole number: somebody usually waits for the answer at the till or on the website.

![System parameters of the ANAF and VIES lookup: url, timeout, vies_url and vies_timeout](https://apps.odoocdn.com/apps/assets/19.0/l10n_ro_anaf_partner_lookup/01_parametri_sistem.png)

**Step 2 — VAT-registered company: partner created from ANAF data**

In the module that uses the service, the operator types the CUI in any form (`RO 12345674`,
`ro12345674`, `12345674`). If the control digit does not match, ANAF is not asked at all. Otherwise
the partner receives the data returned. In the example the company has its registered office in
Timișoara and its fiscal domicile in Arad: the whole address comes from the **registered office**.

- The partner is a **Company**.
- **Tax ID** carries the `RO` prefix only because the company is VAT-registered.
- The street comes with its number (details such as the floor go on the second line).
- The locality has no `Mun.` prefix and uses the correct diacritics (`ș`, `ț` with comma).
- The county, the **NRC** (trade register number) and the 6-digit postal code of the registered
  office are filled in.

![VAT-registered company filled in from ANAF, with the address of the registered office](https://apps.odoocdn.com/apps/assets/19.0/l10n_ro_anaf_partner_lookup/02_firma_platitoare_tva.png)

**Step 3 — Non-VAT-registered company from Bucharest**

For a company that is not VAT-registered, **Tax ID** receives the CUI without `RO`; the partner is
still a **Company**. In the example ANAF wrote the address in capitals, the locality as
`Mun. București` without a sector and the postal code as `30167`.

- The street is shown in the usual form, not in capitals.
- The locality becomes **Sector 3**, deduced from the postal code (`03…` means Sector 3), as
  e-Factura requires.
- The postal code has 6 digits (`030167`).

If neither the locality nor the postal code shows the sector, the locality stays exactly as ANAF
wrote it, so that the e-Factura check can flag the missing sector.

![Non-VAT-registered company from Bucharest, with the sector deduced from the postal code](https://apps.odoocdn.com/apps/assets/19.0/l10n_ro_anaf_partner_lookup/03_firma_bucuresti_sector.png)

**Step 4 — Company ID: the CUI without `RO`**

Open the **Sales & Purchases** tab of the VAT-registered company from step 2. In the **Misc** group
you find **Company ID**. The module does not send it: the Romanian localization (`l10n_ro`)
computes it from **Tax ID** when the partner is saved. Here **Tax ID** is `RO12345674` and
**Company ID** is `12345674`. For a non-VAT-registered company, Company ID equals Tax ID. Without
`l10n_ro` installed, Company ID stays empty.

![Company ID computed from the Tax ID, in the Sales & Purchases tab](https://apps.odoocdn.com/apps/assets/19.0/l10n_ro_anaf_partner_lookup/04_id_companie.png)

**Step 5 — Company from another EU country: partner created from VIES**

The calling module sends the VAT number with the country prefix (`IT00743110157`,
`it 007-43110157`; `EL` for Greece). The country's control digits are checked before VIES is asked.
In the example VIES gives the address on two lines, `LARGO FRANCESCO RICHINI 6` and
`20122 MILANO MI`: the line with the postal code gives the city.

- The partner is a **Company**; **Tax ID** keeps the country prefix.
- The **country** is set from the prefix (Italy here).
- The street, the postal code (`20122`) and the city (`Milano Mi`, with the province code as VIES
  writes it) each go in their own field, capitalized only at the start of each word.
- County and phone stay empty, and NRC does not appear (it is for Romanian companies only): VIES
  does not provide them.

For Germany and Spain, VIES only confirms that the number is valid: the partner then receives only
the Tax ID, the country and the **Company** type. If the address has no recognizable postal code, it
stays whole in **Street**.

![Company from Italy filled in from VIES, with the address split into street, postal code and city](https://apps.odoocdn.com/apps/assets/19.0/l10n_ro_anaf_partner_lookup/05_firma_ue_vies.png)

**Service answers**

The calling module receives one of four answers from ANAF, or the same four from VIES, and decides
what to show the operator:

| Answer | When | What the calling module usually does |
|---|---|---|
| Found | ANAF (or VIES) knows the code | fills in the partner; warns if the company is inactive or struck off |
| Not found | correct code, but the company is not in the register | tells that the company does not exist in the register |
| Invalid code | wrong control digit, a personal ID instead of a CUI, letters | asks for the code to be corrected, with no request sent |
| Unavailable | the service does not answer in time or returns an error | at the Point of Sale and on the website: says that ANAF does not respond and leaves the data to be filled in manually |

When the service is unavailable the customer is never lost: the data can always be entered by hand.
