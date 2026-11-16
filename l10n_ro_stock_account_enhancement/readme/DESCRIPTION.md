Modulul adaugă controale suplimentare peste evaluarea stocului din localizarea românească
(`l10n_ro_stock_account`), ca valorile ajunse în contabilitate să nu fie zero sau fără sursă.

## Funcții principale

- **Preț de cost nenul pe mișcările de stoc**: calculul prețului unitar al unor mișcări reale de
  stoc (`stock.move._get_price_unit`) se oprește cu o eroare când iese zero — de exemplu, la
  validarea livrării unei mărfi fără cost cu modulul de marjă `sale_stock_margin` instalat, la
  închiderea sesiunii de punct de vânzare sau în raportul comenzii de producție. Fără
  `sale_stock_margin`, livrarea se validează. Prețul folosit la costul vânzării (COGS) de pe
  factură nu este verificat.
- **Facturi cu produse stocabile doar din comenzi**: la validarea unei facturi de vânzare sau de
  achiziție (inclusiv storno), fiecare linie cu produs stocabil trebuie să provină dintr-o linie
  de comandă de vânzare (SO), respectiv de achiziție (PO). Liniile cu servicii nu sunt verificate.
- **Restricția se activează din setări**: *Setări → România → Contabilitate*, opțiunea
  *Verifică sursa liniei de produs stocabilă* (implicit dezactivată).

## Parametri de sistem

- `l10n_ro_stock_account.check_storable_line_source` — parametrul din spatele opțiunii din
  setări (`True` / `False`).
- `l10n_ro_stock_account.skip_price_unit_check` — pus pe `True`, dezactivează verificarea
  prețului de cost nenul (implicit verificarea este activă).
