## 20.0.1.0.0

- Portare pe 20.0: mișcarea de stoc își ține unitatea de măsură în `uom_id` (era
  `product_uom`), `t-esc` devine `t-out`, `report_file` dispare din acțiunile de raport, iar
  delegatul acceptă și contactele unei firme (în 20.0 contactele unei firme cu CUI au
  `is_company` bifat).

## 19.0.1.0.0

- Prima versiune: varianta fără Python a modulului `l10n_ro_picking_report`, importabilă pe Odoo
  Online. Calculul liniilor și al totalurilor din rapoarte (prețuri în unitatea documentului, TVA,
  preț de vânzare, adaos) este scris în QWeb și dă aceleași valori ca modelele Python ale modulului
  clasic (verificat linie cu linie). Câmpurile sunt manuale (`x_l10n_ro_*`), setările sunt pe firmă,
  iar delegatul, prețul de vânzare la recepție și referința furnizorului sunt automatizări.
- Corecturi față de modulul clasic: rapoartele de recepție tipăresc doar recepțiile; gestionarul și
  capitalul social se tipăresc doar când sunt completate; starea *Ciornă* se vede pe documente;
  totalul bonului de consum e aliniat la dreapta; traducerile „Recepție fără TVA”, „Semnătura”,
  „Din locația”, „Document sursă”, „recepționarea mărfurilor”.
