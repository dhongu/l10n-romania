Split view for the SPV messages: the invoices received through SPV on the left, as cards, and the
details of the selected one on the right, without leaving the list.

- **Cards and list** — a new menu *Messages SPV (split view)*, with a kanban of cards (supplier,
  amount, number, date, status, days to the due date) and the usual list. A click selects the
  message and shows it in the panel.
- **The panel** — the supplier, the VAT number read from the XML, the dates, the amounts, the review
  state and the buttons *Create Invoice*, *Accept*, *Reject*, *XML*, *PDF* and *ZIP*.
- **The document** — a tab *Document* with the invoice as written in the XML (supplier, customer,
  lines and totals) and a tab *XML Lines* with the lines only. Nothing is stored: the XML is read
  from the ZIP when the message is opened.
- **Installed on request** — it is a bridge between *l10n_ro_message_spv* and *deltatech_web_side_panel*.
  The original menu and views stay as they are.
