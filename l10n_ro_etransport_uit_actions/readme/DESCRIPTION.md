# eTransport UIT Actions

Sends to ANAF the events that follow an eTransport UIT, straight from the transfer:

- **Delete (DEL)** — invalidates the notification; the goods can no longer travel under that UIT.
- **Confirm (CON)** — confirmed / partially confirmed / refused, with an optional remark.
- **Change vehicle (MVH)** — new vehicle and trailer numbers with the modification date.

Each event is a record of its own (`l10n.ro.etransport.event`) with the XML sent, the ANAF load index
and its own state: *Sent* → *Validated* / *Error*. The notification state kept by the standard module
is never touched, so the transfer's eTransport state, the amend button and any validation guard built
on it keep working exactly as before.

ANAF answers the upload with a load index only; the event is accepted or refused later. The module
polls the status every 15 minutes (or on demand) and applies the effects on the transfer — the new
vehicle number, the *UIT deleted* flag — **only after ANAF validates the event**, never right after
the upload.

**Cancelling a transfer with a valid UIT** goes through the deletion: *Cancel* opens the DEL wizard and
the transfer is cancelled as soon as ANAF receives the deletion, so no cancelled transfer is left with a
UIT that is still valid. If ANAF later refuses that deletion, a warning activity is scheduled on the
transfer. Cancellations made from code (for example when a sale order is cancelled) are not affected.

Optional *post-outage declaration* flag (`declPostAvarie`, OUG 41/2022 art. 8 par. 1^3) on every event.
