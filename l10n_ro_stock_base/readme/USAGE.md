The consume and usage giving locations are created for every company whose fiscal
country is Romania, and the matching operation types for every new warehouse of such a
company. The fiscal country comes from the Invoicing app, which must be installed.
Enable **Storage Locations** in **Inventory → Configuration → Settings** to see the
locations menu and the source and destination locations on transfers.

1. Go to **Inventory → Configuration → Locations**, remove the *Internal* filter and
   look for the two locations of the company: one with the **Location Type** *Consume*,
   one with *Usage Giving*.

   ![The locations of type Consume and Usage Giving of the company, with the Location Type column highlighted](static/description/en/01_locatii_consum_dare.png)

2. Open the consume location: its **Location Type** is *Consume*. The location
   names come from the language used at installation and can be renamed; the module
   finds them by their type.

   ![The Consume location form, with Location Type Consume highlighted](static/description/en/02_locatie_consum.png)

3. Go to **Inventory → Configuration → Warehouses** and open the warehouse. With the
   developer mode on, the **Technical Information** tab shows **Romania - Consume Type**
   and **Romania - Usage Giving Type**. Warehouses that existed before the installation
   do not get them automatically: change the warehouse **Short Name**, save, then set it
   back and save again, and the missing operation types are created; then correct
   their **Barcode**, which keeps the temporary short name.

   ![The Technical Information tab of the warehouse, with the Romania - Consume Type and Romania - Usage Giving Type fields highlighted](static/description/en/03_depozit_tipuri_operatie.png)

4. The **Consume** operation type is an internal transfer from the warehouse stock to
   the company consume location, numbered with the `CONS` sequence prefix
   (`<warehouse code>/CONS/00001`). The **Usage Giving** type is the same, towards the
   usage giving location, with the `USAGE` prefix.

   ![The Consume operation type, with the Sequence Prefix CONS and the Consume destination location highlighted](static/description/en/04_tip_operatie_consum.png)

5. Create a transfer of type **Consume** from **Inventory → Overview**, add the products
   and quantities, then **Mark as Todo** and **Validate**. The quantity leaves the
   warehouse stock; a **Return** brings it back, numbered in the same `CONS` sequence
   unless a **Return Type** is set on the operation type. Moves to the consume and usage giving
   locations count as outgoing for the stock valuation, and moves from them as incoming.

   ![The done consume transfer DC/CONS/00001, from DC/Stoc to the Consume location](static/description/en/05_bon_consum.png)

6. On the product, the **Inventory** tab shows the **Net Weight** under the weight, in
   the same unit. Fill it in after the product is saved for the first time.

   ![The Inventory tab of a product, with the Net Weight field highlighted](static/description/en/06_produs_greutate_neta.png)
