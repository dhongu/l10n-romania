This is a technical add-on for the OCA storage sheet report (`l10n_ro_stock_report`, on the OCA
valuation engine `l10n_ro_stock_account`): when dropshipping (`stock_dropshipping`) is also
installed, dropshipped stock movements are recognized as a "Dropship" valuation type and included
in the storage sheet report lines, under the account the movement is valued on. There is no
separate menu or setting to configure; simply generate the storage sheet report as usual
(Inventory > Reporting) and dropship lines will appear alongside purchase/sale lines.
