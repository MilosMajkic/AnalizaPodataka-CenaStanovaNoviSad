import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# --- KONFIGURACIJA ---
BASE_URL = "https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/grad/novi-sad/"
# Stavićemo samo 1 stranicu za testiranje dok ne proradi
BROJ_STRANICA = 1
HEADERS = {
    # Koristimo noviji User-Agent da izgledamo kao pravi pregledač
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,sr;q=0.8",
    "Referer": "https://www.google.com/"
}


def parsiraj_stranicu(url):
    print(f"Preuzimam: {url}")
    time.sleep(random.uniform(2, 4))  # Malo duža pauza

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"Greška u konekciji: {e}")
        return []

    print(f"Status koda: {response.status_code}")  # 200 je OK, 403 je Zabranjeno

    if response.status_code != 200:
        print("Sajt je odbio zahtev! Verovatno blokira botove.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- DEBUG SEKCIJA ---
    # Ovo će sačuvati ono što skripta "vidi" u fajl, da možemo da proverimo
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Sačuvao sam HTML stranice u 'debug_page.html'. Proveri taj fajl ako nema rezultata.")
    # ---------------------

    # Pokušavamo da nađemo oglase. Nekretnine.rs obično koristi klasu 'offer-body' ili 'row offer'
    # Probaćemo širu pretragu
    oglasi = soup.find_all('div', class_='offer-body')

    if not oglasi:
        print("UPOZORENJE: Nisam našao nijedan div sa klasom 'offer-body'. Pokušavam alternativni selektor...")
        oglasi = soup.find_all('div', class_='row offer')

    print(f"Broj potencijalnih oglasa na stranici: {len(oglasi)}")

    podaci_sa_stranice = []

    for oglas in oglasi:
        try:
            # Naslov
            naslov_tag = oglas.find('h2', class_='offer-title')
            # Ako ne nađe u h2, probaj u a tagu direktno
            if not naslov_tag:
                naslov_tag = oglas.find('a', class_='offer-title')

            naslov = naslov_tag.get_text(strip=True) if naslov_tag else "N/A"
            link = "https://www.nekretnine.rs" + naslov_tag.find('a')['href'] if naslov_tag and naslov_tag.find(
                'a') else "N/A"

            # Lokacija
            lokacija_tag = oglas.find('p', class_='offer-location')
            lokacija = lokacija_tag.get_text(strip=True) if lokacija_tag else "N/A"

            # Cena
            cena_tag = oglas.find('p', class_='offer-price')
            cena = None
            if cena_tag:
                raw_cena = cena_tag.get_text(strip=True).replace("EUR", "").replace(" ", "").replace(".", "")
                # Često piše "Dogovor", to preskačemo
                if any(char.isdigit() for char in raw_cena):
                    # Izvuci samo brojeve
                    import re
                    brojevi = re.findall(r'\d+', raw_cena)
                    if brojevi:
                        cena = int(''.join(brojevi))

            # Kvadratura
            kvadratura = None
            meta_info = oglas.find('div', class_='offer-meta-info')
            if meta_info:
                tekst = meta_info.get_text(strip=True)
                # Primer: "75 m2 | 3.0 sobe"
                delovi = tekst.split('|')
                for deo in delovi:
                    if 'm2' in deo:
                        kv_raw = deo.replace('m2', '').strip().replace(',', '.')
                        try:
                            kvadratura = float(kv_raw)
                        except:
                            pass

            if cena and kvadratura:
                podaci_sa_stranice.append({
                    'Naslov': naslov,
                    'Lokacija': lokacija,
                    'Cena_EUR': cena,
                    'Kvadratura_m2': kvadratura,
                    'Link': link
                })

        except Exception as e:
            continue

    return podaci_sa_stranice


def main():
    print(f"Počinjem prikupljanje podataka sa {BASE_URL}...")
    svi_stanovi = []

    for i in range(1, BROJ_STRANICA + 1):
        url = f"{BASE_URL}?p={i}"
        print(f"Obrađujem stranicu {i}...")
        novi_podaci = parsiraj_stranicu(url)
        svi_stanovi.extend(novi_podaci)
        print(f" -> Pronađeno {len(novi_podaci)} validnih stanova.")

    # --- GLAVNA POPRAVKA: Provera da li ima podataka pre pravljenja DataFrame-a ---
    if not svi_stanovi:
        print("\n[GREŠKA] Nisu prikupljeni nikakvi podaci! Proveri 'debug_page.html'.")
        print("Mogući razlozi: IP blokada ili promena HTML strukture sajta.")
        return

    df = pd.DataFrame(svi_stanovi)

    # Sigurnija obrada lokacije
    try:
        df[['Grad', 'Deo_Grada']] = df['Lokacija'].str.split(',', n=1, expand=True)
    except:
        print("Upozorenje: Nisam uspeo lepo da podelim lokaciju, ostavljam original.")
        df['Deo_Grada'] = df['Lokacija']

    # Dodajemo cenu po m2
    df['Cena_po_m2'] = (df['Cena_EUR'] / df['Kvadratura_m2']).round(2)

    file_name = "nekretnine_ns_dataset.csv"
    df.to_csv(file_name, index=False, encoding='utf-8')
    print(f"\nUspešno završeno! Podaci sačuvani u '{file_name}'.")
    print(df.head())


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

# --- KONFIGURACIJA ---
BASE_URL = "https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/grad/novi-sad/"
BROJ_STRANICA = 3  # Možeš povećati na 50+ kasnije
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def parsiraj_stranicu(url):
    print(f"Preuzimam: {url}")
    time.sleep(random.uniform(1.5, 3.5))  # Pauza da budemo pristojni

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"Greška u konekciji: {e}")
        return []

    if response.status_code != 200:
        print(f"Status greška: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Glavni kontejner za svaki oglas
    oglasi = soup.find_all('div', class_='row offer')

    podaci_sa_stranice = []

    for oglas in oglasi:
        try:
            # 1. Naslov i Link
            naslov_tag = oglas.find('h2', class_='offer-title')
            naslov = "N/A"
            link = "N/A"

            if naslov_tag:
                a_tag = naslov_tag.find('a')
                if a_tag:
                    naslov = a_tag.get_text(strip=True)
                    link = "https://www.nekretnine.rs" + a_tag['href']

            # 2. Lokacija
            lokacija_tag = oglas.find('p', class_='offer-location')
            lokacija = lokacija_tag.get_text(strip=True) if lokacija_tag else "N/A"

            # 3. Cena
            # U HTML-u cena je u <p class="offer-price"><span>66 950 €</span>...</p>
            # Moramo paziti da ne uzmemo "offer-price--invert" (to je kvadratura)
            cena = None
            # Trazimo sve p tagove sa klasom offer-price, ali filtriramo onaj koji NEMA klasu invert
            cena_container = oglas.find('p', class_='offer-price')

            # Provera da li smo slučajno uhvatili kvadraturu (koja ima klasu 'offer-price--invert')
            # Klasa 'offer-price' je zajednička, ali cena je obično prva u DOM-u unutar tog bloka
            if cena_container and 'offer-price--invert' not in cena_container.get('class', []):
                span_cena = cena_container.find('span')
                if span_cena:
                    raw_cena = span_cena.get_text(strip=True)
                    # Čišćenje: skloni "€", razmake, tačke
                    clean_cena = re.sub(r'[^\d]', '', raw_cena)
                    if clean_cena:
                        cena = int(clean_cena)

            # 4. Kvadratura
            # Nalazi se u <p class="offer-price offer-price--invert"><span>34 m²</span></p>
            kvadratura = None
            kvad_container = oglas.find('p', class_='offer-price--invert')
            if kvad_container:
                span_kvad = kvad_container.find('span')
                if span_kvad:
                    raw_kvad = span_kvad.get_text(strip=True)
                    # Uzmi samo broj pre "m2"
                    clean_kvad = raw_kvad.lower().replace('m²', '').replace('m2', '').replace(' ', '').replace(',', '.')
                    try:
                        kvadratura = float(clean_kvad)
                    except:
                        pass

            # Dodajemo samo ako imamo cenu i kvadraturu (bitno za statistiku)
            if cena and kvadratura:
                podaci_sa_stranice.append({
                    'Naslov': naslov,
                    'Lokacija': lokacija,
                    'Cena_EUR': cena,
                    'Kvadratura_m2': kvadratura,
                    'Link': link
                })

        except Exception as e:
            # print(f"Greška na oglasu: {e}") # Otkomentariši za detaljniji debug
            continue

    return podaci_sa_stranice


def main():
    print(f"--- POČETAK SKRAPINGA ---")
    svi_stanovi = []

    for i in range(1, BROJ_STRANICA + 1):
        url = f"{BASE_URL}?p={i}"
        print(f"Obrađujem stranicu {i}...")
        novi_podaci = parsiraj_stranicu(url)
        svi_stanovi.extend(novi_podaci)
        print(f" -> Pronađeno {len(novi_podaci)} stanova na ovoj stranici.")

    if not svi_stanovi:
        print("\n[GREŠKA] Opet nisam našao podatke. Da li je sajt promenio strukturu?")
        return

    # Kreiranje tabele
    df = pd.DataFrame(svi_stanovi)

    # Obrada lokacije (Grad, Deo Grada)
    try:
        # Lokacija je obično: "Deo Grada, Novi Sad, Srbija"
        # Uzimamo prvi deo pre prvog zareza kao deo grada
        df['Deo_Grada'] = df['Lokacija'].apply(lambda x: x.split(',')[0].strip())
    except:
        df['Deo_Grada'] = df['Lokacija']

    # Računanje cene po m2
    df['Cena_po_m2'] = (df['Cena_EUR'] / df['Kvadratura_m2']).round(2)

    # Čuvanje
    file_name = "nekretnine_ns_final.csv"
    df.to_csv(file_name, index=False, encoding='utf-8')
    print(f"\nUspešno! Ukupno prikupljeno {len(df)} stanova.")
    print(f"Podaci sačuvani u: {file_name}")
    print("\nPrvih 5 redova:")
    print(df[['Deo_Grada', 'Cena_EUR', 'Kvadratura_m2', 'Cena_po_m2']].head())


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()