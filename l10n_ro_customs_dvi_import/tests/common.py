# Copyright (C) 2026 Terrabit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""Positioned lines of real SNI declarations, extracted with pdfminer and anonymized.

Names, addresses, tax identifiers, MRN / LRN and document references were replaced; the layout,
the labels and the amounts are the ones of the original documents.
"""

import json

from odoo.tools.misc import file_path

from ..tools.sni_dvi import TextLine

# anonymized VAT code of the importer, the same in every fixture
IMPORTER_VAT = "RO12345674"


def load_lines(name):
    with open(file_path(f"l10n_ro_customs_dvi_import/tests/data/{name}.json"), encoding="utf-8") as fixture:
        return [TextLine(*row) for row in json.load(fixture)]
