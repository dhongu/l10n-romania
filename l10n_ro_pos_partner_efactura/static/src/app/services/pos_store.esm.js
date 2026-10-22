import {PosStore} from "@point_of_sale/app/services/pos_store";
import {patch} from "@web/core/utils/patch";

patch(PosStore.prototype, {
    editPartnerContext() {
        // The partner form opened from POS requires the data e-Factura needs
        const ctx = {...super.editPartnerContext(...arguments), pos_efactura_check: true};
        // A default only applies to a new partner
        if (this.company.country_id) {
            ctx.default_country_id = this.company.country_id.id;
        }
        return ctx;
    },
});
