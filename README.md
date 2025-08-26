

# VIACAREME – Backend (Django REST Framework)

Backend de la solution **VIACAREME**, un système de gestion des dossiers médicaux des femmes enceintes, conçu pour centraliser et sécuriser les données médicales.

## 🚀 Fonctionnalités principales

* Gestion des hôpitaux et des médecins
* Enregistrement et suivi des patientes
* Gestion des cartes à puce (RFID) pour l’identification sécurisée
* Consultations médicales et rendez-vous
* Accès temporaire aux données via code sécurisé
* Authentification et rôles (SuperAdmin, Gestionnaire, Médecin, Patiente)

## 🛠️ Stack technique

* **Backend** : Django + Django REST Framework
* **Base de données** : PostgreSQL
* **Authentification** : JWT (JSON Web Token)
* **Déploiement** : Render (hébergement cloud)

## 📂 Structure du projet

```
viacareme-backend/
│── viacareme/         # Configuration Django
│── apps/              # Applications (auth, hôpitaux, patientes, etc.)
│── requirements.txt   # Dépendances
│── manage.py
```

## ⚙️ Installation locale

```bash
# Cloner le repo
git clone https://github.com/TON-ORGANISATION/viacareme-backend.git
cd viacareme-backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Lancer le serveur
python manage.py runserver
```

## 🔑 Authentification

* Login via email + mot de passe
* JWT (access & refresh tokens)
* Permissions basées sur les rôles (SuperAdmin, Gestionnaire, Médecin, Patiente)


