## 19.0.1.0.0

- Prima versiune: varianta fără Python a modulului `terrabit_iap_anaf`, importabilă pe Odoo Online.
  Tokenul vine de la serverul Terrabit pe o automatizare *On webhook* (în locul rutei
  `/iap/anaf_token_response`), care oprește și acțiunea programată de reînnoire e-Factura; butonul
  Generează token (Terrabit) trimite adresa acestui webhook în linkul de autorizare. O autorizare
  costă 1 credit și apare în *Consum credite*. Necesită `terrabit_iap_server_anaf` 19.0.1.5.0 pe
  server și `deltatech_iap_online` 19.0.1.2.0.
