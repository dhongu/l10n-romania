import {PosStore} from "@point_of_sale/app/services/pos_store";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
    editPartnerContext(partner) {
        // The partner form opened from POS requires the data e-Factura needs
        const res = super.editPartnerContext(partner);
        const ctx = {...res, pos_efactura_check: true};
        if (!partner && this.company.country_id) {
            ctx.default_country_id = this.company.country_id.id;
        }
        return ctx;
    },
});
