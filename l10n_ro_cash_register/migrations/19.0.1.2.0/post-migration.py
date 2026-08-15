# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Recalculează soldurile registrelor existente.

    Până la această versiune soldurile stocate nu se actualizau când apăreau mișcări
    ulterioare creării registrului, deci registrele deja existente pot avea solduri
    învechite. Recalculul readuce fiecare registru la soldurile care rezultă din
    mișcările contabile postate.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    registers = env["l10n.ro.cash.register"].search([])
    if not registers:
        return
    registers.action_refresh()
    _logger.info("l10n_ro_cash_register: solduri recalculate pentru %s registre", len(registers))
