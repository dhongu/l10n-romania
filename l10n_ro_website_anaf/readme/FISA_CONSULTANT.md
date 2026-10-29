# Fișă Modul: Datele firmei de la ANAF în formularul de adresă al magazinului online

**Modul:** `l10n_ro_website_anaf`  
**Suită:** `l10n-romania`  
**Versiune Odoo:** 19.0  
**Utilizator principal:** clientul firmă din magazinul online (completează adresa); agentul de vânzări
(citește nota de pe comandă); consultantul de implementare (verifică fluxul)  
**Prioritate:** 🟡 Medie (scutește clientul B2B de tastarea datelor firmei și oprește comenzile pe
coduri fiscale greșite sau pe firme radiate, dar nu este un flux contabil obligatoriu)

---

## 1. Scop business

Când un client cumpără din magazinul online pe firmă, trebuie să completeze în formularul de adresă
denumirea firmei, codul fiscal și adresa sediului. Datele tastate de mână ies adesea greșit (denumire
prescurtată, cod fiscal cu o cifră greșită, CNP tastat în locul CUI-ului), iar factura și e-Factura
pleacă apoi pe date care nu corespund cu registrul ANAF.

Modulul caută firma la ANAF **chiar în timp ce clientul tastează codul fiscal (CUI)**: sub câmp apare
firma găsită (denumirea pe care se emite factura, adresa, dacă e plătitoare de TVA), iar câmpurile
goale ale formularului — numele companiei, strada, localitatea, codul poștal, județul — se completează
singure. Linkul **„Completează din ANAF”** înlocuiește, doar la cererea clientului, și ce a tastat el
deja.

La **salvarea adresei**, codul fiscal se verifică din nou pe server: un cod care nu apare la ANAF sau o
firmă radiată sunt refuzate, un CNP primește un mesaj propriu, iar pentru o firmă găsită
**partenerul clientului primește denumirea legală de la ANAF și devine „Companie”** (în Odoo 19
modulul nu creează o firmă separată deasupra persoanei de contact). O firmă inactivă fiscal poate
comanda, dar comanda primește o notă internă pentru agentul de vânzări. Dacă ANAF nu răspunde,
vânzarea nu se oprește: codul se acceptă așa cum a fost tastat și comanda primește o notă.

## 2. Bază legală și context

- **Firma inactivă fiscal** — la o firmă declarată inactivă, înregistrarea în scopuri de TVA se
  anulează (Codul fiscal, Legea 227/2015, art. 316 alin. (11) lit. a)), iar cât timp este inactivă
  firma nu își poate deduce cheltuielile și TVA-ul achizițiilor (art. 11 alin. (6); deducerea se poate
  recupera după reînregistrarea în scopuri de TVA). Modulul nu
  calculează nimic fiscal; afișează clientului un avertisment și lasă agentului de vânzări o notă cu
  consecința practică (factura se emite cu TVA, fără taxare inversă, cu codul fiscal fără prefixul
  RO; încasarea se verifică, de preferat plata în avans). Textul notei este cel din modul.
- **Firma radiată** — nu mai există juridic, deci nu poate fi cumpărător; modulul refuză adresa.
- **e-Factura** — factura se transmite în SPV pe denumirea și codul fiscal ale entității comerciale;
  modulul asigură doar că denumirea legală de la ANAF ajunge pe partenerul clientului, care este
  entitatea comercială a comenzii.
- **Sursa datelor** — serviciul public ANAF de interogare a contribuabililor, apelat prin modulul
  `l10n_ro_anaf_partner_lookup` (fără cheie de acces).

## 3. Utilizatori și roluri

| Rol | Ce face în flux |
|---|---|
| **Client din magazin (utilizator portal sau vizitator)** | tastează codul fiscal în formularul de adresă de facturare, verifică firma afișată, apasă „Completează din ANAF” dacă vrea adresa ANAF, salvează adresa |
| **Agent de vânzări** | deschide comanda din backend, citește nota internă (firmă inactivă, ANAF indisponibil) și decide modul de încasare |
| **Consultant implementare** | verifică pe o bază de test mesajele pentru fiecare situație (firmă găsită, inactivă, radiată, inexistentă, CNP) și partenerul devenit firmă în Contacte |

La testare: un utilizator portal (ex. „Ion Popescu”) cu un coș deschis pentru partea de magazin și
administratorul (sau un utilizator cu drept de **Vânzări**) pentru verificarea comenzii și a firmei în
backend.

## 4. Conturi și date implicate

