On a new database, the module is installed automatically with `l10n_ro_zip`; where `l10n_ro_zip` was already
installed, install it from **Apps**. It has nothing to configure. It adds the streets
of 269 small towns to the postal codes; you use them exactly as the other postal codes of `l10n_ro_zip`.

1. **See the streets of a small town.** As an administrator, go to **Contacts → Configuration → Localization →
   Zip Codes** and search the town's postal code (for Huși, type `735100` and press Enter). The first row, with no
   street, is the town row of the post office; the other rows are the streets added by the module, all with the
   same postal code. A town whose code returns a single row is not covered.

   ![Postal Codes list filtered on the code 735100: 163 rows, the first one without a street, then the streets of Huși (Alee Dobrina, Bulevard 1 Mai, Strada 1 Decembrie 1918 and others), all with the code 735100, city Huși (VS), state Vaslui (RO) and country Romania; the search bar is highlighted](static/description/en/01_lista_strazi_oras_mic.png)

2. **Find the street on a partner.** On the partner form, pick the city from the list first (1); the state
   and the town's postal code follow. Then type the street name in the postal code field right below the city (2), the one with the
   dropdown arrow. The streets of the partner's city are offered, each with the town's postal code. The street
   names have no diacritics, so typing without them is safer. If a street is missing, pick the town row: the
   postal code is the same.

   ![Partner Exemplu Distribuție SRL with the city Huși (VS), the state Vaslui (RO) and the ZIP 735100 already filled in: Stefan cel Mare typed in the postal code field below the city, and the dropdown offers Strada Stefan cel Mare with 735100 · Husi, VS; the city and the search field are highlighted](static/description/en/02_partener_cautare_strada.png)

3. **Pick the street and save.** The ZIP field keeps the town's postal code (3), with the city (1), the state (2)
   and the country, and the chosen street fills the postal code field (4); the street and number of the address
   stay as you typed them. The screenshot shows the form before saving.

   ![The partner after picking the street: city Huși (VS), state Vaslui (RO), ZIP 735100 and the postal code field with Strada Stefan cel Mare (735100), highlighted 1 to 4; country Romania; the form has unsaved changes](static/description/en/03_partener_cod_completat.png)
