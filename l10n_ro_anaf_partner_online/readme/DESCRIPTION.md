Fill in Romanian companies from ANAF by their CUI (Tax ID), on **Odoo Online** too: the module has
no Python code and is imported as a zip (Apps > Import Module). The lookup itself runs on the
Terrabit service, which asks ANAF and sends the data back to your database.

- **ANAF button on the partner form**: next to the Tax ID, it fills in the name, the address of
  the registered office (county, city, postal code), the Tax ID with `RO` only for VAT payers and
  the phone, before you save.
- **Many partners at once**: *Action > Update from ANAF* on a selection of partners; the service
  answers in a few seconds and posts a note in the chatter of each partner.
- **ANAF status on the partner**: VAT payer, fiscally inactive, struck off, the trade register
  number (J…) and the date of the last check, on the **ANAF** tab.
- **Activation in one click**: *Contacts > Configuration > ANAF > ANAF Service*, **Activate**;
  the service token is written in your database automatically, with free trial lookups.
  **Buy Credits** and **Refresh Credits** are on the same screen (module *IAP Services for Odoo
  Online*, `deltatech_iap_online`, installed with this one).
- **Who sees what**: the users who edit partners (*Contact Creation*) can read the service
  account, because the ANAF button asks the service from their browser. Every internal user can
  create requests (the button, *Update from ANAF*), but only administrators read them and their
  answers (access rights of `deltatech_iap_online`).
- **What leaves your database**: only the CUI you look up, the request token and the address of
  your database (for the answer). The requests and their answers stay visible under *ANAF Requests*.

The service is provided by Terrabit: after the trial lookups, more can be bought from Terrabit.
