import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# --- KONFIGURACIJA ---
ULAZNI_FAJL = "nekretnine_ns_final.csv"
IZLAZNI_FAJL = "nekretnine_ns_geo.csv"
GRAD = "Novi Sad"


def main():
    print(f"Učitavam podatke iz {ULAZNI_FAJL}...")
    try:
        df = pd.read_csv(ULAZNI_FAJL)
    except FileNotFoundError:
        print(f"GREŠKA: Nije pronađen fajl '{ULAZNI_FAJL}'. Proveri da li je u istom folderu.")
        return

    print(f"Učitano {len(df)} redova.")

    # Inicijalizacija geolokatora (Moraš staviti svoj user_agent, bilo šta jedinstveno)
    geolocator = Nominatim(user_agent="moj_nekretnine_projekt_v1")

    # RateLimiter je bitan da nas servis ne blokira (min 1 sekunda pauze)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

    # Pravimo punu adresu za pretragu kako bi bila preciznija
    # Ako u koloni 'Deo_Grada' piše samo 'Grbavica', dodajemo ', Novi Sad, Srbija'
    df['Puna_Adresa'] = df['Deo_Grada'] + ', ' + GRAD + ', Srbija'

    print("Počinjem geokodiranje... Ovo može potrajati (oko 1-2 sekunde po oglasu).")

    # --- GLAVNA MAGIJA ---
    # Kreiramo novu kolonu 'location' koja sadrži ceo objekat sa koordinatama
    # Koristimo progress bar ako je moguće, ili samo ispisujemo

    locations = []
    total = len(df)

    for index, row in df.iterrows():
        address = row['Puna_Adresa']
        try:
            loc = geocode(address)
            if loc:
                locations.append((loc.latitude, loc.longitude))
                print(f"[{index + 1}/{total}] Nađeno: {address} -> {loc.latitude}, {loc.longitude}")
            else:
                locations.append((None, None))
                print(f"[{index + 1}/{total}] Nije nađeno: {address}")
        except Exception as e:
            print(f"Greška na {address}: {e}")
            locations.append((None, None))

    # Dodavanje koordinata u DataFrame
    df['Latitude'], df['Longitude'] = zip(*locations)

    # Čišćenje: brišemo one gde nismo našli koordinate (opciono)
    broj_bez_lokacije = df['Latitude'].isna().sum()
    print(f"\nZavršeno! Nisam uspeo da lociram {broj_bez_lokacije} stanova.")

    # Čuvamo samo validne ili sve (ovde čuvamo sve)
    df.to_csv(IZLAZNI_FAJL, index=False)
    print(f"Geokodirani podaci sačuvani u '{IZLAZNI_FAJL}'.")

    # Prikaz prvih nekoliko redova
    print(df[['Deo_Grada', 'Latitude', 'Longitude']].head())


if __name__ == "__main__":
    main()