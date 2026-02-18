import folium
import pandas as pd

# --- KONFIGURACIJA ---
ULAZNI_FAJL = "nekretnine_ns_geo.csv"
IZLAZNI_FAJL = "mapa_nekretnina_ns.html"

# Centar Novog Sada (da mapa zna gde da se fokusira na početku)
NS_KOORDINATE = [45.25167, 19.83694]


def get_marker_color(cena_po_m2):
    """Određuje boju markera na osnovu cene po kvadratu."""
    if cena_po_m2 < 1800:
        return 'green'  # Povoljno
    elif cena_po_m2 < 2500:
        return 'orange'  # Srednja klasa
    else:
        return 'red'  # Skupo / Luksuz


def main():
    print("Učitavam podatke...")
    try:
        df = pd.read_csv(ULAZNI_FAJL)
    except FileNotFoundError:
        print(f"Nema fajla {ULAZNI_FAJL}! Prvo pokreni geokodiranje.")
        return

    # Čišćenje podataka (samo oni sa koordinatama i cenom)
    df = df.dropna(subset=['Latitude', 'Longitude', 'Cena_EUR', 'Kvadratura_m2'])

    # Kreiramo osnovnu mapu
    mapa = folium.Map(location=NS_KOORDINATE, zoom_start=13, tiles="OpenStreetMap")

    print(f"Dodajem {len(df)} stanova na mapu...")

    for index, row in df.iterrows():
        # Izračunavamo cenu po kvadratu
        cena_m2 = row['Cena_EUR'] / row['Kvadratura_m2']

        # Pripremamo tekst za popup (HTML format)
        popup_text = f"""
        <div style="width: 200px">
            <h4>{row['Deo_Grada']}</h4>
            <b>Cena:</b> {row['Cena_EUR']:,.0f} EUR<br>
            <b>Kvadratura:</b> {row['Kvadratura_m2']} m²<br>
            <b>Cena po m²:</b> {cena_m2:,.0f} EUR<br>
        </div>
        """

        # Dodajemo marker
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=f"{row['Deo_Grada']} ({row['Cena_EUR']}€)",
            icon=folium.Icon(color=get_marker_color(cena_m2), icon="home", prefix="fa")
        ).add_to(mapa)

    # Dodajemo legendu (mali trik sa HTML-om u mapi)
    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 150px; height: 130px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white; opacity: 0.9; padding: 10px;">
     <b>Legenda (Cena/m²)</b><br>
     <i style="background:green; width:10px; height:10px; display:inline-block;"></i> < 1.800 €<br>
     <i style="background:orange; width:10px; height:10px; display:inline-block;"></i> 1.800 - 2.500 €<br>
     <i style="background:red; width:10px; height:10px; display:inline-block;"></i> > 2.500 €
     </div>
     '''
    mapa.get_root().html.add_child(folium.Element(legend_html))

    # Čuvanje mape
    mapa.save(IZLAZNI_FAJL)
    print(f"Uspeh! Mapa je sačuvana kao '{IZLAZNI_FAJL}'.")
    print("Otvori taj fajl u svom internet pregledaču (Chrome, Firefox...).")


if __name__ == "__main__":
    main()