Adds the "Romania - Is a notice" option on the stock operation types. Transfers
created for an operation type that has it set are marked as notice (aviz)
by default, so that, with `l10n_ro_stock_account` installed, receptions and deliveries use the
408/418 accounts without the user having to tick the box on each transfer.

The field `l10n_ro_notice` is kept by `l10n_ro_stock_account_base`; the notice valuation and the
408/418 entries are done by `l10n_ro_stock_account`.
