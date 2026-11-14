Import `l10n_ro_report_common_online` first, then this module, from **Apps > Import Module**.

**1. Invoice options, on the company.** In **Settings > Users & Companies > Companies**, open the
company and go to the **Romanian Invoice** tab. Tick what the invoice prints: the address
details (marker, e-mail, phone), the lines (index line, total with taxes, product name removed,
undiscounted price) and the footer (payment communication, pickings, delegate, Coface logo).

![Company form, Romanian Invoice tab, with the Addresses, Lines and Footer groups](static/description/en/01_companie_tab_factura.png)

On the company bank account, tick **Romania - Print in Report**: the account is printed on the
invoices in its currency (or in the company currency, when the account has none).

**2. Operating unit, on the sales journal.** In **Invoicing > Configuration > Journals**, set
**Operating Unit** on the sales journal. Its name and address are printed under the supplier;
its bank accounts, when it has any, replace those of the company.

![Sales journal with the Operating Unit field set](static/description/en/02_jurnal_unitate_operationala.png)

**3. Partner fields.** On the partner, **Sales & Purchase** tab, **Misc** group:
**Payment bank account** (the company account the customer pays into, set on its draft customer
invoices) and **Mean transport** (filled on the delegate, copied on the invoice).

![Customer form, Sales & Purchase tab, with Mean transport and Payment bank account](static/description/en/03_partener_cont_plata.png)

On the **Invoicing** tab, **Additional info for invoice** is printed at the end of the
partner's invoices.

![Customer form, Invoicing tab, with Additional info for invoice](static/description/en/04_partener_info_factura.png)

If you use the payment bank account, mark the company bank account as trusted (*Send Money*),
otherwise Odoo does not confirm the invoices on which the account was set.

**4. Delegate on the invoice.** On a draft customer invoice, choose the **Delegate** (a person,
not a company): the **Mean transport** of the delegate is copied on the invoice.

![Draft customer invoice with the delegate chosen and the means of transport filled in](static/description/en/05_factura_delegat.png)

**5. Origin from pickings.** On an invoice from a sale or purchase order, **Actions > Set origin
from pickings** writes the done deliveries (or receptions) in the **Source** of the invoice.

![Invoice Actions menu with Set origin from pickings](static/description/en/06_actiune_origine_livrari.png)

**6. Printed invoice.** **Print > Invoice PDF** prints the supplier and the customer side by side,
the operating unit, the lines with the VAT value per line, the issuer, the delegate, the means of
transport, the deliveries with their AWB, the legal mention, the additional info of the customer
and the optional Coface logo. **Invoices in company language** prints it in the language of the
company partner.

![Printed invoice with the operating unit, discounted line, delegate, deliveries and Coface logo](static/description/en/07_factura_tiparita.png)

An invoice paid on a **cash** journal carries the cash receipt below, with the amount in words,
on **Invoice PDF** only (not on **PDF without Payment**).

![Receipt box printed below an invoice paid in cash, with the amount in words](static/description/en/08_factura_chitanta.png)

**7. Voucher / Payment.** From a payment, **Actions > Print > Voucher / Payment** prints the
receipt (inbound) or the payment disposal (outbound). On a cash journal it adds the form code
(14-4-1 or 14-4-4), the cash desk and, for payments, the identity document line.

![Voucher printed from a cash payment, form 14-4-1](static/description/en/09_dispozitie_incasare.png)

**8. Due filters.** On the customer invoices, the filters **Due tomorrow**, **Due today**,
**Overdue 1-7 days**, **Overdue 8-14 days**, **Overdue 15-30 days** and
**Overdue more than 30 days** list the posted invoices not fully paid.

![Invoice list with the Overdue 1-7 days filter active](static/description/en/10_filtre_scadenta.png)
