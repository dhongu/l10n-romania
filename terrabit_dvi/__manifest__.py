# ©  2008-2026 Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details
#
# MODUL TRANZITORIU — NU SE PORTEAZĂ PE 20.0.
#
# Conţinutul a fost mutat în `l10n_ro_customs_dvi`, pentru alinierea la convenţia `l10n_ro_`
# a repo-ului. Acest modul nu mai are cod şi nici date: există doar ca manifestele care îl
# declară ca dependenţă (ex. `proiecte/ptc/deltatech_ptc`) să continue să se încarce.
#
# La portarea pe 20.0: se actualizează acele manifeste direct pe `l10n_ro_customs_dvi` şi
# modulul de faţă se abandonează pe 19.0. Decizie 2026-09-23, vezi
# `l10n_ro_ent/readme/roadmap/ROADMAP_dvi.md` §1.
{
    "name": "Terrabit - DVI (moved to l10n_ro_customs_dvi)",
    "summary": "Transitional module, kept only so existing dependencies keep resolving. "
    "It installs l10n_ro_customs_dvi and will NOT be ported to 20.0.",
    "license": "AGPL-3",
    "version": "19.0.1.3.0",
    "countries": ["ro"],
    "author": "Terrabit",
    "website": "https://www.terrabit.ro",
    "category": "Localization",
    "depends": ["l10n_ro_customs_dvi"],
    "data": [],
    "installable": True,
    "auto_install": False,
    "development_status": "Production/Stable",
}
