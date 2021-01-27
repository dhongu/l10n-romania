# ©  2018 Terrabit
# See README.rst file on addons root folder for license details

{
    "name": "Deltatech Declaratii ANAF D100",
    "version": "12.0.1.0.0",
    "author": "Terrabit, Dorin Hongu",
    "website": "www.terrabit.ro",
    "description": """


    """,
    "category": "Generic Modules",
    "depends": ["account", "l10n_ro", "l10n_ro_declarations"],
    "data": ["views/d100_view.xml", "views/declaration_view.xml"],  # se permite generarea de decalaratii din finacinar
    "active": False,
    "installable": True,
    "application": False,
}
