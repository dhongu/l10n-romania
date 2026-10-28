ANAF on the address forms of the website (checkout and customer portal), for a Romanian billing
address.

**While the tax code (CUI) is typed:**

- Under the tax code, the company found at ANAF: the name the invoice is issued to, the address
  and whether it is a VAT payer
- The empty fields (company name, trade register number, street, city, zip, county) are filled
  in at once; the **Fill in from ANAF** button also replaces what the customer typed, only when
  they ask
- A fiscally inactive company gets a warning, a struck-off company is told it cannot order, and a
  personal numeric code (CNP) typed by mistake gets its own message
- A public route with a limit per visitor (20 look-ups per 10 minutes) and a one-day cache per
  tax code: ANAF is not asked twice for the same company

**When the address is sent:**

- A company not found or struck off at ANAF is refused; a CNP gets its own message
- A company found gives the partner its legal name (the invoice and e-Factura are issued to it);
  the address typed by the customer is kept, ANAF only fills the empty fields
- A fiscally inactive company can order: the cart gets an internal note for the salesperson
  (VAT code cancelled: invoice with VAT, without reverse charge, check the collection)
- ANAF not answering never stops the sale: the number is accepted as typed and the cart gets a note

Any form can use the look-up: an input marked with `data-anaf-lookup` and a `data-anaf-fill` map
of the fields to fill in (the B2B account request form of `deltatech_b2b_portal` does).
