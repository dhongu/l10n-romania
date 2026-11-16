import {PartnerList} from "@point_of_sale/app/screens/partner_list/partner_list";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(PartnerList.prototype, {
    /**
     * The CUI behind the search, or false when the cashier is not looking for one.
     * With or without RO: the customer reading it off a document does not know
     * which of the two the shop keeps.
     */
    get l10nRoCuiQuery() {
        const query = (this.state.query || "").replace(/[\s.-]/g, "").toUpperCase();
        const cui = query.startsWith("RO") ? query.slice(2) : query;
        return /^\d{2,10}$/.test(cui) ? cui : false;
    },

    get l10nRoAnafButtonLabel() {
        return _t("Search ANAF (CUI: %s)", this.l10nRoCuiQuery);
    },

    async l10nRoSearchAnaf() {
        const cui = this.l10nRoCuiQuery;
        if (!cui) {
            return;
        }
        this.state.loading = true;
        let result = false;
        try {
            result = await this.pos.data.callRelated("res.partner", "l10n_ro_pos_partner_from_cui", [
                this.pos.config.id,
                cui,
            ]);
        } catch (error) {
            this.notification.add(error.data?.message || error.message || _t("Error fetching data from ANAF"), {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
        const partner = result && result["res.partner"]?.[0];
        if (partner) {
            await this.clickPartner(partner);
        }
    },

    async clickPartner(partner) {
        // Also a customer fetched earlier whose form was closed without saving:
        // it is loaded in POS by then and is picked from the list
        if (partner?.l10n_ro_pos_anaf_to_confirm) {
            this.notification.add(_t("Check the customer data fetched from ANAF before saving."), {
                type: "warning",
            });
            // The form resolves only on save: closing it leaves the customer off the order
            const saved = await this.pos.editPartner(partner);
            await this.pos.data.call("res.partner", "l10n_ro_pos_anaf_confirm", [[saved.id]]);
            const [confirmed] = await this.pos.data.read("res.partner", [saved.id]);
            return super.clickPartner(confirmed);
        }
        return super.clickPartner(partner);
    },
});
