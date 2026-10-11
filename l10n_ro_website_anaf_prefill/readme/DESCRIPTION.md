Fills in the company name and address from ANAF while the customer types the tax code (CUI) in
the address form of the website: checkout and customer portal.

- Under the tax code, the company found at ANAF: the name the invoice is issued to, the address
  and whether it is a VAT payer
- The empty fields (company name, trade register number, street, city, zip, county) are filled
  in at once; the
  **Fill in from ANAF** button also replaces what the customer typed, only when they ask
- A fiscally inactive company gets a warning, a struck-off company is told it cannot order, and a
  personal numeric code (CNP) typed by mistake gets its own message
- A public route with a limit per visitor (20 look-ups per 10 minutes) and a one-day cache per
  tax code: ANAF is not asked twice for the same company
- If ANAF does not answer, nothing is shown and the form works as before

Any form can use it: an input marked with `data-anaf-lookup` and a `data-anaf-fill` map of the
fields to fill in.
