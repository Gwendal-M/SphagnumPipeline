# 🌿 SphagnumPipeline

Pipeline de données de biodiversité centré sur la famille **Sphagnaceae** (sphaignes),
construit à partir des données open source [GBIF](https://www.gbif.org/).

Le projet couvre l'ensemble de la chaîne Data Engineering : ingestion d'un fichier brut
d'1,1 Go, nettoyage et validation des coordonnées géographiques, puis exposition
des résultats sous forme de cartes interactives et de tableaux statistiques.

---

## Contexte scientifique

Les sphaignes sont des mousses formant les tourbières — des écosystèmes jouant un rôle
clé dans le stockage du carbone et la régulation hydrologique. Leur distribution
géographique est un indicateur de la santé des milieux humides.

Les données françaises sont volontairement peu représentées dans cet export (~21
occurrences sur 100 000) : le genre *Sphagnum* est difficile à identifier sans
formation botanique spécialisée, ce qui explique la sous-déclaration en France
comparée aux pays nordiques (Suède : ~80 000 occurrences).

---

## Stack technique

| Couche | Outils |
|---|---|
| Langage | Python 3.14 |
| Manipulation des données | pandas, numpy |
| Visualisation géospatiale | Folium, Leaflet.js |
| Visualisation exploratoire | matplotlib |
| Versioning | Git |

---

## Structure du projet

```
SphagnumPipeline/
├── data/
│   ├── occurrence.txt          # Export brut GBIF — Sphagnaceae (non versionné)
│   └── occurrence_clean.csv    # Données nettoyées (généré par le pipeline)
├── exploration/
│   ├── explore.py              # Script d'exploration — modules 2 & 3
│   ├── journal_terminal.sh     # Trace des commandes Git Bash
│   └── notes.txt               # Notes de travail
├── scripts/
│   └── pipeline.py             # Pipeline principal
├── outputs/                    # Résultats générés (non versionnés)
│   ├── heatmap_europe.html
│   ├── heatmap_france.html
│   └── stats.html
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/<ton-username>/SphagnumPipeline.git
cd SphagnumPipeline

python -m venv .venv
source .venv/Scripts/activate   # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

Placer le fichier `occurrence.txt` exporté depuis GBIF dans le dossier `data/`.

---

## Utilisation

```bash
# Test rapide — 200 000 lignes
python scripts/pipeline.py --sample 200000

# Fichier complet (~1,1 Go)
python scripts/pipeline.py
```

### Ce que le pipeline produit

| Fichier | Description |
|---|---|
| `outputs/heatmap_europe.html` | Heatmap interactive — densité d'observations en Europe |
| `outputs/heatmap_france.html` | Heatmap zoomée sur la France |
| `outputs/stats.html` | Tableaux interactifs : par espèce, par pays, par ordre |

Les fichiers `.html` s'ouvrent directement dans le navigateur, sans serveur.

---

## Résultats

Sur 100 000 occurrences chargées :

- **95 714** coordonnées GPS valides (95,7 %)
- **69** espèces identifiées au niveau spécifique
- **4 286** lignes écartées (coordonnées manquantes ou invalides)
- Répartition géographique dominée par la Scandinavie (SE, NO, FI)

---

## Source des données

- **GBIF** — Global Biodiversity Information Facility
- Famille : *Sphagnaceae*
- Licence : [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Export : [gbif.org/occurrence/download](https://www.gbif.org/occurrence/download)
