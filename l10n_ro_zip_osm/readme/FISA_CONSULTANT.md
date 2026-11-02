# Fișă Modul: Străzile orașelor mici în nomenclatorul de coduri poștale

**Modul:** `l10n_ro_zip_osm`
**Utilizator principal:** Operatorul care creează și întreține partenerii (agent de vânzări, operator comenzi, contabil la introducerea furnizorilor)
**Prioritate:** 🟢 Scăzută (modul de date, instalat automat; nu schimbă codul poștal, doar ajută la alegerea străzii)

---

## 1. Scop business

Poșta Română are **un singur cod poștal** pentru orașele sub 50.000 de locuitori și nu le publică
străzile, așa că nomenclatorul din modulul `l10n_ro_zip` are pentru ele un singur rând, fără
stradă. Pe partener, operatorul nu poate căuta strada, ci doar alege codul orașului. Modulul
adaugă în nomenclator **15.968 de străzi** pentru **269 de astfel de orașe** (de ex. Pantelimon,
Voluntari, Lugoj, Râmnicu Sărat, Tecuci, Câmpina, Bușteni, Huși), fiecare cu codul poștal unic
al orașului. Operatorul caută strada pe partener la fel ca într-un oraș mare, iar codul poștal se
completează corect.

Modulul nu are meniuri, câmpuri sau setări proprii: aduce doar date în nomenclatorul existent.

## 2. Bază legală și context

- Nu există o obligație legală care să ceară un nomenclator anume. Modulul ține de **calitatea
  datelor de adresă**; codul poștal ajunge în adresa partenerului de pe factură și din e-Factura.
