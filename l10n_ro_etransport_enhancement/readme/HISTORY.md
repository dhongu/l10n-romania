## 19.0.0.9.0 (2026-09-13)

**Corecție** — liniile declarate într-o unitate de măsură secundară (cutie, bax,
pungă) plecau la ANAF cu unitatea și valoarea greșite.

Standardul `l10n_ro_edi_stock` compune linia din două surse diferite:
`cantitate` este `move.product_qty`, prin definiție cantitatea în unitatea de
măsură de BAZĂ a produsului, iar `codUnitateMasura` vine din `move.product_uom`,
unitatea aleasă pe LINIE. Cât timp cele două coincid nu se vede nimic; când
transferul e făcut într-o unitate secundară, perechea devine incoerentă. O
recepție de import de 10 cutii × 13 kg pleca drept `cantitate="130"`
`codUnitateMasura="C62"` — „130 de bucăți". Schema ANAF validează fiecare atribut
separat și nu prinde nepotrivirea dintre ele, deci declarația primea UIT, iar
eroarea rămânea tăcută. În plus, orice unitate proprie a clientului (fără XML ID
în lista fixă din `_get_unece_code()`) cade oricum pe `C62`, deci codul liniei nu
putea fi corect nici teoretic.

Cu setarea **„UIT: get price from order"** activă, aceeași nepotrivire afecta și
valoarea: prețul se calcula per unitate a liniei de comandă
(`price_subtotal / product_qty` pe `purchase.order.line`, `price_reduce_taxexcl`
pe linia de vânzare) și se înmulțea cu o cantitate exprimată în unitatea de bază,
declarând la ANAF de 13 ori valoarea reală în exemplul de mai sus.

Acum `codUnitateMasura` urmează unitatea în care e exprimată cantitatea, iar
prețul din comandă se convertește în unitatea de bază a produsului — ambele așa
cum face deja calea de dropship. Transferurile fără unități secundare produc
exact aceeași declarație ca înainte.

## 19.0.0.8.1 (2026-09-09)

- Configure the optional OCA Romanian-accounting flag in the view test fixture;
  preserve the localization's field-hiding behavior for other companies.
- Check loading-address visibility for every supported dropship operation and
  retain existing warehouse/border/customs visibility rules.
- Document the intentional separate ORM extension and its required super() chain
  with a scoped Pylint exception; no repository-wide checks are disabled.

## 19.0.0.7.6 (2026-08-27)

**Corecție** — codul UIT nu mai este scris în `carrier_tracking_ref`.

La „Preluare stare", când declarația ajungea `stock_validated`, UIT-ul era copiat
în `carrier_tracking_ref` (referința de urmărire a curierului, din `stock_delivery`).
UIT-ul nu este un AWB: pe o livrare cu curier, scrierea suprascria sau preceda
numărul real de AWB (tracking-ul, eticheta și evidența curierului se legau de un
cod ANAF), iar pe orice bază care protejează referința de urmărire (module de
curierat care permit scrierea ei doar din fluxul curierului) butonul ridica
„Operație invalidă" și derula înapoi inclusiv starea tocmai preluată de la ANAF.
Standardul `l10n_ro_edi_stock` nu citește nicăieri `carrier_tracking_ref`, iar
UIT-ul rămâne disponibil în `l10n_ro_edi_stock_document_uit` (tab-ul eTransport).
Același lucru pentru `post_init_hook`-ul de migrare din vechiul `l10n_ro_etransport`.

## 19.0.0.7.5 (2026-08-15)

- Imp: `l10n_ro_transport_partner_id` and `l10n_ro_etransport_start_address` are now indexed. Both are foreign keys to `res_partner` on `stock_picking`, one of the largest tables on high-volume instances.
  Context: `res_partner` is referenced by ~158 foreign-key columns; on a production database 77 of them had no index, so a single partner deletion triggered sequential scans over 3.180 MB of tables. Deleting 5.350 merged partner records took over 8 minutes without indexes and 190 seconds with them, foreign keys left ENABLED.

