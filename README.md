# Refroidisseur Clinker - Tableau de Bord Django

Ce projet est une application web développée avec **Django** qui permet de suivre, analyser et visualiser les mesures du refroidisseur de clinker dans une cimenterie. Il offre une interface conviviale pour enregistrer les données, générer des graphiques dynamiques, exporter les résultats (PDF/Excel), et stocker des images liées à chaque mesure.

## 🚀 Fonctionnalités principales

- 📊 Calcul automatique des débits d'air par chambre
- 📈 Génération de graphiques (débit ventilateurs, flow spécifique, air load, heatmap)
- 🗃️ Enregistrement et historique des mesures
- 🖼️ Ajout et affichage d’images liées à chaque mesure
- 🧾 Export des résultats en PDF et Excel
- 🔎 Recherche par date, ID ou commentaire

## 🛠️ Technologies utilisées

- Python 3.12
- Django 5.1
- Matplotlib (pour les graphes)
- SQLite (base de données locale)
- HTML/CSS + Bootstrap 5
- xhtml2pdf (export PDF)

## 📂 Structure du projet

refroidisseur_project/ │ ├── refroidisseur_app/ │ ├── models.py # Modèles : Mesure, VentilateurMesure, ResultatCalcul, Image │ ├── views.py # Logique des vues │ ├── templates/ # Fichiers HTML (index, détails, liste, PDF) │ └── static/ # CSS/JS statique (optionnel) │ ├── media/ # Dossier pour stocker les images et Excel ├── db.sqlite3 # Base de données locale ├── manage.py # Commandes Django └── requirements.txt # Dépendances Python


## ▶️ Lancer le projet localement

```bash
git clone https://github.com/elothamni1993/refroidisseur_project.git
cd refroidisseur_project
pip install -r requirements.txt

# Créer la base de données et les tables
python manage.py makemigrations
python manage.py migrate

# Démarrer le serveur
python manage.py runserver
