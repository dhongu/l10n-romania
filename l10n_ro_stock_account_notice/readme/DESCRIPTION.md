Adds the "Romania - Is a notice" option on the stock operation types. Transfers
created for an operation type that has it set are marked as notice (aviz)
by default, so receptions and deliveries use the 408/418 accounts without the
user having to tick the box on each transfer.

The notice logic itself (field `l10n_ro_notice` on transfers, valuation types and
accounting entries) is part of `l10n_ro_stock_account_base`.
