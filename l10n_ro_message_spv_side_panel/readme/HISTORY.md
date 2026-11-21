## 19.0.1.3.0 (2026-11-13)

- The state of the message is a status bar next to the buttons, in the panel and in the full form.
- The panel no longer repeats what the document shows (reference, dates, currency, untaxed amount,
  tax and the title): it keeps the partner, the VAT number read from the XML, the invoice, the total
  (red when it differs from the invoice) and the review state.
- The boxes of the document follow the direction of the invoice: the other party on the left, the
  invoice in the middle and our own company on the right, in a lighter color (the supplier on an
  issued invoice, the customer on a received one).
- The sheet of paper has only a soft shadow, without a border and without the second "page" behind.

## 19.0.1.2.0 (2026-11-13)

- The tabs *Document* and *XML Lines* are gone: the document (the invoice as written in the XML,
  with its lines and totals) is shown directly under the data of the message, in the panel and in
  the full form. The lines were shown twice, in both tabs.
- The document looks like a sheet of paper (border and shadow), to show that it is the invoice as
  received, and the supplier, the customer and the data of the invoice are three boxes on a row
  (fewer on a narrow panel).
- The fields of the full form are regrouped in three groups on a row (*Supplier*, *Invoice* and
  *Amounts*), followed by the document; the technical data of the message (message id, type,
  request id, VAT number, date, details) are in the group *Message* at the bottom.

## 19.0.1.1.0 (2026-11-13)

- One entry in the menu: *Messages SPV* (and its parent *SPV*) opens the split view; the extra entry
  *Messages SPV (split view)* is gone. The uninstall hook puts the menus back on the original
  action.
- The full form of the message has the VAT ID read from the XML and the tabs *Document* and *XML
  Lines*, like the panel.
- The lines show the code of the item from the XML: the code of the seller, or the standard
  identifier (e.g. GTIN) when there is none.
- A draft (a message whose archive is not downloaded yet) is a useful card: it shows the id, the
  type and the date of the message and says that the archive has not been downloaded, instead of an
  empty card with 0.00.
- The document and the lines built from the XML use the size of the text of the form, smaller than
  before, in the panel and in the full form.

## 19.0.1.0.0 (2026-11-13)

- First release: the menu *Messages SPV (split view)* with a kanban and a list that show the
  selected message in a side panel (`deltatech_web_side_panel`). The panel reads the supplier VAT
  number, the document and the lines from the invoice XML when the message is opened.
