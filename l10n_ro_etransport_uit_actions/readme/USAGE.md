On a transfer whose eTransport notification is **Validated**, the header shows three extra buttons:
**Delete UIT**, **Confirm UIT** and **Change Vehicle**. Each opens the same dialog with the action
preselected; fill in the specific fields (confirmation type, or the new plates and date), optionally a
remark and the post-outage flag, then **Send to ANAF**.

The event appears in the *UIT Events* table on the eTransport tab in state *Sent*. Its final state
comes from ANAF: wait for the scheduled check or press **Fetch Event Status**. While an event is
pending no other event can be sent for the same UIT.

Once a deletion is validated, the transfer shows a red *UIT deleted* banner and no further actions are
offered; a new notification has to be sent for the transport.
