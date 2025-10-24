## Overview
The l10n_ro_efactura_enhancement module extends the standard Romanian e-Invoicing (e-Factura) functionality in Odoo with additional features and improvements designed to enhance user experience and accommodate specific business needs for Romanian fiscal compliance.
## Key Features
- Automatic completion with 13 zeros for individual persons (physical persons) in the VAT field
- Ability to retransmit an invoice to the e-Factura system
- Configurable system parameters:
    - - Controls whether to include embedded PDF in the e-invoice (Default: True) `efactura.embed_pdf`
    - - Controls whether to clean the "/" character from invoice names in the ID tag (Default: False) `efactura.clean_name`
    - - Controls whether to include all banks with l10n_ro_print_report and in the invoice currency (Default: False) `efactura.get_all_banks`

## Technical Implementation
The module builds upon the standard Romanian localization and enhances the e-Factura integration with additional configuration options and data handling improvements.
## Business Benefits
- Improved compliance with Romanian fiscal requirements
- Enhanced flexibility in e-invoice generation and transmission
- Better handling of special cases like individual customers without VAT numbers
- Support for retransmission of invoices when needed

## Usage
After installation, the module automatically enhances the e-Factura functionality. System parameters can be configured in the technical settings to adjust behavior according to specific business needs.
This module is part of the Romanian localization suite developed by Terrabit.



Features:
- Types can be defined for records sale.order, purchase.order, account.move
- If a model has no types defined, the type field will not be displayed
- completare automata cu 13 de zero pt persane fizice
- retransmiterea unei facturi
- parametri sistem:
  - "efactura.embed_pdf" - daca pune sau nu embedded pdf. Default pe True
  - "efactura.clean_name" - daca curata caracterul "/" din numele facturii in tag-ul de ID. Default pe False
  - "efactura.get_all_banks" - daca pune toate bancile cu l10n_ro_print_report si in valuta facturii. Default pe False
