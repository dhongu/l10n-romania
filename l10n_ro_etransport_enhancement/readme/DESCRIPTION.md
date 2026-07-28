# l10n_ro_etransport_enhancement
## Overview
The l10n_ro_etransport_enhancement module extends the standard Romanian e-Transport functionality in Odoo with additional features and improvements. This module enhances the e-Transport system integration for Romanian fiscal compliance, making it more flexible and user-friendly.
## Key Features
- Enhanced functionality for sending e-Transport documents directly from stock pickings
- Support for different sending types through context parameters
- Improved handling of stock valuation layer tracking for e-Transport documents
- Streamlined integration with the Romanian e-Transport system (SPV)
- Configurable timeout for the ANAF API (the Odoo standard hardcodes 10 seconds, often too short)
- Network failures towards ANAF no longer raise a traceback: the transfer keeps a failed
  document with a readable message warning to check SPV before resending, so no duplicate UIT is issued
- Automatic retry on status requests only (GET is idempotent); document upload is never retried automatically
- Road route between a border crossing point and a customs office: for import and export, both ends
  of the route can be a border crossing point or a customs office, so a UIT can be issued for the leg
  under customs supervision (border crossing point to inland customs office on import, customs office
  to border crossing point on export). The Odoo standard only allows the customs office at departure
  on import and at arrival on export, the other end being forced to a location.
- The transport date no longer breaks when the sending user has no timezone set (the usual case for
  automated sends running as OdooBot); it falls back to the Romanian timezone
- Lines the standard sends with a zero value no longer reach ANAF as zero: the unit price falls back
  to the stock value of the move, then to the product cost, then to the sales price. When no price can
  be found at all, sending stops with an explicit error instead of filing an invalid declaration
- Lines without a quantity are dropped from the declaration, and a missing net or gross weight is
  approximated with the other one. The QWeb template renders all three through `t-att-*`, which
  silently drops a zero, while the ANAF schema requires them: a zero invalidates the declaration
- "Get lines" recomputes the shipping weight lines instead of adding to them, so pressing it twice no
  longer doubles the weights sent to ANAF

## Technical Implementation
The module builds upon the standard Romanian localization and enhances the e-Transport integration through:
- Extended stock picking methods for e-Transport document submission
- Advanced tracking mechanisms for stock valuation layers
- Improved context handling for different document sending scenarios

## Business Benefits
- Simplified compliance with Romanian e-Transport regulations
- More flexible options for submitting transport documents to authorities
- Better tracking and management of stock movements subject to e-Transport requirements
- Reduced administrative burden for logistics and accounting departments

## Usage
After installation, the module automatically enhances the e-Transport functionality in stock operations. Users can access the enhanced e-Transport features through the stock picking interface, with additional options available in the action menu.
This module is part of the Romanian localization suite developed by Terrabit.

