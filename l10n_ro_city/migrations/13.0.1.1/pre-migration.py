# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
                UPDATE ir_model_data
                SET module = '__import__'
                WHERE model = 'res.city' and module = 'base'
                """,
    )
