import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# --- UČITAVANJE I PRIPREMA (Isto kao malopre) ---
df = pd.read_csv("nekretnine_ns_geo.csv")
df = df.dropna(subset=['Latitude', 'Longitude', 'Cena_EUR', 'Kvadratura_m2'])
df = df[df['Cena_EUR'] > 10000]

X = df[['Kvadratura_m2', 'Latitude', 'Longitude', 'Deo_Grada']]
X = pd.get_dummies(X, columns=['Deo_Grada'], drop_first=True)
y = df['Cena_EUR']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
predikcije = model.predict(X_test)

# --- VIZUELIZACIJA ---
plt.figure(figsize=(15, 6))

# GRAFIKON 1: Stvarna vs Predviđena cena
plt.subplot(1, 2, 1)
sns.scatterplot(x=y_test, y=predikcije, color='blue', alpha=0.6)
# Idealna linija (gde bi tačkice bile da je model savršen)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel("Stvarna Cena (EUR)")
plt.ylabel("Predviđena Cena (EUR)")
plt.title(f"Preciznost Modela (R2: {model.score(X_test, y_test):.2f})")
plt.grid(True)

# GRAFIKON 2: Šta najviše utiče na cenu?
plt.subplot(1, 2, 2)
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)
sns.barplot(x=importances, y=importances.index, palette="viridis")
plt.xlabel("Uticaj na cenu (0-1)")
plt.title("Top faktori koji određuju cenu")

plt.tight_layout()
plt.show()