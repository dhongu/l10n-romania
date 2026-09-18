## Dropshipping (factory directly to customer)

Use the existing **Send eTransport** action on the native dropship transfer.
There is no additional addon and no intermediate warehouse movement.
`stock_dropshipping` is optional: this feature applies only where the native
dropshipping workflow is already installed.

Before sending, the responsible operator must establish the declarant's legal
role and select the actual operation. The addon does not determine whether a
UIT is legally required, whether a supplier already declared the shipment, or
which transaction in a chain carries the transport.

| Selected operation | Commercial partner / value source | Typical Romanian road segment |
| --- | --- | --- |
| 30 — domestic | Sale customer / tax-exclusive sale | Supplier loading address → customer delivery address |
| 10 — AIC | Purchase supplier / tax-exclusive purchase | Border crossing → customer address in Romania |
| 20 — LIC | Sale customer / tax-exclusive sale | Supplier address in Romania → border crossing |
| 40 — import | Purchase supplier / tax-exclusive purchase | Border/customs → Romanian destination; customs legs are also supported |
| 50 — export | Sale customer / tax-exclusive sale | Romanian loading/customs → border/customs |

Values use the linked order's discounted, tax-exclusive price, native unit
conversion and currency conversion to RON on the scheduled date. Dropships use
order values even if the warehouse order-price setting is disabled.

The supplier on the purchase is not necessarily the physical loading site.
Use **Specific Start Location** for a different factory/gate or an intermodal
road start in Romania. It applies only to an address endpoint, not a border or
customs code. The final delivery address comes from the linked sale/purchase;
conflicting addresses are rejected rather than guessed.

Each goods line must have a sale and purchase link in the declaring company.
One declaration must have one supplier, one commercial customer and one delivery
address. Country/operation mismatches, missing Romanian address data, unsupported
operation codes, returns and mixed/batch dropships are blocked. Foreign-to-foreign
transactions, special fiscal territories and export intermodal road ends that
differ from the customer's address need separate handling; do not select another
operation simply to bypass a validation.

Enter the actual accompanying documents (CMR, invoice, delivery note). The
default-documents button adds the transfer number and posted customer invoices;
for AIC/import, enter the supplier's accompanying invoice/documents explicitly.
It does not prove that these documents are legally sufficient.

Validate the generated XML and business interpretation in a test environment
before promotion. Automated tests mock ANAF; they do not certify ANAF acceptance.

Reference: [ANAF eTransport user guide](https://static.anaf.ro/static/10/Anaf/AsistentaContribuabili_r/Ghid_RO_e_Transport_2025.pdf).
