The postal codes are loaded on install; there is nothing to configure.

1. **Browse the postal codes.** As an administrator, go to **Contacts → Configuration → Localization → Zip Codes**. The
   list shows one row per street in the big cities, with the street type, the street name, the
   postal code, the city, the state (county) and the country. The search bar looks up a postal
   code: type its first digits and press Enter.

   ![Postal Codes list filtered on the code 70011: 38 streets of Iași with the columns Street Type, Street Name, Postal Code, City Iași (IS), State Iași (RO) and Country Romania; the search bar is highlighted](readme/screenshots/en/01_lista_coduri_postale.png)

2. **Open a postal code.** A row shows everything the post office lists for it. In Bucharest the
   city is the sector, and the **Sector** field holds its number; **Office** and **Address** are the
   post office that serves the street.

   ![Postal code 011376: Piata 1 Mai, city Sector1 (București) (B), state București (RO), country Romania, sector 1, post office Bucuresti 2 at Bd. 1 Mai, nr. 75](readme/screenshots/en/02_fisa_cod_postal.png)

3. **Find the street on a partner.** On the partner form, pick the city from the list first (1);
   the state follows. Then type the street name in the postal code field right below the city (2),
   the one with the dropdown arrow; do not type in the grey *ZIP* field next to the state, which
   is filled in for you. Only the streets of the partner's city are offered, each with
   its postal code, city and county in grey. The word order does not matter (*Nicolae Balcescu*
   finds *Balcescu Nicolae*), and you can also type the code or the street type (*Strada
   Mircea*). The post office data has no diacritics, so typing without them is safer. Left empty,
   the dropdown lists the first codes of the city, and *Search more...* the rest.

   ![Partner Exemplu Distribuție SRL in Iași: Nicolae Balcescu typed in the postal code field below the city, and the dropdown offers Strada Balcescu Nicolae and Fundac Balcescu Nicolae, both 700117 · Iasi, IS; the city and the search field are highlighted](readme/screenshots/en/03_partener_cautare_strada.png)

4. **Pick the street and save.** The partner gets the postal code (3), the city (1), the state (2)
   and the country of the chosen row; the street and number of the address stay as you typed them.
   Invoices, delivery slips and e-Factura take the postal code from the partner's address. If you
   change the city afterwards, or a module update changes the street's code, pick the street again.

   ![The partner after picking the street: city Iași (IS), state Iași (RO), ZIP 700117 and the postal code field with Strada Balcescu Nicolae (700117), highlighted 1 to 4; country Romania; the form has unsaved changes](readme/screenshots/en/04_partener_cod_completat.png)
