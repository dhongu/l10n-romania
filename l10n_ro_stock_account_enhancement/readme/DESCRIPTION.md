Modulul adaugă controale suplimentare peste evaluarea stocului din localizarea românească
(`l10n_ro_stock_account`), ca valorile ajunse în contabilitate să nu fie zero sau fără sursă.

## Funcții principale

- **Preț de cost nenul pe mișcările de stoc**: calculul prețului unitar al unei mișcări de stoc
  (`stock.move._get_price_unit`) se oprește cu o eroare dacă mișcarea nu are valoare, în loc să
  ducă în contabilitate o descărcare de gestiune la cost zero. Prețul folosit la costul vânzării
  (COGS) de pe factură nu este verificat.
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
