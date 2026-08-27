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