- **Sursa datelor**: numele străzilor vin din [OpenStreetMap](https://www.openstreetmap.org/copyright)
  (© contribuitorii OpenStreetMap), sub licența
  [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/); codurile poștale vin
  de pe [posta-romana.ro](https://www.posta-romana.ro). Atribuirea este în secțiunea *Credits* a
  modulului.
- Numele străzilor sunt scrise **fără diacritice**, ca în restul nomenclatorului Poștei.
- OpenStreetMap este o hartă colaborativă: lista străzilor unui oraș poate fi incompletă sau poate
  conține denumiri vechi. Codul poștal este însă mereu cel unic al orașului, deci corect.

## 3. Utilizatori și roluri

Drepturile sunt cele ale modulului `l10n_ro_zip`; modulul nu adaugă altele.

- **Operatorul de parteneri** (dreptul **Contact: Creare**): caută strada pe partener.
- **Administratorul / consultantul** (rolul **Administrator**): vede lista
  nomenclatorului în **Contacte → Configurare → Localizare → Coduri poștale**.
- **La testare**: un administrator pentru listă și un utilizator cu **Contact: Creare** pentru
  partener.

## 4. Conturi și date implicate

Modulul **nu generează note contabile** și nu atinge conturi. Datele implicate:

| Dată | Unde | Observație |
|---|---|---|
| Străzile orașelor mici | **Coduri poștale** (nomenclatorul din `l10n_ro_zip`) | 15.968 de rânduri: tip și nume de stradă, codul unic al orașului, localitate, județ, oficiul poștal al orașului |
| Localitatea și județul | județele României și localitățile din `l10n_ro_city`, dacă e instalat | fiecare stradă se leagă de județ și, când `l10n_ro_city` e instalat, de localitate |
| Codul poștal de pe partener | câmpul **Cod poștal** din nomenclator, sub localitate, și codul tipărit al adresei | comportamentul este cel din `l10n_ro_zip` |

Date minime pentru demo: un partener firmă din România, cu localitatea **Huși (VS)** aleasă din
listă (cod poștal unic `735100`).

## 5. Configurare inițială

1. Pe o bază nouă, modulul se instalează **automat** împreună cu `l10n_ro_zip`, când baza are o
   firmă din România. Pe o bază unde `l10n_ro_zip` era deja instalat, actualizarea lui nu
   instalează acest modul: instalați-l din **Aplicații**; străzile existente nu se dublează.
2. Localitățile României vin cu modulul `l10n_ro_city`, care se instalează separat (recomandat).
   Fără el, străzile se leagă doar de județ, iar pe partener nu se pot filtra după localitate;
   dacă `l10n_ro_city` se instalează mai târziu, străzile se leagă atunci de localități, automat.
3. Străzile se încarcă la instalare, fără pași manuali. O stradă deja existentă în nomenclator nu
   se adaugă a doua oară.
4. Nu există parametri de configurat.

## 6. Flux de utilizare

Fluxul complet al codului poștal pe partener este descris în fișa modulului `l10n_ro_zip`. Aici,
doar ce se schimbă pentru un oraș mic, pe exemplul orașului Huși.

### Pasul 1 — Străzile unui oraș mic în nomenclator

Ca administrator, accesați **Contacte → Configurare → Localizare → Coduri poștale** și căutați
codul poștal al orașului (tastați `735100` și apăsați Enter).

- **Găsiți pe ecran:** ① în bara de căutare, filtrul **Cod poștal** cu valoarea `735100`; în
  dreapta-sus, numărul de rânduri găsite (163); coloanele **Tip stradă**, **Nume Stradă**,
  **Cod poștal**, **Localitate** (*Huși (VS)*), **Stare** (aici înseamnă județul, *Vaslui (RO)*) și
  **Țară**.
- **Verificați:** primul rând, fără stradă, este rândul orașului din nomenclatorul Poștei;
  celelalte 162 sunt străzile aduse de modul (*Alee Dobrina*, *Bulevard 1 Mai*, *Strada 1 Decembrie
  1918* etc.), toate cu același cod `735100` și cu localitatea completată. Un oraș pentru care
  căutarea codului întoarce un singur rând nu este acoperit de modul.

![Lista Coduri poștale filtrată după codul 735100: 163 de rânduri, primul fără stradă, apoi străzile din Huși (Alee Dobrina, Bulevard 1 Mai, Strada 1 Decembrie 1918 și altele), toate cu codul 735100, localitatea Huși (VS), județul Vaslui (RO) și țara România; filtrul de căutare este evidențiat](../static/description/01_lista_strazi_oras_mic.png)

### Pasul 2 — Căutarea străzii pe un partener din Huși

Deschideți partenerul din **Contacte**. În blocul de adresă, alegeți întâi ① **localitatea**
(*Huși (VS)*); județul și codul poștal al orașului (`735100`) se completează singure. Apoi, în ② câmpul **Cod poștal** din nomenclator,
aflat sub localitate (câmpul cu săgeată de listă, fără etichetă vizibilă), tastați numele străzii.

- **Găsiți pe ecran:** după ce ați tastat *Stefan cel Mare*, lista propune *Strada Stefan cel
  Mare*, cu gri în dreapta `735100 · Husi, VS`.
- **Verificați:** propunerile sunt doar din localitatea aleasă; codul din dreapta este codul
  unic al orașului. Fără diacritice găsiți mai sigur, pentru că numele străzilor nu le au. Dacă
  strada nu apare, folosiți *Caută mai mult...* sau alegeți rândul orașului, fără stradă: codul
  poștal este același.

![Partenerul Exemplu Distribuție SRL cu localitatea Huși (VS), județul Vaslui (RO) și codul poștal 735100 deja completat: în câmpul Cod poștal de sub localitate s-a tastat Stefan cel Mare, iar lista propune Strada Stefan cel Mare cu 735100 · Husi, VS; localitatea și câmpul de căutare sunt evidențiate cu 1 și 2](../static/description/02_partener_cautare_strada.png)

### Pasul 3 — Codul poștal completat pe partener

Alegeți propunerea (*Strada Stefan cel Mare*) și salvați partenerul (iconița de salvare de lângă
numele lui).

- **Găsiți pe ecran (înainte de salvare):** ① localitatea *Huși (VS)*; ② județul *Vaslui (RO)*;
  ③ codul poștal al adresei, care rămâne `735100`; ④ câmpul din nomenclator, cu *Strada Stefan
  cel Mare (735100)*; țara *România*.
- **Verificați:** codul poștal tipărit (③) este codul unic al orașului; strada din adresa
  partenerului (*Strada Ștefan cel Mare nr. 5*) rămâne cum a scris-o operatorul.

![Partenerul după alegerea străzii: localitatea Huși (VS), județul Vaslui (RO), codul poștal 735100 și câmpul din nomenclator cu Strada Stefan cel Mare (735100) sunt evidențiate cu 1–4; țara România; strada adresei rămâne Strada Ștefan cel Mare nr. 5; formularul are modificări nesalvate](../static/description/03_partener_cod_completat.png)

### Note de monografie și raportare

Modulul **nu generează note contabile** și nu are rapoarte. Factura, avizul și XML-ul e-Factura
preiau codul poștal din adresa partenerului (③ din pasul 3), ca la orice alt cod din nomenclator.

## 7. Legături cu alte module / declarații

| Modul | Rol în flux |
|---|---|
| `l10n_ro_zip` (obligatoriu) | nomenclatorul de coduri poștale și câmpul **Cod poștal** de pe partener, în care apar străzile |
| `l10n_ro_city` (recomandat, se instalează separat) | localitățile României, de care se leagă străzile; fără el, străzile nu se filtrează pe partener după localitate |
| e-Factura / rapoartele de factură | preiau codul poștal din adresa partenerului |

**Ce e automat:** instalarea modulului împreună cu `l10n_ro_zip`; încărcarea străzilor și
legarea lor de județ și localitate (și la o instalare ulterioară a `l10n_ro_city`); sărirea
străzilor deja existente în nomenclator.

**Ce rămâne manual:** alegerea localității înaintea străzii; completarea străzii și a numărului în
adresă; pentru o stradă care lipsește din OpenStreetMap, alegerea rândului orașului (același cod).

## 8. Verificări pentru consultant

- [ ] Modulul **Romania - Postal Codes, Streets of Small Towns** apare instalat în **Aplicații**
      (pe o bază nouă, automat; pe una existentă, după instalarea lui din **Aplicații**).
- [ ] În **Coduri poștale**, căutarea codului `735100` întoarce 163 de rânduri (rândul orașului
      Huși și 162 de străzi), toate cu localitatea *Huși (VS)*.
- [ ] Pe un partener cu localitatea *Huși*, tastarea *Stefan cel Mare* în câmpul **Cod poștal**
      propune *Strada Stefan cel Mare* (`735100`).
- [ ] După alegere, codul poștal al adresei este `735100`, iar strada și numărul din adresă nu
      s-au schimbat.
- [ ] Pentru un alt oraș mic al clientului (ex. Lugoj, Câmpina), căutarea codului în listă arată
      străzile, cu localitatea completată.
- [ ] În listă, căutarea codului unui oraș acoperit nu arată aceeași stradă de două ori.

## 9. Mesaje de eroare frecvente

Modulul nu afișează mesaje de eroare proprii. Situațiile frecvente:

| Mesaj / simptom | Cauză | Remediere |
|---|---|---|
| Pentru un oraș mic, lista nu propune nicio stradă | orașul nu este printre cele 269 acoperite (căutarea codului în listă întoarce un singur rând) | alegeți rândul orașului, fără stradă; codul poștal este același |
| Strada nu se propune, deși orașul are străzi în listă | strada lipsește din OpenStreetMap sau are alt nume acolo; ori localitatea partenerului nu este aleasă | căutați după o parte din nume sau prin *Caută mai mult...*; altfel alegeți rândul orașului |
| Străzile din Breaza (PH), Băile Govora, Băile Olănești și Ocnele Mari nu se propun pe partener | aceste orașe lipsesc din lista localităților (`l10n_ro_city`), deci nu pot fi alese pe partener; străzile lor apar doar în nomenclator, cu coloana **Localitate** goală | căutați codul poștal al orașului în câmpul **Cod poștal**; anunțați echipa de suport pentru completarea localității |
| Străzile există în listă, dar nu se propun pe partener | coloana **Localitate** este goală: `l10n_ro_city` nu este instalat sau numele localității diferă | verificați că `l10n_ro_city` este instalat; altfel anunțați echipa de suport pentru legarea străzilor de localitate |
| Numele străzii nu are diacritice | nomenclatorul scrie numele fără diacritice | normal; strada din adresă o scrieți cu diacritice, câmpul din nomenclator rămâne fără |

## 10. Capturi de ecran

Capturile sunt generate automat din `tests/test_screenshots.py` (mixinul `ScreenshotCase` din
`deltatech_doc_screenshots` sau, în lipsa lui, `l10n_ro_doc_screenshots`, import defensiv; dacă
lipsește, testul se sare), în RO, pe compania „RO Company” în RON, în `static/description/`, în
ordinea pașilor din secțiunea 6. Străzile sunt cele reale din modul; partenerul *Exemplu
Distribuție SRL* este de exemplu. Aceleași ecrane, cu interfața în engleză, sunt în
`static/description/en/`, pentru `readme/USAGE.md`.

| # | Fișier | Conținut |
|---|--------|----------|
| 1 | `../static/description/01_lista_strazi_oras_mic.png` | Lista **Coduri poștale** filtrată după codul `735100`: străzile din Huși |
| 2 | `../static/description/02_partener_cautare_strada.png` | Partener din Huși: căutarea *Stefan cel Mare* în câmpul **Cod poștal** și propunerea |
| 3 | `../static/description/03_partener_cod_completat.png` | Partenerul după alegerea străzii: codul `735100`, localitatea și județul |

Regenerare:

```bash
./odoo/odoo-bin -c odoo.conf -d test19 -i l10n_ro_zip_osm,deltatech_doc_screenshots \
    --test-tags=/l10n_ro_zip_osm:TestZipOsmScreenshots --stop-after-init
```

## 11. Observații pentru manual

- Capitolul este o completare a celui despre codul poștal pe partener (`l10n_ro_zip`): aceeași
  regulă *localitate → stradă în câmpul Cod poștal → alegere*, acum și pentru orașele mici.
- De spus clar că, la un oraș mic, codul poștal este același pentru toate străzile; strada aleasă
  ajută doar la căutare și la consecvența adresei.
- De menționat sursa OpenStreetMap și licența ODbL, și că lista poate fi incompletă: rândul
  orașului rămâne soluția de rezervă.
- Fără diacritice în căutare: numele străzilor nu le au.
