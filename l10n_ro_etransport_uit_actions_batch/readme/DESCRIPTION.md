# eTransport UIT Actions - Batch

Brings the UIT actions of `l10n_ro_etransport_uit_actions` — **Delete**, **Confirm** and
**Change vehicle** — to transfer batches declared with `l10n_ro_edi_stock_batch`, where one
truck (one batch) carries one UIT for several transfers.

Events sent for a batch are stored on the batch, logged in its chatter and polled for their
ANAF status exactly like the ones sent for a single transfer; a validated vehicle change updates
the plates on the batch, and a validated deletion flags the batch UIT as deleted.

Installs automatically when both parent modules are present.
