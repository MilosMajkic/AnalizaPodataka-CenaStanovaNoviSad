import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# --- KONFIGURACIJA ---
ULAZNI_FAJL = "nekretnine_ns_geo.csv"


def main():
    # 1. Učitavanje podataka
    print("Učitavam podatke...")
    try:
        df = pd.read_csv(ULAZNI_FAJL)
    except FileNotFoundError:
        print(f"Nema fajla {ULAZNI_FAJL}! Prvo pokreni geokodiranje.")
        return

    # 2. Čišćenje podataka
    # Izbacujemo redove gde nemamo koordinate ili cenu
    initial_len = len(df)
    df = df.dropna(subset=['Latitude', 'Longitude', 'Cena_EUR', 'Kvadratura_m2'])
    print(f"Obrisano {initial_len - len(df)} redova zbog nedostajućih podataka.")

    # Opciono: Izbacivanje ekstremnih vrednosti (npr. greške u unosu, stanovi od 1€)
    df = df[df['Cena_EUR'] > 10000]

    # 3. Priprema za ML
    # X su ulazni podaci (Kvadratura, Lat, Lon, Deo Grada)
    # y je ono što predviđamo (Cena)

    # "One-Hot Encoding": Pretvaramo "Deo_Grada" u kolone npr. "Deo_Grada_Grbavica" (0 ili 1)
    # Ovo pomaže modelu da razume koliko lokacija utiče na cenu.
    X = df[['Kvadratura_m2', 'Latitude', 'Longitude', 'Deo_Grada']]
    X = pd.get_dummies(X, columns=['Deo_Grada'], drop_first=True)

    y = df['Cena_EUR']

    # 4. Podela na Trening i Test set (80% učimo, 20% testiramo)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"\nTreniram model na {len(X_train)} stanova...")

    # 5. Kreiranje i treniranje modela (Random Forest)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("Model je istreniran! Testiram na neviđenim podacima...")

    # 6. Evaluacija (Testiranje)
    predikcije = model.predict(X_test)

    # Koliko prosečno grešimo u eurima?
    mae = mean_absolute_error(y_test, predikcije)
    # Koliko dobro model "objašnjava" varijaciju cena (od 0 do 1, gde je 1 savršeno)
    r2 = r2_score(y_test, predikcije)

    print(f"\n--- REZULTATI ---")
    print(f"Prosečna greška (MAE): {mae:,.0f} EUR")
    print(f"Preciznost modela (R2 Score): {r2:.2f} (što bliže 1.0 to bolje)")

    # 7. Primeri predviđanja
    print("\n--- PRIMERI IZ TEST SETA (Stvarno vs Predviđeno) ---")
    results = pd.DataFrame({'Stvarna Cena': y_test, 'Predviđena': predikcije})
    results['Razlika'] = results['Stvarna Cena'] - results['Predviđena']
    print(results.head(5))

    # --- BONUS: Koje osobine su najvažnije za cenu? ---
    print("\n--- ŠTA NAJVIŠE UTIČE NA CENU? ---")
    feature_importances = pd.Series(model.feature_importances_, index=X.columns)
    print(feature_importances.nlargest(5))


if __name__ == "__main__":
    main()