Modulul **nu generează note contabile** și nu atinge conturi. Datele implicate:

| Dată | Unde ajunge |
|---|---|
| Codul fiscal (CUI), cu sau fără prefixul RO | câmpul **TVA** al formularului, apoi câmpul **TVA** al partenerului |
| Denumirea legală de la ANAF | câmpul **Numele companiei** al formularului (la tastare); la salvare, **numele partenerului** clientului, care devine „Companie” |
| Strada, localitatea, codul poștal, județul | câmpurile de adresă, **doar dacă sunt goale** (sau la „Completează din ANAF”) |
| Stare: plătitor de TVA / inactiv / radiat | doar în mesajul de sub codul fiscal și în nota de pe comandă |

Numărul de înregistrare la Registrul Comerțului (**NRC**) nu se completează din formularul de adresă
al magazinului (formularul nu are acest câmp).

Date minime pentru demo: un produs publicat în magazin, un utilizator portal cu țara România, e-mail și
telefon (telefonul e obligatoriu în formularul de adresă), un coș deschis.

## 5. Configurare inițială

Modulul nu are ecran de configurare. Pași de pregătire pe baza demo:

1. Instalați `l10n_ro_website_anaf` (aduce `website_sale` și `l10n_ro_anaf_partner_lookup`).
2. Activați limba română pe site și setați-o ca limbă implicită (**Site web → Configurare → Setări**,
   secțiunea limbilor), ca mesajele ANAF să apară în română.
3. Publicați un produs în magazin și creați (sau lăsați să se înregistreze) un client portal cu țara
   **România**.
4. Adresa serviciului ANAF este cea a modulului `l10n_ro_anaf_partner_lookup` (parametrul de sistem
   `l10n_ro_anaf_partner_lookup.url`); site-ul așteaptă un răspuns cel mult 5 secunde.

## 6. Flux de utilizare

Fluxul se desfășoară în magazin, pe pasul **Adresă** al comenzii: **Magazin → coș → Confirmă →
Editează adresa** (adresa de facturare). Căutarea pornește doar când țara din formular este
**România**. Același câmp funcționează și în formularul de adresă din contul de client
al portalului (**Contul meu → Adrese**, pentru adresa de facturare).

### Pasul 1 — Formularul de adresă de facturare

Clientul ajunge pe pasul **Adresă**. Sub e-mail și telefon sunt câmpurile **TVA** (codul fiscal) ①, pe
care îl tastează clientul, și **Numele companiei** ②, pe care îl completează căutarea. Câmpurile de
adresă (stradă, localitate, cod poștal, județ) sunt încă goale.

![Formularul de adresă de facturare, înainte de codul fiscal](../static/description/01_formular_adresa.png)

### Pasul 2 — Codul fiscal tastat: firma găsită la ANAF

Clientul tastează codul fiscal în câmpul **TVA**, cu sau fără prefixul `RO`. La tastare, spațiile,
punctele și liniuțele dintre cifre sunt ignorate; **la salvare însă codul trebuie să aibă doar cifre**
(cu sau fără `RO` în față), altfel adresa este refuzată (vezi pasul 9). După o scurtă pauză apare
„Se caută la ANAF…”, apoi, în verde, sub cod:

- **găsiți pe ecran** — mesajul „Factura se emite pe *denumire* — *adresă* — plătitor de TVA /
  neplătitor de TVA” ① și linkul **Completează din ANAF**;
- **verificați** — câmpul **Numele companiei** ② are denumirea legală de la ANAF, iar
  **Stradă și număr** ③, **Localitate** ④, **Cod poștal** ⑤ și **Județ** ⑥ s-au completat, pentru că
  erau goale.

![Firma găsită la ANAF și câmpurile goale completate](../static/description/02_firma_gasita.png)

### Pasul 3 — Ce a tastat clientul rămâne neschimbat

Dacă clientul tastase deja o adresă (de exemplu adresa depozitului), căutarea **nu o suprascrie**:
**Stradă și număr** ① rămâne cea tastată, iar câmpurile goale (localitate, cod poștal, județ, numele
companiei) se completează. Linkul **Completează din ANAF** ② rămâne la vedere.

![Strada tastată de client rămâne; linkul „Completează din ANAF”](../static/description/03_strada_tastata.png)

### Pasul 4 — „Completează din ANAF” înlocuiește adresa

La clic pe **Completează din ANAF**, toate câmpurile mapate (numele companiei, stradă, localitate, cod
poștal, județ) primesc valorile de la ANAF, inclusiv cele tastate de client: **Stradă și număr** ① are
acum adresa sediului social.

