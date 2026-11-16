Modulul are nevoie de biblioteca Python `pdfminer.six`, trecută în `requirements.txt` al repo-ului.

Versiunile recente de `pdfminer.six` cer `cryptography>=36`. Pe un server cu `cryptography` mai
veche (de exemplu 3.4.8, din pachetele Ubuntu 22.04), `pip install pdfminer.six` actualizează
`cryptography`, iar pyOpenSSL-ul existent nu mai pornește odată cu ea: Odoo se oprește cu
`module 'lib' has no attribute 'GEN_EMAIL'`. Pe un astfel de server, păstrați versiunea instalată:

```bash
pip install pdfminer.six "cryptography==$(pip show cryptography | awk '/^Version/ {print $2}')"
```

`pip` alege atunci o versiune de `pdfminer.six` compatibilă. Modulul a fost verificat pe
`pdfminer.six` 20220319 și 20260107, cu aceleași rezultate.
