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