![Adresa preluată de la ANAF după „Completează din ANAF”](../static/description/04_completat_din_anaf.png)

### Pasul 5 — Firmă inactivă fiscal: avertisment, comanda continuă

Pentru o firmă inactivă, mesajul de sub cod ① este **galben-portocaliu**, arată „neplătitor de TVA” (codul
de TVA i-a fost anulat) și are un al doilea rând: firma figurează ca inactivă fiscal la ANAF; comanda
poate fi plasată, însă cât timp firma este inactivă nu își poate deduce cheltuiala și TVA-ul aferente
achiziției. Câmpurile goale se completează la fel, iar clientul poate merge mai departe cu
**Confirmă** ②.

![Avertismentul pentru firma inactivă fiscal](../static/description/05_firma_inactiva.png)

### Pasul 6 — Firmă radiată: nu poate comanda

Pentru o firmă radiată, mesajul este **roșu** ①: „*denumire* este radiată la ANAF: nu poate plasa o
comandă.” Câmpurile nu se completează, iar linkul **Completează din ANAF** nu apare.

![Mesajul pentru firma radiată](../static/description/06_firma_radiata.png)

### Pasul 7 — Cod fiscal care nu apare la ANAF

Un cod fiscal valid ca formă, dar inexistent la ANAF, primește mesajul roșu ① „Acest cod fiscal nu
apare la ANAF.” Nu se completează nimic.

![Mesajul pentru codul fiscal care nu apare la ANAF](../static/description/07_cod_negasit.png)

### Pasul 8 — CNP tastat din greșeală

O persoană fizică tastează uneori CNP-ul în câmpul de cod fiscal. Un CNP valid (13 cifre, cu cifra de
control corectă) **nu se trimite la ANAF**; apare mesajul roșu ① „Acesta pare a fi un cod numeric
personal (CNP). Dacă cumpărați ca persoană fizică, lăsați câmpul gol.”

![Mesajul pentru CNP](../static/description/08_cnp.png)

### Pasul 9 — La salvare, codul se verifică din nou pe server

Mesajele de sub cod sunt doar informative. Când clientul apasă **Confirmă**, adresa se verifică pe
server, indiferent ce a afișat formularul: pentru o firmă radiată, deasupra formularului apare eroarea
① „Firma cu acest cod fiscal este radiată la ANAF.”, câmpul **TVA** ② e marcat invalid și adresa nu se
salvează. La fel se refuză:

- un cod care nu apare la ANAF — „Codul fiscal nu este valid conform ANAF”;
- un CNP — mesaj propriu (vezi secțiunea 9);
- un cod tastat cu **spații sau liniuțe** (de exemplu „RO 185 472 90” sau „RO-18547290”) — „Codul
  fiscal trebuie să conțină doar cifre (după codul țării)”, chiar dacă la tastare firma a fost găsită;
  un cod cu **puncte** primește mesajul standard Odoo de cod TVA invalid (în engleză). Clientul
  tastează codul fără separatori și salvează din nou.

![Adresa refuzată la salvare pentru firma radiată](../static/description/09_refuz_la_salvare.png)

### Pasul 10 — Adresa salvată: comanda merge mai departe

Pentru o firmă găsită (aici, firma inactivă de la pasul 5), adresa se salvează și clientul ajunge la
**Metoda de livrare**. Cardul **Adresă de livrare** arată acum **denumirea legală a firmei**
(BETA CONSTRUCT SRL) în locul numelui tastat de client (Ion Popescu), cu adresa completată; adresa de
facturare este aceeași. Tot denumirea firmei apare și ca nume al clientului autentificat, în
dreapta-sus: în Odoo 19 numele persoanei se înlocuiește cu cel al firmei.

![Pasul următor al comenzii, după salvarea adresei](../static/description/10_adresa_salvata.png)

### Pasul 11 — Comanda din backend și nota pentru agentul de vânzări

Agentul deschide comanda din **Vânzări → Comenzi → Oferte** (scoateți filtrul implicit „Ofertele
mele”: coșul din magazin poate să nu aibă agent sau să aibă altul): cât timp clientul nu a plătit, coșul
este încă o ofertă.

- **găsiți pe ecran** — **Client** ① este firma, cu denumirea legală de la ANAF, adresa și codul
  fiscal; în istoricul din dreapta ② apare nota internă (autorul afișat este clientul, pentru că nota
  se scrie în timpul comenzii lui; nu este un mesaj tastat de el) „Clientul *cod* este declarat inactiv
  fiscal la ANAF (din *data*), iar codul său de TVA este anulat: facturăm cu TVA, fără taxare inversă,
  cu codul fiscal fără prefixul RO. Verificați încasarea, de preferat cu plată în avans.”;
