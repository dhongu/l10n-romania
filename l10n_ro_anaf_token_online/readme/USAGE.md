1. Importați `deltatech_iap_online`, apoi acest modul, din **Aplicații → Importați Modulul**. Dacă baza
   are instalat `terrabit_iap_anaf`, dezinstalați-l întâi: importul e refuzat cât timp e instalat.

2. Deschideți **Setări → Facturare**, blocul **E-Factura România** (firma trebuie să aibă țara
   fiscală România și codul fiscal completat). Butonul standard **Generare token** e ascuns;
   apăsați **Generează token (Terrabit)**. Prima apăsare activează serviciul Terrabit; după câteva
   secunde, apăsați din nou: se deschide, într-o filă nouă, autorizarea ANAF pe serverul Terrabit.

   ![Blocul E-Factura România cu câmpurile tokenului goale și butonul Generează token (Terrabit) evidențiat](static/description/01_setari_buton_terrabit.png)

3. Serviciul apare în **Setări → Credite Terrabit → Servicii și credite**, ca **ANAF SPV Token**,
   cu soldul în **Credite rămase** (1 credit = 1 EUR). Activarea a reușit când a doua apăsare pe
   **Generează token (Terrabit)** deschide pagina de autorizare; altfel, verificați cererea de
   activare în **Setări → Tehnic → Servicii Terrabit → Cereri** (modul dezvoltator). O autorizare
   reușită costă 1 credit, iar reînnoirile sunt gratuite: înainte de autorizare, **Credite rămase**
   trebuie să fie cel puțin 1 (altfel apăsați **Cumpără credite**).

   ![Serviciul ANAF SPV Token activat, cu Cod serviciu anaf_token și Credite rămase evidențiate](static/description/02_serviciu_anaf_spv_token.png)

4. Pe pagina de autorizare, titularul certificatului digital se autentifică la ANAF. Serverul
   Terrabit trimite apoi tokenul în Odoo. Fără credite suficiente, serverul refuză autorizarea cu
   „Not enough credits”, înainte de alegerea certificatului: cumpărați credite din
   **Servicii și credite** și reluați autorizarea. Autorizarea taxată apare în
   **Setări → Credite Terrabit → Consum credite** ca „ANAF authorization”, cu 1 credit.

5. Reîncărcați **Setări → Facturare**: ID Client, Secret Client, tokenurile și datele de expirare
   sunt completate pe firmă. Verificați că data de expirare a tokenului de acces e în viitor.

   ![Blocul E-Factura România cu tokenul primit și datele de expirare evidențiate](static/description/03_setari_token_primit.png)

6. Opțional, în modul dezvoltator: regula de automatizare **ANAF: token SPV de la Terrabit**
   (**Setări → Tehnic → Automatizare → Regulă de automatizare**) primește tokenul pe un URL secret.
   Nu apăsați **Reînnoire** lângă URL și lăsați **Înregistrare apeluri** oprit.

   ![Regula de automatizare cu declanșatorul Pe webhook și URL-ul secret evidențiate](static/description/04_automatizare_webhook.png)

7. Odată primit tokenul, acțiunea planificată **E-Factura: Reîmprospătare token de acces** se
   oprește: tokenul îl reînnoiește serverul Terrabit.

   ![Acțiunea planificată E-Factura: Reîmprospătare token de acces cu comutatorul Activ oprit](static/description/05_cron_reinnoire_oprit.png)

La dezinstalarea modulului, reporniți manual acțiunea planificată de reîmprospătare
(**Setări → Tehnic → Automatizare → Acțiuni planificate**, filtrul **Arhivat**) sau generați un token cu butonul
standard.
