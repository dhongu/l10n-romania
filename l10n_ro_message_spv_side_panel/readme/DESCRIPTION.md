Split view for the SPV messages: the invoices received through SPV on the left, as cards, and the
details of the selected one on the right, without leaving the list.

- **Cards and list** — the menu *Messages SPV* opens a kanban of cards (supplier, amount, number,
  date, status, days to the due date; a message whose archive is not downloaded yet shows its id,
  type and date) and the usual list. A click selects the
  message and shows it in the panel.
- **The panel** — the supplier, the VAT number read from the XML, the dates, the amounts, the review
  state and the buttons *Create Invoice*, *Accept*, *Reject*, *XML*, *PDF* and *ZIP*.
- **The document** — a tab *Document* with the invoice as written in the XML (supplier, customer,
  lines and totals) and a tab *XML Lines* with the lines only: code, description, unit, quantity,
  price, VAT rate and amount. The full form of the message has the same two tabs. Nothing is stored: the XML is read
  from the ZIP when the message is opened.
- **Installed on request** — it is a bridge between *l10n_ro_message_spv* and *deltatech_web_side_panel*.
  The menu of the SPV messages opens the split view; uninstalling the module puts it back.
