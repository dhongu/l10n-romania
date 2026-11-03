# © 2026 Terrabit
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


def post_init_hook(env):
    """Completează taxele de serviciu la companiile cu planul de conturi RO deja încărcat.

    Valorile existente (de ex. preluate din OCA l10n_ro_config, aceeași coloană) nu se ating.
    """
    companies = env["res.company"].search([("chart_template", "=", "ro")])
    for company in companies:
        ref = env["account.chart.template"].with_company(company).ref
        vals = {}
        if not company.l10n_ro_account_serv_sale_tax_id:
            tax = ref("tvac_21_s", raise_if_not_found=False)
            if tax:
                vals["l10n_ro_account_serv_sale_tax_id"] = tax.id
        if not company.l10n_ro_account_serv_purchase_tax_id:
            tax = ref("tvad_21_s", raise_if_not_found=False)
            if tax:
                vals["l10n_ro_account_serv_purchase_tax_id"] = tax.id
        if vals:
            company.write(vals)
