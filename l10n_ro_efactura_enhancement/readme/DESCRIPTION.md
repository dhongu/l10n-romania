## Overview
The l10n_ro_efactura_enhancement module extends the standard Romanian e-Invoicing (e-Factura) functionality in Odoo with additional features and improvements designed to enhance user experience and accommodate specific business needs for Romanian fiscal compliance.

## Key Features
- **Automatic completion with 13 zeros** for individual persons (physical persons) in the VAT field for e-invoice generation.
- **Enhanced Address Validation**: Automatically checks that Romanian partners have a country, state, city, and street defined before posting an invoice.
- **EDI Format Suggestion**: Automatically suggests the `ciusro` format for Romanian partners.
- **Automated e-Invoice Operations**:
    - Cron job for **automatic sending** of posted invoices to SPV.
    - Cron job for **fetching status** updates from SPV for sent invoices.
- **Data Truncation and Sanitization**:
    - Truncates product names to 100 characters and descriptions to 200 characters to ensure compliance with UBL standards.
    - Truncates notes to 300 characters.
    - Truncates order references and despatch advice to 200 characters.
- **POS Integration**: Automatically changes the document type code to 751 (Specialised Invoice) for invoices originating from Point of Sale.
- **Configurable System Parameters**:
    - `efactura.embed_pdf`: Controls whether to include the embedded PDF in the e-invoice (Default: True).
    - `efactura.use_line_description`: If enabled, uses the invoice line description instead of the product name/description in the e-invoice (Default: False).
    - `efactura.replace_unit_uom`: Allows specifying a replacement unit code for the standard 'C62' unit (Default: False).
    - `efactura.get_all_banks`: If enabled, includes all banks marked with `l10n_ro_print_report` that match the invoice currency (Default: False).
- **Line Length Tracking**: Adds computed fields on invoice lines to track the length of descriptions and product names, helping users identify potential truncation issues.

## Technical Implementation
The module inherits and extends several base Odoo and Romanian localization models:
- `account.move`: Adds validation, cron jobs, and POS type handling.
- `account.edi.xml.ubl_ro`: Enhances UBL generation with custom logic for addresses, product descriptions, and multi-bank support.
- `res.partner`: Overrides the EDI format suggestion for Romanian entities.
- `account.move.line`: Adds UI helpers for label length.

## Business Benefits
- **Improved Compliance**: Prevents errors by validating mandatory address fields for Romanian fiscal reporting.
- **Automation**: Reduces manual effort by automatically transmitting and tracking e-invoices.
- **Flexibility**: Provides granular control over how product information and unit codes are mapped to the e-invoice.
- **UBL Stability**: Ensures generated XML files remain within character limit constraints for various fields.

## Usage
After installation, the module automatically enhances the e-Factura functionality. System parameters can be configured in the technical settings (`Settings > Technical > Parameters > System Parameters`) to adjust behavior according to specific business needs.
This module is part of the Romanian localization suite developed by Terrabit.
