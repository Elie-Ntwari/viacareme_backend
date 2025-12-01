# VIACAREME – Backend (Django REST Framework)

Backend de la solution **VIACAREME**, un système de gestion des dossiers médicaux des femmes enceintes, conçu pour centraliser et sécuriser les données médicales.

## 🚀 Fonctionnalités principales

- Gestion des hôpitaux et des médecins
- Enregistrement et suivi des patientes
- Gestion des cartes à puce (RFID) pour l'identification sécurisée
- Consultations médicales et rendez-vous
- Gestion des grossesses et clôture de dossiers
- Accès temporaire aux données via code OTP sécurisé
- Envoi de SMS pour notifications
- Authentification et rôles (SuperAdmin, Gestionnaire, Médecin, Patiente)

## 🛠️ Stack technique

- **Backend** : Django + Django REST Framework
- **Base de données** : PostgreSQL
- **Authentification** : JWT (JSON Web Token)
- **Hébergement** : AWS (Amazon Web Services)
- **API Base URL** : https://api.viacareme.com/api/

## 📂 Structure du projet

```
viacareme_backend/
│── jali_django_api/        # Configuration Django principale
│── auth_module/            # Authentification et gestion des utilisateurs
│── hospital_module/        # Gestion des hôpitaux
│── medical_module/         # Gestion des médecins
│── patiente__module/       # Gestion des patientes
│── consultation_module/    # Consultations médicales
│── grossesse_module/       # Suivi des grossesses
│── cards_module/           # Gestion des cartes RFID
│── sms_sender/             # Envoi de SMS
│── requirements.txt        # Dépendances Python
│── manage.py               # Script de gestion Django
```

## 🌐 API en Production

L'API est hébergée sur **AWS** et accessible à l'adresse suivante :

**Base URL** : `https://api.viacareme.com/api/`

### Endpoints principaux

- **Authentification** : `/auth/`
  - Login, logout, refresh token
- **Hôpitaux** : `/hospitals/`
  - CRUD des hôpitaux et zones de santé
- **Médecins** : `/medecins/`
  - Gestion des médecins et leurs affectations
- **Patientes** : `/patientes/`
  - Enregistrement et suivi des patientes
- **Consultations** : `/consultations/`
  - Gestion des consultations médicales
- **Grossesses** : `/grossesses/`
  - Suivi des grossesses et clôture de dossiers
- **Cartes RFID** : `/cards/`
  - Attribution et gestion des cartes à puce
- **SMS** : `/sms/`
  - Envoi de notifications par SMS

## 🧪 Tester l'API avec Postman

Une collection Postman complète est disponible avec tous les endpoints et exemples de requêtes :

**[📦 Collection Postman VIACAREME](https://www.postman.com/zigi77-5461/viacareme/collection/33722566-854fff4b-c2d4-44c2-8f77-78644ca8ad16?action=share&source=copy-link&creator=33722566)**

### 🔐 Guide de test rapide

1. **Ouvrir la collection Postman** via le lien ci-dessus
2. **Naviguer vers** `auth_module` → `LOGIN`
3. **Vérifier l'URL** : Assurez-vous que l'URL est `https://api.viacareme.com/api/auth/login/` (et non localhost)
4. **Lancer la requête** avec les credentials fournis dans le body :

   ```json
   {
     "email": "docteur@hopital.cd",
     "password": "1234567890"
   }
   ```

   _(Autres rôles disponibles en commentaire : Admin, Gestionnaire)_

5. **Copier le token** : Dans la réponse, récupérer la valeur de `access_token`

6. **Tester d'autres endpoints** :
   - Aller dans un autre module (ex: `consultation_module`)
   - Sélectionner une requête (ex: `patientes medecin full info`)
   - Dans l'onglet **Authorization** :
     - Type : `Bearer Token`
     - Token : Coller le `access_token` obtenu
   - Lancer la requête

### 📋 Exemples de requêtes disponibles

La collection Postman contient des exemples pour :

- ✅ Authentification (login, logout, refresh)
- 🏥 Gestion des hôpitaux
- 👨‍⚕️ Gestion des médecins
- 🤰 Gestion des patientes
- 📋 Consultations médicales
- 🤱 Suivi des grossesses
- 💳 Attribution de cartes RFID
- 📱 Envoi de SMS

## ⚙️ Installation locale

```bash
# Cloner le repo
git clone https://github.com/TON-ORGANISATION/viacareme-backend.git
cd viacareme-backend

# Créer un environnement virtuel
python -m venv venv
# Activer environnement sur Windows:
venv\Scripts\activate
# Activer environnement sur Linux
source venv/bin/activate 

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## 🔑 Authentification

- **Login** via email + mot de passe
- **JWT** (access & refresh tokens)
- **Permissions** basées sur les rôles :
  - **SuperAdmin** : Accès complet au système
  - **Gestionnaire** : Gestion des hôpitaux et médecins
  - **Médecin** : Consultation et suivi des patientes
  - **Patiente** : Accès à son propre dossier médical

## 🔒 Sécurité

- Authentification JWT avec tokens d'accès et de rafraîchissement
- Codes OTP temporaires pour accès sécurisé aux dossiers
- Gestion des permissions par rôle
- Chiffrement des données sensibles
- Audit trail pour toutes les actions critiques

## 📝 Documentation API

Pour une documentation complète de l'API, consultez la collection Postman qui contient :

- Tous les endpoints disponibles
- Exemples de requêtes et réponses
- Structure JSON attendue
- Codes d'erreur et leur signification



## 📧 Contact

Pour toute question ou support, contactez l'équipe VIACAREME.

- site web : `https://viacareme.com/`
- mail : `mablaferawi@gmail.com`
- téléphone : `+243 813 308 078`
---


**© 2024 VIACAREME - Tous droits réservés**