- **verificați** — liniile comenzii au TVA (fără taxare inversă) și modul de plată ales ține cont de
  notă.

Mesajul „Default (RON) → Fără (Listă de prețuri)” din istoric nu vine de la acest modul: la schimbarea
adresei, magazinul standard recalculează lista de prețuri a coșului după partener (în baza de test,
fără liste de prețuri configurate, ea rămâne goală).

Dacă ANAF nu a răspuns la salvare, nota spune că codul fiscal nu a putut fi verificat și cere
verificarea datelor clientului.

![Comanda cu nota internă pentru firma inactivă](../static/description/11_comanda_nota_inactiva.png)

### Pasul 12 — Partenerul clientului, devenit firmă

Din **Client**, deschideți partenerul (sau **Vânzări → Comenzi → Clienți**). În Odoo 19 modulul nu
creează o firmă separată: **partenerul clientului** (cel legat de contul lui de portal) primește
denumirea legală de la ANAF ① și are selectat **Companie** ③. **TVA** ② are codul fiscal, **fără
prefixul `RO`**, deși clientul l-a tastat cu `RO`: modulul nu scrie pe firmă starea de plătitor de TVA,
deci **TVA aplicabil** rămâne nebifat, iar localizarea RO (`l10n_ro_config`) scoate prefixul `RO` de la
orice partener cu TVA aplicabil nebifat. Pentru această firmă inactivă rezultatul este corect
(cumpărător fără cod de TVA valid); **pentru o firmă activă, plătitoare de TVA, este greșit** și se
corectează manual (vezi „Note de monografie” și secțiunea 8). **NRC** rămâne gol (formularul magazinului nu îl
are). Fila **Contacte** este goală: numele persoanei (Ion Popescu) nu se mai păstrează nicăieri; dacă
este nevoie de persoana de contact, ea se adaugă manual.

![Partenerul clientului, cu denumirea legală de la ANAF](../static/description/12_firma_din_anaf.png)

### Note de monografie și raportare

Modulul **nu generează note contabile**. Efectul lui asupra contabilității este indirect: factura
emisă din comandă poartă **denumirea legală de la ANAF** (numele partenerului clientului) și codul
fiscal verificat la ANAF. Adresa cumpărătorului este cea de la ANAF doar dacă clientul nu a tastat alta
sau a apăsat „Completează din ANAF”. **Starea de plătitor de TVA nu se preia pe firmă**: orice client
salvat din magazin rămâne cu **TVA aplicabil** nebifat și, cu localizarea RO, cu codul fiscal fără
prefixul `RO`. Pentru o firmă plătitoare de TVA, bifa **TVA aplicabil** și prefixul `RO` trebuie puse
manual **înainte de prima factură**, altfel factura, e-Factura și D394 o tratează ca neplătitoare de
TVA. Aceste date ajung apoi în e-Factura, jurnalul de vânzări și declarații (D394, SAF-T). Pentru o firmă inactivă, factura
se emite cu TVA, fără taxare inversă (vezi nota de la pasul 11).

## 7. Legături cu alte module / declarații

| Modul | Rol |
|---|---|
| `website_sale` | formularul de adresă al comenzii, în care se face căutarea și verificarea la salvare |
| `l10n_ro_anaf_partner_lookup` | face cererea la ANAF și întoarce datele firmei (localitate, sector București, cod poștal) |
| `portal` | formularul de adresă din contul de client folosește aceleași câmpuri |
| `deltatech_b2b_portal` (suita bitshop) | formularul de cerere de cont B2B folosește aceeași căutare (atributele `data-anaf-lookup` și `data-anaf-fill`); acolo se completează și NRC-ul |
| `deltatech_website_vat_validation` | notă istorică: versiunile până la 19.0.0.1.0 făceau aceeași verificare la salvare; cât timp o asemenea versiune o face, modulul acesta nu o repetă |

**Ce e automat:** căutarea la tastarea codului; completarea câmpurilor goale; refuzul la salvare
pentru cod inexistent, firmă radiată, CNP și cod cu separatori; denumirea legală și tipul „Companie” pe
partenerul clientului; nota pe comandă pentru firmă inactivă sau ANAF indisponibil; cache-ul de o zi și
limita de cereri (doar pentru căutarea de la tastare).

