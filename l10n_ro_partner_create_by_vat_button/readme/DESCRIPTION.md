**No longer developed: use `l10n_ro_partner_autocomplete`.** It fills a Romanian partner in
from ANAF, for free, from the CUI typed in the name or the Tax ID, and has an **Update from ANAF**
button on the partner. It does not depend on the OCA `l10n_ro_partner_create_by_vat`, which this
module needs, and cannot be installed together with it. This module only receives fixes until the
databases that use it have switched.

Adds a button on the partner form to read the partner data again from ANAF (or VIES for a
partner from another EU country), and fills a new partner in from the CUI typed in its name.
