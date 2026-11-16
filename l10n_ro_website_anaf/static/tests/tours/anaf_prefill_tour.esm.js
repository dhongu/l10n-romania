import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("l10n_ro_website_anaf_tour", {
    steps: () => [
        {
            content: "The customer types a delivery street of their own",
            trigger: "input[name='street']",
            run: "edit Depozit 3",
        },
        {
            content: "Type the tax code of a company",
            trigger: "input[name='vat'][data-anaf-lookup]",
            run: "edit RO1234567897",
        },
        {
            content: "The company found at ANAF is shown under the tax code",
            trigger: ".o_anaf_feedback .o_anaf_message:contains(FIRMA ANAF SRL)",
        },
        {
            content: "The empty company name was filled in",
            trigger: "input[name='company_name']:value(FIRMA ANAF SRL)",
        },
        {
            content: "The street typed by the customer was kept",
            trigger: "input[name='street']:value(Depozit 3)",
        },
        {
            content: "Replace it with the ANAF address on request",
            trigger: ".o_anaf_fill",
            run: "click",
        },
        {
            content: "The street now comes from ANAF",
            trigger: "input[name='street']:value(Str. Anaf Nr. 7)",
        },
    ],
});
