
Modulul l10n_ro_etransport_enhancement extinde funcționalitatea standard e-Transport din Odoo cu caracteristici și îmbunătățiri suplimentare. Acest modul optimizează integrarea sistemului e-Transport pentru conformitatea fiscală din România, făcându-l mai flexibil și mai ușor de utilizat.
## Caracteristici Cheie
- Posibilitatea de a defini un partener de transport manual (`l10n_ro_transport_partner_id`) fără a fi necesară configurarea unui curier (`delivery.carrier`).
- Validarea transferurilor (pickings) permite lipsa curierului dacă este completat partenerul de transport.
- Calculul și distribuirea greutăților (netă și brută) direct pe liniile de transfer pentru raportarea corectă în e-Transport.
- Integrare îmbunătățită pentru preluarea prețurilor din comenzile de vânzare/achiziție în documentul e-Transport.
- Suport pentru corecția greutăților pe linii prin distribuirea unei valori totale.

## Implementare Tehnică
Modulul se bazează pe localizarea standard pentru România și îmbunătățește integrarea e-Transport prin:
- Metode extinse pentru livrări (stock picking) pentru trimiterea documentelor e-Transport
- Mecanisme avansate de urmărire a straturilor de evaluare a stocurilor (stock valuation layers)
- Gestionare îmbunătățită a contextului pentru diferite scenarii de trimitere a documentelor

## Beneficii pentru Afacere
- Conformitate simplificată cu reglementările românești privind e-Transport
- Opțiuni mai flexibile pentru transmiterea documentelor de transport către autorități
- Monitorizare și gestionare mai bună a mișcărilor de stoc supuse cerințelor e-Transport
- Reducerea poverii administrative pentru departamentele de logistică și contabilitate

## Utilizare
După instalare, modulul îmbunătățește automat funcționalitatea e-Transport în operațiunile de stoc. Utilizatorii pot accesa funcțiile extinse e-Transport prin interfața de livrări, cu opțiuni suplimentare disponibile în meniul de acțiuni.
Acest modul face parte din suita de localizare pentru România dezvoltată de Terrabit.