**Ce rămâne manual:** înlocuirea adresei tastate de client (doar prin „Completează din ANAF”);
decizia agentului privind încasarea la o firmă inactivă; verificarea datelor când ANAF a fost
indisponibil; adăugarea persoanei de contact, dacă e nevoie (numele tastat de client se înlocuiește cu
denumirea firmei); NRC-ul firmei; bifa **TVA aplicabil** și prefixul `RO` pentru o firmă plătitoare
de TVA. Starea de plătitor de TVA apare doar în mesajul de sub cod — modulul nu o scrie pe firmă.

## 8. Verificări pentru consultant

- [ ] Cu țara **România** în formular, tastarea unui CUI existent afișează în verde firma, adresa și
  „plătitor de TVA”/„neplătitor de TVA”.
- [ ] Un CUI tastat cu spații (de exemplu „RO 185 472 90”) găsește firma la tastare, dar la
  **Confirmă** este refuzat cu „Codul fiscal trebuie să conțină doar cifre (după codul țării)”; fără
  spații, adresa se salvează.
- [ ] Câmpurile goale (numele companiei, stradă, localitate, cod poștal, județ) se completează; o stradă
  tastată înainte rămâne neschimbată.
- [ ] **Completează din ANAF** înlocuiește strada tastată cu adresa de la ANAF.
- [ ] Cu altă țară decât România în formular, nu apare niciun mesaj ANAF.
- [ ] O firmă inactivă primește mesaj galben-portocaliu, adresa se salvează, iar comanda are nota internă
  cu data inactivării.
- [ ] O firmă radiată primește mesaj roșu la tastare și eroare la **Confirmă**; adresa nu se salvează.
- [ ] Un cod inexistent la ANAF este refuzat la salvare cu „Codul fiscal nu este valid conform ANAF”.
- [ ] Un CNP valid primește mesajul de CNP și nu ajunge la ANAF.
- [ ] După salvare, partenerul clientului din Contacte poartă denumirea legală, are tipul
  **Companie** (selectat) și are codul fiscal în **TVA**; numele persoanei tastat în formular nu se mai regăsește.
- [ ] Pentru o firmă **activă, plătitoare de TVA**, verificați după salvare câmpurile **TVA** și
  **TVA aplicabil** de pe firmă: modulul nu scrie starea de plătitor, iar localizarea RO scoate
  prefixul `RO` cât timp TVA aplicabil e nebifat. Bifați **TVA aplicabil** și puneți `RO` în față
  înainte de prima factură (altfel D394 și e-Factura o tratează ca neplătitoare).
- [ ] Același CUI căutat a doua oară în aceeași zi răspunde imediat la tastare (din cache), fără o nouă
  cerere la ANAF. Cache-ul și limita privesc doar căutarea de la tastare: la salvare codul se verifică
  mereu la ANAF. Cache-ul și limita de căutări sunt ținute în memoria fiecărui proces (worker) al serverului;
  pe o instanță cu mai mulți workeri, testați pe un singur worker.
- [ ] Cu serviciul ANAF indisponibil, adresa se salvează și comanda primește nota „nu a putut fi
  verificat la ANAF”.

## 9. Mesaje de eroare frecvente

| Mesaj | Cauză | Remediere |
|---|---|---|
| „Acest cod fiscal nu apare la ANAF.” (la tastare) | codul nu există în registrul ANAF | clientul verifică codul pe certificatul de înregistrare |
| „Codul fiscal nu este valid conform ANAF” (la salvare) | același caz, verificat pe server | se corectează codul; adresa nu se salvează până atunci |
| „*denumire* este radiată la ANAF: nu poate plasa o comandă.” / „Firma cu acest cod fiscal este radiată la ANAF.” | firma este radiată | comanda nu se poate plasa pe această firmă |
| „Acesta pare a fi un cod numeric personal (CNP). Dacă cumpărați ca persoană fizică, lăsați câmpul gol.” (la tastare) | s-a tastat un CNP în câmpul de cod fiscal | persoana fizică lasă câmpul gol |
| „Acesta pare a fi un cod numeric personal (CNP). Câmpul este pentru codul fiscal (CUI) al unei firme; dacă cumpărați ca persoană fizică, lăsați-l gol.” (la salvare) | același caz, verificat pe server | persoana fizică lasă câmpul gol; adresa nu se salvează până atunci |
| „Codul fiscal trebuie să conțină doar cifre (după codul țării)” | la salvare, codul are spații, liniuțe sau alte caractere după `RO` (la tastare acestea sunt ignorate) | se tastează doar cifrele, fără separatori (cu sau fără `RO` în față) |
| „The VAT number [...] does not seem to be valid…” (în engleză) | mesajul standard Odoo: codul are puncte sau nu respectă formatul unui cod fiscal românesc | se tastează doar cifrele, fără separatori |
| Niciun mesaj sub cod | țara din formular nu e România, codul are sub 2 cifre sau formatul e invalid (peste 10 cifre) | se alege România și se tastează CUI-ul complet |
| Niciun mesaj după multe căutări | s-a atins limita de 20 de căutări în 10 minute de pe aceeași adresă IP (per worker) | se așteaptă; la salvare codul se verifică oricum pe server |
| Niciun mesaj după „Se caută la ANAF…” | ANAF nu a răspuns în 5 secunde | clientul poate salva; codul se acceptă așa cum e tastat, iar comanda primește nota de indisponibilitate |
| Nota „Codul fiscal … nu a putut fi verificat la ANAF (serviciu indisponibil)” pe comandă | ANAF nu a răspuns în 5 secunde | agentul verifică manual datele clientului |

