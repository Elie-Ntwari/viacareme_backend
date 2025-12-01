
# VIACAREME – Backend (Django REST Framework)

Backend officiel de **VIACAREME**, une plateforme de gestion des dossiers médicaux des femmes enceintes permettant la centralisation, la sécurité et l’analyse intelligente des données médicales.
Cette version inclut désormais un **module d’Intelligence Artificielle dédié à la santé maternelle**.

---

## 🚀 Fonctionnalités principales

* Gestion des hôpitaux et des médecins
* Enregistrement et suivi des patientes
* Gestion des cartes à puce (RFID)
* Consultations médicales et rendez-vous
* Gestion des grossesses et clôture de dossiers
* Accès temporaire via OTP sécurisé
* Envoi de SMS
* Authentification et rôles (SuperAdmin, Gestionnaire, Médecin, Patiente)
* ** Module IA**

  * Chatbot de bien-être (conseils non médicaux)
  * Prédiction du risque de santé maternelle (Faible / Moyen / Élevé)
  * Analyse explicative des facteurs de risque
  * Génération de graphique d'évolution du risque

---

## 🛠️ Stack technique

* **Backend** : Django + DRF
* **Base de données** : PostgreSQL
* **Auth** : JWT
* **IA/ML** : modèle scikit-learn sérialisé (`maternal_health.pkl`)
* **Hébergement** : AWS
* **API Base URL** : [https://api.viacareme.com/api/](https://api.viacareme.com/api/)

---

## 📂 Structure du projet

```
viacareme_backend/
│── jali_django_api/         # Configuration Django
│── auth_module/             # Authentification & utilisateurs
│── hospital_module/         # Hôpitaux et zones de santé
│── medical_module/          # Médecins
│── patiente_module/         # Patientes
│── consultation_module/     # Consultations
│── grossesse_module/        # Grossesses
│── cards_module/            # Cartes RFID
│── sms_sender/              # Notifications SMS
│── modele_ia/               # MODULE IA 
│── requirements.txt
│── manage.py
```

---

# 🧠 Module IA – Présentation

L'application inclut désormais un module `modele_ia` offrant **deux services intelligents** :

---

## 1️⃣ 💬 Chatbot de Bien-Être

**Endpoint :** `api/chatbot/`

Un chatbot conçu pour accompagner les femmes enceintes avec des **conseils non médicaux** :

* Gestion du stress
* Bien-être émotionnel
* Activité physique légère
* Conseils généraux de prévention

**Contraintes éthiques & sécurité :**

* ❌ **Aucune recommandation médicale, aucun médicament**
* ❌ **Aucun diagnostic médical**
* ✔️ Le bot oriente toujours la patiente vers un médecin en cas de symptômes

---

## 2️⃣ 🔬 Prédiction du Risque de Santé Maternelle

**Endpoint :** `api/predict/`

Un outil d’aide à la décision pour les médecins.

### Fonctionnalités :

* Analyse automatique des données des visites
* Classification du risque : **Faible / Moyen / Élevé**
* Explication du facteur principal ayant influencé la prédiction
* Génération d’un graphique montrant l’évolution du risque au fil du temps

### Variables utilisées :

| Variable            | Description                     | Unité         |
| ------------------- | ------------------------------- | ------------- |
| Âge                 | Âge de la patiente              | années        |
| BP Sys              | Pression artérielle systolique  | mmHg          |
| BP Dia              | Pression artérielle diastolique | mmHg          |
| Glycémie (BGS)      | Taux de sucre                   | g/L ou mmol/L |
| Température         | Température corporelle          | °F            |
| Fréquence cardiaque | Battement/min                   | bpm           |

### Fichiers inclus :

* **maternal_health.pkl** : modèle ML entraîné
* **Maternal Health Risk Data Set.csv** : dataset de référence

---

## ⚙️ Installation locale

*(inchangé, juste propre)*

```bash
git clone https://github.com/TON-ORGANISATION/viacareme-backend.git
cd viacareme-backend

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🔑 Authentification (JWT)

* Login via email + mot de passe
* Access / Refresh tokens
* Permissions selon rôles (SuperAdmin, Gestionnaire, Médecin, Patiente)

---

## 🌐 API en Production

Base URL : `https://api.viacareme.com/api/`

### Modules principaux :

* `/auth/` – Authentification
* `/hospitals/` – Hôpitaux
* `/medecins/` – Médecins
* `/patientes/` – Patientes
* `/consultations/` – Consultations
* `/grossesses/` – Grossesses
* `/cards/` – Cartes RFID
* `/sms/` – SMS
* **`/chatbot/` – Chatbot IA**
* **`/predict/` – Prédiction de risque**

---

## 🧪 Tester avec Postman

Collection complète :
👉 **[https://www.postman.com/zigi77-5461/viacareme/](https://www.postman.com/zigi77-5461/viacareme/)...**

*(section inchangée)*

---

## 🔒 Sécurité

* Auth JWT
* Permissions par rôle
* OTP sécurisé
* Chiffrement des données sensibles
* Contraintes IA strictes (pas de médecine)
* Audit des actions sensibles

---

## 📧 Contact

* Site : [https://viacareme.com](https://viacareme.com)
* Email : [mablaferawi@gmail.com](mailto:mablaferawi@gmail.com)
* Téléphone : +243 813 308 078

---

## © 2024 VIACAREME – Tous droits réservés

