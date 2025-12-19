import requests
import re



BASE_URL = "https://www.posta-romana.ro"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def cauta_localitati(judet):
    url = BASE_URL + "/cnpr-app/modules/cauta-cod-postal/ajax/cauta_orase.php?q="
    data = {
        "k_judet": judet,
        "k_lang": "ro"
    }
    r = requests.post(url, data=data, headers=HEADERS)
    r=  r.json()   # conține HTML în câmpul "formular"
    html = r["formular"]
    return parseaza_localitati(html)


def parseaza_localitati(html):
    """
    Extrage localitatile din HTML-ul <option> returnat de Poșta Română.
    Returnează lista de dict-uri cu 'nume' și 'clasa'.
    """
    rezultate = []

    # găsim toate tag-urile <option ...>...</option>
    options = re.findall(r"<option\s+([^>]*)>(.*?)</option>", html, flags=re.DOTALL)

    for attr, text in options:
        # ignorăm primul <option> placeholder
        if "Localitate / Sector" in text:
            continue

        # extragem valoarea din value='...'
        value_match = re.search(r"value=['\"](.*?)['\"]", attr)
        valoare = value_match.group(1) if value_match else text.strip()

        # extragem clasa
        class_match = re.search(r"class=['\"](.*?)['\"]", attr)
        clasa = class_match.group(1) if class_match else ""

        rezultate.append({
            "nume": valoare,
            "clasa": clasa
        })

    return rezultate

def cauta_cod_postal_dupa_adresa(judet, localitate, adresa=""):
    url = BASE_URL + "/cnpr-app/modules/cauta-cod-postal/ajax/cautare_pentru_cod.php?q="
    data = {
        "k_adresa": adresa,
        "k_judet": judet,
        "k_localitate": localitate,
        "k_lang": "ro"
    }
    r = requests.post(url, data=data, headers=HEADERS)
    r = r.json()
    html = r["formular"]
    return parseaza_coduri_localitate_div(html)


def parseaza_coduri_localitate_div(html):
    """
    Extrage codurile poștale din HTML-ul cu div-uri <div class="cod-postal-line">.
    Returnează listă de dict-uri:
        - cod_postal
        - judet
        - localitate
        - strada
        - oficiu
    """
    rezultate = []

    # găsim toate div-urile "cod-postal-line"
    lines = re.findall(r'<div class="col-md-12 cod-postal-line">(.*?)</div>\s*</div>', html, flags=re.DOTALL)

    for line in lines:
        # găsim toate <p> și <a>
        p_tags = re.findall(r"<p>(.*?)</p>", line, flags=re.DOTALL)
        a_tags = re.findall(r"<a.*?>(.*?)</a>", line, flags=re.DOTALL)

        # construim dict
        rezultat = {
            "cod_postal": p_tags[0].strip() if len(p_tags) > 0 else "",
            "judet": p_tags[1].strip() if len(p_tags) > 1 else "",
            "localitate": p_tags[2].strip() if len(p_tags) > 2 else "",
            "strada": p_tags[3].strip() if len(p_tags) > 3 else "",
            "oficiu": a_tags[0].strip() if len(a_tags) > 0 else ""
        }

        rezultate.append(rezultat)

    return rezultate


def cauta_dupa_cod_postal(cod_postal):
    url = BASE_URL + "/cnpr-app/modules/cauta-cod-postal/ajax/cautare_cod.php?q="
    data = {
        "k_cod_postal": cod_postal,
        "k_lang": "ro"
    }
    r = requests.post(url, data=data, headers=HEADERS)
    return r.json()




# ---------------------------
# Exemple de utilizare:
# ---------------------------

print("Lista localități Bacău:")
print(cauta_localitati("BACĂU"))

print("Căutare cod poștal pentru Onesti:")
print(cauta_cod_postal_dupa_adresa("BACĂU", "Onești"))

print("Căutare după cod poștal:")
print(cauta_dupa_cod_postal("607226"))
