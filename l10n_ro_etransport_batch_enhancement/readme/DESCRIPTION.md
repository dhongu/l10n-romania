
Extinde funcționalitatea e-Transport pentru loturile de transferuri (stock.picking.batch), oferind suport pentru gestionarea centralizată a transportatorilor și greutăților.

## Caracteristici Cheie
- Adăugarea câmpului `l10n_ro_transport_partner_id` pe lotul de transferuri, cu sincronizare automată către toate transferurile (pickings) componente.
- Posibilitatea de a specifica un curier (`delivery.carrier`) la nivel de lot, care se propagă către transferurile individuale.
- Gestionarea greutăților la nivel de lot:
  - Calculul greutăților pe liniile de transfer din lot.
  - Distribuirea greutății totale (netă și brută) proporțional pe liniile lotului.
  - Avertisment când unor mișcări din lot le lipsește linia de greutate, ca declarația să nu plece
    la ANAF cu greutăți incomplete fără să se vadă.
- Validarea datelor e-Transport pentru loturi, injectând corect partenerul de transport în datele trimise către ANAF.
- Afișarea numărului UIT pe raportul de livrare al lotului.

## Implementare Tehnică
- Moștenește `stock.picking.batch` pentru a adăuga suportul e-Transport similar cu transferurile individuale.
- Sincronizează câmpurile de transport între lot și transferurile sale prin metode de `compute` și `inverse`.
- Extinde logica de validare a datelor (`_l10n_ro_edi_stock_validate_data`) pentru a utiliza partenerul de transport manual de pe lot.
