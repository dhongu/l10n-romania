# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from lxml import etree

_logger = logging.getLogger(__name__)
_KEY = "l10n_ro_footer_anpc.footer_anpc_data"
_CALL = "l10n_ro_footer_anpc.footer_anpc_sal"
_OLD_IMAGES = (
    "/l10n_ro_footer_anpc/static/src/img/anpc1.svg",
    "/l10n_ro_footer_anpc/static/src/img/anpc2.svg",
)


def migrate_legacy_footer_views(env):
    """Replace only the known legacy pictograms, preserving website layouts.

    Website COW views with a modified architecture are intentionally preserved
    by the native XML loader. Move their old badges to a shared template so
    future module updates can update the managed content without resetting COW.
    """
    views = env["ir.ui.view"].with_context(active_test=False, lang=None, no_cow=True)
    for view in views.search([("key", "=", _KEY), ("website_id", "!=", False)]):
        root = etree.fromstring(view.arch_db.encode())
        if root.xpath(".//t[@t-call=$call]", call=_CALL):
            continue
        images = [root.xpath(".//img[@src=$src]", src=src) for src in _OLD_IMAGES]
        if not any(images):
            continue
        if any(len(found) != 1 for found in images):
            _logger.warning("ANPC view %s has an unknown legacy layout; preserved", view.id)
            continue
        anchors = [found[0].getparent() for found in images]
        # Do not delete custom labels, extra links or images inside either badge.
        if (
            any(a.tag != "a" or len(a) != 1 or any(t.strip() for t in a.itertext()) for a in anchors)
            or anchors[0].getparent() is not anchors[1].getparent()
        ):
            _logger.warning("ANPC view %s contains custom badge content; preserved", view.id)
            continue
        parent = anchors[0].getparent()
        call = etree.Element("t", {"t-call": _CALL})
        call.tail = anchors[0].tail
        parent.replace(anchors[0], call)
        parent.remove(anchors[1])
        classes = parent.get("class", "").split()
        if "o_footer_anpc" not in classes:
            parent.set("class", " ".join([*classes, "o_footer_anpc"]))
        view.write({"arch_db": etree.tostring(root, encoding="unicode")})
