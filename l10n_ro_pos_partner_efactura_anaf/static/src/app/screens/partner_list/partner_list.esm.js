import {PartnerList} from "@point_of_sale/app/screens/partner_list/partner_list";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(PartnerList.prototype, {
    async clickPartner(partner) {
        // Also a customer fetched earlier whose form was closed without saving:
        // it is loaded in POS by then and is picked from the list, not from ANAF
        if (partner?.l10n_ro_pos_anaf_to_confirm) {
            this.notification.add(_t("Check the customer data fetched from ANAF before saving."), {type: "warning"});
            // The form resolves only on save: closing it leaves the customer off the order
            const saved = await this.pos.editPartner(partner);
            await this.pos.data.call("res.partner", "l10n_ro_pos_anaf_confirm", [[saved.id]]);
            const [confirmed] = await this.pos.data.read("res.partner", [saved.id]);
            return super.clickPartner(confirmed);
        }
        return super.clickPartner(partner);
    },
});
