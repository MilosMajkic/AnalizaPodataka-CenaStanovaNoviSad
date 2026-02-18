import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("nekretnine_ns_final.csv")

# Primer 1: Histogram cena po kvadratu
plt.figure(figsize=(10, 6))
sns.histplot(df['Cena_po_m2'], bins=30, kde=True)
plt.title("Distribucija cena kvadrata u Novom Sadu")
plt.show()

# Primer 2: Koja lokacija je najskuplja?
top_lokacije = df.groupby('Deo_Grada')['Cena_po_m2'].mean().sort_values(ascending=False).head(10)
print(top_lokacije)