## 10. Capturi de ecran

Capturile din `static/description/` sunt **generate automat** de `tests/test_screenshots.py` (mixinul
`ScreenshotCase` din `l10n_ro_doc_screenshots`, import defensiv), cu interfața în română, pe compania
„RO Company” cu planul de conturi RO, în Odoo 19. Răspunsurile ANAF sunt simulate în test (fără cereri
reale).

| Fișier | Ce arată |
|---|---|
| `01_formular_adresa.png` | formularul de adresă de facturare, cu câmpurile Numele companiei și TVA goale |
| `02_firma_gasita.png` | firma găsită la ANAF sub codul fiscal și câmpurile goale completate |
| `03_strada_tastata.png` | strada tastată de client păstrată; linkul „Completează din ANAF” |
| `04_completat_din_anaf.png` | adresa de la ANAF după „Completează din ANAF” |
| `05_firma_inactiva.png` | avertismentul galben-portocaliu pentru firma inactivă fiscal |
| `06_firma_radiata.png` | mesajul roșu pentru firma radiată |
| `07_cod_negasit.png` | mesajul pentru codul fiscal care nu apare la ANAF |
| `08_cnp.png` | mesajul pentru CNP |
| `09_refuz_la_salvare.png` | eroarea de la salvare pentru firma radiată |
| `10_adresa_salvata.png` | pasul următor al comenzii, după salvarea adresei, cu denumirea firmei |
| `11_comanda_nota_inactiva.png` | comanda în backend, cu nota internă pentru firma inactivă |
| `12_firma_din_anaf.png` | partenerul clientului, devenit firmă cu denumirea legală |

Regenerare:

```bash
.venv/bin/python odoo/odoo-bin -c odoo.conf -d <db> -u l10n_ro_website_anaf \
    --test-tags=fise_screenshots/l10n_ro_website_anaf --stop-after-init
```

(`l10n_ro_doc_screenshots` și `deltatech_doc_screenshots` trebuie să fie în `addons_path`; baza
trebuie să aibă planul de conturi RO și limba română.)

## 11. Observații pentru manual

- Accentul cade pe **momentul tastării**: clientul vede imediat pe ce firmă se emite factura, înainte
  de a salva.
- De subliniat regula „**doar câmpurile goale**”: căutarea nu strică o adresă de livrare tastată de
  client; adresa sediului vine doar la clic pe „Completează din ANAF”.
- Mesajele de sub cod sunt informative; **verificarea care contează este cea de la salvare**. Clientul
  trebuie îndrumat să tasteze codul fiscal **fără spații, puncte sau liniuțe**: la tastare firma se
  găsește oricum, dar la salvare codul cu separatori este refuzat.
- În Odoo 19, denumirea legală **înlocuiește numele clientului** pe partenerul lui (inclusiv numele
  afișat în contul de portal), iar partenerul devine „Companie”; pe comandă și pe factură apare firma.
  Persoana de contact nu se creează automat.
- Unele etichete ale ecranelor standard Odoo nu au încă traducere în română în Odoo 19 și apar în
  engleză în capturi: în magazin banda galbenă despre adresele de livrare și facturare; în backend
  „Sales Order created”. Nu țin de acest modul.
- Limita de 20 de căutări în 10 minute și cache-ul de o zi protejează serviciul ANAF de abuz (ruta
  este publică); nu se configurează din interfață.
