


Features:
- Types can be defined for records sale.order, purchase.order, account.move
- If a model has no types defined, the type field will not be displayed
- completare automata cu 13 de zero pt persane fizice
- retransmiterea unei facturi
- parametri sistem:
  - "efactura.embed_pdf" - daca pune sau nu embedded pdf. Default pe True
  - "efactura.clean_name" - daca curata caracterul "/" din numele facturii in tag-ul de ID. Default pe False
  - "efactura.get_all_banks" - daca pune toate bancile cu l10n_ro_print_report si in valuta facturii. Default pe False