## 19.0.0.7.4

**Îmbunătățire** — coloana mișcării, în lista de linii de greutate, nu identifica produsul.

Coloana `move_id` din lista **Shipping Weight Lines** afișa `display_name`-ul
standard al mișcării de stoc (`origine/cod_produs: locație>locație_destinație`),
care nu include denumirea produsului — doar codul intern, și doar dacă produsul
are cod setat. Când o livrare avea mai multe linii de greutate, acestea puteau
ieși identice și imposibil de distins vizual (ex. două linii arătând ambele
„S00011/Stoc>Customers"). Contextul `show_product_in_move`, deja transmis de
view dar neconsumat până acum, este folosit acum într-un override al
`stock.move._compute_display_name`: când e prezent în context, coloana arată
direct denumirea produsului. Comportamentul standard al `display_name`-ului
(fără acest context) rămâne neschimbat oriunde altundeva.

## 19.0.0.7.3

**Corecție** — greutatea netă/brută ieșea greșită când mișcarea de stoc era
în altă UoM decât baza produsului.

`net_weight`/`gross_weight` (atât la „Get lines" cât și la adăugarea manuală
a unei linii de greutate) înmulțeau `move.quantity` direct cu
`l10n_ro_net_weight`/`weight`, câmpuri exprimate per unitate din UoM-ul de
bază al produsului. Când produsul era livrat într-o UoM secundară (ex.
cutie/palet, nu kg), rezultatul ieșea greșit cu exact factorul de conversie
dintre cele două unități. Cantitatea e convertită acum explicit la UoM-ul de
bază al produsului înainte de înmulțire.

## 19.0.0.7.2

**Îmbunătățire** — locație de start specifică pentru transportul pe teritoriul național.

Câmpul **Specific Start Location** (`l10n_ro_etransport_start_address`) permite
alegerea manuală a unui partener a cărui adresă să înlocuiască, în declarația
eTransport, adresa calculată automat (depozit) pentru locația de start —
util când transportul național (cod operațiune `30`) pleacă efectiv dintr-un
alt loc decât depozitul (de exemplu un birou vamal de interior, după vămuire).

Câmpul e vizibil doar pe livrări (`picking_type_code = 'outgoing'`), doar
pentru operațiunea "Transport pe teritoriul național" și doar când locația de
start e de tip "Location" (nu are sens pe BCP/birou vamal, unde declarația nu
conține o adresă).

## 19.0.0.7.1

**Corecție** — documentele însoțitoare fără observație erau respinse de ANAF.

Atributul `observatii` este tipat `Str200` (minLength=1) în schema eTransport, iar
QWeb randează string-ul gol ca `observatii=""`. Un document însoțitor lăsat fără
observații pica la validare cu:

    cvc-minLength-valid: Value '' with length = '0' is not facet-valid
    with respect to minLength '1' for type 'Str200'

Acum atributul este omis complet când observația lipsește (sau conține numai spații).
Câmpul **Observații** de pe linia de document rămâne opțional.
## 19.0.0.8.0 (2026-09-09)

- Support factory-to-customer dropships (operations 10, 20, 30, 40, 50) through
  the existing eTransport action, without a fictitious warehouse or stock transfer.
- Resolve the supplier loading address (or explicit loading override), linked
  orders' delivery address and sale's commercial customer separately.
- Use the declared purchase (AIC/import) or sale (domestic/LIC/export) value in RON with native UoM/currency
  conversion. Reject missing, inconsistent or cross-company order links.
- Preserve native carrier/vehicle/border/customs validation. Ambiguous international
  transactions, returns and batch dropship declarations require separate review.
- Use native product weight when the optional legacy net-weight field is absent.
- Add translatable help, Romanian translations and language-aware accompanying
  document names. No new addon and no change to existing document type codes.
