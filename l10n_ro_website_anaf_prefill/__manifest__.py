# ©  2026 Terrabit
# See README.rst file on addons root folder for license details

{
    "name": "Romania - Website ANAF Prefill",
    "summary": "Fills in the company name and address from ANAF while the customer types the tax code",
    "version": "19.0.1.0.0",
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",
    "license": "AGPL-3",
    "category": "Website/Website",
    "countries": ["ro"],
    "depends": ["website_sale", "l10n_ro_partner_create_by_vat"],
    "data": ["views/templates.xml"],
    "assets": {
        "web.assets_frontend": [
            "l10n_ro_website_anaf_prefill/static/src/interactions/anaf_lookup.esm.js",
        ],
        "web.assets_tests": [
            "l10n_ro_website_anaf_prefill/static/tests/tours/anaf_prefill_tour.esm.js",
        ],
    },
    "images": ["static/description/main_screenshot.png"],
    "development_status": "Beta",
    "maintainers": ["dhongu"],
    "installable": True,
}
