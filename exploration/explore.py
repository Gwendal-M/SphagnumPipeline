"""
Exploration des données GBIF — occurrence.txt
"""

import pandas as pd
import matplotlib.pyplot as plt

# ── Colonnes utiles ────────────────────────────────────────────────────────────
COLS = [
    "decimalLatitude", "decimalLongitude",
    "species", "family", "eventDate",
    "countryCode", "county", "occurrenceID",
    "iucnRedListCategory"
]


# 1. Structure du fichier

# Aperçu rapide — 5 lignes, toutes les colonnes
df_full = pd.read_csv("data/occurrence.txt", sep="\t", nrows=5, on_bad_lines="skip")
print(f"Nombre de colonnes : {df_full.shape[1]}")
print(f"Colonnes disponibles :\n{df_full.columns.tolist()}\n")


# 2. Chargement des colonnes utiles uniquement


df = pd.read_csv(
    "data/occurrence.txt",
    sep="\t",
    usecols=lambda c: c in COLS,
    dtype=str,
    on_bad_lines="skip",
    nrows=100_000
)

print(f"Shape : {df.shape}")
print(f"\nAperçu :\n{df.head(5)}\n")


# 3. QUALITÉ DES DONNÉES

print(f"Valeurs nulles par colonne :\n{df.isnull().sum()}\n")


# 4. Exploration taxonomique des Sphagnum


print(f"Nombre d'espèces uniques : {df['species'].nunique()}")
print(f"\nTop 10 espèces :\n{df['species'].value_counts().head(10)}\n")
print(f"Top 10 pays :\n{df['countryCode'].value_counts().head(10)}\n")


# 5. Validation des coordonnées


lat = pd.to_numeric(df["decimalLatitude"], errors="coerce")
lon = pd.to_numeric(df["decimalLongitude"], errors="coerce")

print(f"Coordonnées valides : {lat.notna().sum():,} / {len(df):,}")
print(f"\nStatistiques latitude :\n{lat.describe()}\n")
print(f"Lat hors plage : {(lat.abs() > 90).sum()}")
print(f"Coordonnées (0,0) : {((lat == 0) & (lon == 0)).sum()} lignes")


# 6. Visualisation rapide


lat = lat.dropna()
lon = pd.to_numeric(df["decimalLongitude"], errors="coerce").dropna()

plt.figure(figsize=(12, 5))
plt.scatter(lon, lat, s=0.1, alpha=0.3, color="limegreen")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title(f"Distribution spatiale — {len(lat):,} occurrences")
plt.tight_layout()
plt.savefig("outputs/exploration_coords.png", dpi=120)
plt.show()
print("✓ Carte sauvegardée → outputs/exploration_coords.png")
