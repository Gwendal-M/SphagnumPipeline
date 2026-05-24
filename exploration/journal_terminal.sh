# Journal de bord — Terminal Git Bash
# Projet : SphagnumPipeline
# Date   : 22/05/2026


# 1. Environnement


python --version
# Python 3.14.5


# 2. Création du projet


mkdir SphagnumPipeline
cd SphagnumPipeline

# Création de l'environnement virtuel
python -m venv .venv
source .venv/Scripts/activate
# si (.venv) environnement actif

# Création de la structure de dossiers
mkdir data exploration scripts outputs

# Création des fichiers de base
touch README.md requirements.txt .gitignore
touch src/main.py


# 3. Installation des dépendances


pip install pandas folium
# pandas 3.0.3, folium 0.20.0, numpy 2.4.6

pip install requests sqlalchemy psycopg2-binary
# sqlalchemy 2.0.49, psycopg2-binary 2.9.12

pip install matplotlib
# matplotlib 3.10.9

# Vérif installation
python -c "import pandas; import folium; print('OK')"

# Sauvegarde des versions dans requirements.txt
pip freeze > requirements.txt


# 4. Initialisation Git


git init
git status
git add .
git commit -m "Initial Sphagnum project setup"


# 5. Lancement de python

python
exit()


# NOTE — Commandes utiles à retenir


# Activer l'environnement virtuel (à faire à chaque nouvelle session)
source .venv/Scripts/activate

# Se placer à la racine du projet (syntaxe Git Bash)
cd /c/Users/progw/SphagnumPipeline

# Lancer le pipeline principal
python scripts/pipeline.py --sample 100000

# Sauvegarder les nouvelles dépendances
pip freeze > requirements.txt

# Voir l'état Git
git status

# Commiter les modifications
git add .
git commit -m "description du changement"

# Créer un script
touch dossier/script.py

# Ouvrir un fichier pour modification sur visual studio code
code dossier/script.py