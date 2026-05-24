# 🌿 SphagnumPipeline

Pipeline de données de biodiversité centré sur la famille **Sphagnaceae** (sphaignes),
construit à partir des données open source [GBIF](https://www.gbif.org/).

Le projet couvre l'ensemble de la chaîne Data Engineering : ingestion d'un fichier brut
d'1,1 Go, nettoyage et validation des coordonnées géographiques, puis exposition
des résultats sous forme de cartes interactives et de tableaux statistiques.

---

## Contexte scientifique

Les sphaignes sont des mousses formant les tourbières, qui sont des écosystèmes jouant un rôle
clé dans le stockage du carbone et la régulation hydrologique. Leur distribution
géographique est un indicateur de la santé des milieux humides.

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
│   ├── explore.py              # Script d'exploration
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
## Données

Les données ne sont pas versionnées (fichier > 1 Go).

Télécharger l'export GBIF utilisé dans ce projet :
👉 [Sphagnaceae — GBIF Occurrence Download](https://www.gbif.org/fr/occurrence/download?continent=EUROPE&taxon_key=4673&occurrence_status=present)

Filtres appliqués :
- Famille : *Sphagnaceae*
- Format : Darwin Core Archive (DwC-A)

Placer le fichier `occurrence.txt` dans le dossier `data/`.
---

## Installation

```bash
git clone https://github.com/Gwendal-M/SphagnumPipeline.git
cd SphagnumPipeline
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Placer le fichier `occurrence.txt` exporté depuis GBIF dans le dossier `data/`.

---

## Utilisation

```bash
# Test rapide — 100 000 lignes
python scripts/pipeline.py --sample 1000000

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

## Démarche

Le projet a été construit de façon itérative en plusieurs phases :

1. **Exploration** — chargement d'un échantillon de 5 puis 100 000 lignes
   pour comprendre la structure du fichier DwC-A (230 colonnes, format TSV),
   identifier les colonnes utiles et mesurer la qualité des données

2. **Nettoyage** — validation des coordonnées GPS (suppression des NaN,
   des valeurs hors plage et de l'artefact GBIF (0,0)),
   95,7% de données exploitables conservées

3. **Pipeline** — consolidation de toutes les étapes en un script unique
   `pipeline.py` avec chargement par chunks pour gérer le fichier d'1,1 Go
   sans saturer la RAM

4. **Visualisation** — génération de deux heatmaps (Europe / France)
   et d'une page de statistiques interactives triables par espèce, pays et ordre

Le dossier `exploration/` conserve les scripts et notes de la phase de découverte,
séparés du pipeline de production.

---

## Résultats

Sur 939,520 occurrences chargées :

- **838 075** coordonnées GPS valides (89,2 %)
- **95** espèces identifiées au niveau spécifique
- **101 445** lignes écartées (coordonnées manquantes ou invalides)

---

## Source des données

- **GBIF** — Global Biodiversity Information Facility
- Famille : *Sphagnaceae*
- Licence : [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Export : [gbif.org/occurrence/download](https://www.gbif.org/occurrence/download)

## Licence

Code sous licence [MIT](https://opensource.org/licenses/MIT) — © 2026 Gwendal-M
