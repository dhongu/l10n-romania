  # Roadmap

## Known Bugs to Fix

- **Missing system parameter defaults**: `efactura.get_all_banks` and `efactura.replace_unit_uom`
  are used in the code but have no default entries in `data/ir_config_parameter.xml`. Add records
  with `False` as default value.

## Fixed Bugs

- ✅ **`_get_address_node` tuple bug** *(v18.0.0.2.7)*: Line 41 in `models/account_edi_xml_cius_ro.py`
  was assigning a tuple `({"_text": "Principala"},)` instead of a dict `{"_text": "Principala"}`.
  Caused `TypeError` during XML serialization for partners without a street address.

- ✅ **`_ubl_add_accounting_supplier_party_legal_entity_nodes` wrong super call** *(v18.0.0.2.7)*:
  Was calling `super()._ubl_add_accounting_supplier_party_tax_scheme_nodes(vals)` instead of
  `super()._ubl_add_accounting_supplier_party_legal_entity_nodes(vals)`. When the supplier had no
  `nrc`, the `cac:PartyLegalEntity` node was omitted from the XML, producing an invalid e-invoice.

- ✅ **Missing company filter in cron auto-send** *(v18.0.0.2.7)*: The `invoice_sending_failed`
  domain in `_cron_l10n_ro_edi_auto_send` was not filtering by `company_id`, causing invoices from
  all companies to be collected instead of only the current company in the loop.

## Planned Improvements

### Dashboard operațional eFactura (`l10n.ro.efactura.dashboard`)

Obiectiv: pagină dedicată în meniul Accounting → Rapoarte → eFactura Dashboard care oferă
o vedere rapidă a stării trimiterilor SPV cu navigare directă la liste filtrate.

Funcționalități dorite:

- **Stat buttons** pentru fiecare stare SPV:
  - *De trimis* — facturi confirmate fără `l10n_ro_edi_state` (state `False`)
  - *Trimise (în așteptare)* — `invoice_sent`, trimise dar neconfirmate încă de SPV
  - *Neindexate* — `invoice_not_indexed`, acceptate dar neindexate în portalul ANAF
  - *Validate* — `invoice_validated`, acceptate și indexate cu succes
  - *Refuzate* — `invoice_refused`, respinse de SPV
  - *Eroare trimitere* — `invoice_sending_failed` pe documentul EDI
- **Click pe orice buton** deschide lista facturilor filtrate pe acea stare
- **Selector companie** pentru multi-company
- **Acces**: grupurile `account.group_account_invoice` și `account.group_account_manager`

Probleme tehnice identificate și rezolvate (de re-activat după testare):
- View structurat cu `oe_button_box` ca prim copil al `<sheet>` (standard Odoo 19)
- Server action returnează `target: "current"` în loc de `"main"` (compatibil TransientModel)
- Atribute deprecate `create/edit/delete` eliminate din `<form>`
- Access rules adăugate în `security/ir.model.access.csv`

Codul modelului și view-ului este prezent dar **dezactivat temporar** (`efactura_dashboard.py`,
`views/efactura_dashboard_views.xml`) — de re-activat după validare pe o instanță live.

### Alte îmbunătățiri planificate

- **Re-enable wizard view**: Uncomment `wizard/account_move_send_views.xml` in the manifest once the
  resend UI flow is finalized for Odoo 18 (see TODO in `wizard/account_move_send.py`).

- **UBL integration tests**: Add test cases covering XML generation for invoices with and without
  street, with and without `nrc`, and with `efactura.get_all_banks` enabled, to prevent regressions
  in the UBL override methods.

- **Multi-company cron robustness**: Review both cron methods (`_cron_l10n_ro_edi_auto_send` and
  `_cron_l10n_ro_edi_fetch_status`) for correct company isolation throughout all domain searches.

- **English code comments**: Translate remaining Romanian inline comments in `models/account_move.py`
  to English for consistency with the project convention.

- **`efactura.replace_unit_uom` UI**: Expose the `replace_unit_uom` system parameter in the
  Accounting configuration page alongside the existing `l10n_ro_spv_cron_no_email` setting.
