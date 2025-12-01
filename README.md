#  ** Mise à Jour du Projet : Intégration de l'Intelligence Artificielle pour la Santé Maternelle **

Ce document présente les modifications ajoutées au code existant et les étapes de configuration nécessaires suite à l'intégration d'un nouveau module d'intelligence artificielle (IA) et de fonctionnalités d'assistance dans l'application.

Le travail consistait principalement à :

Ajouter des fonctionnalités d'assistance (Chatbot de bien-être).

Intégrer un modèle de Machine Learning pour la prédiction et l'analyse du risque en santé maternelle.

## 💡 ** 1. 🛠️ Étapes de Configuration et Initialisation du Module **
Cette section détaille les actions nécessaires pour initialiser le nouveau module et préparer l'environnement.

Le nouveau module modele_ia introduit deux vues principales exposant des services via des endpoints API.A. 💬 Chatbot de Bien-être et Conseils (API Endpoint: api/chatbot/ et api/predict/)Cette vue implémente un chatbot conçu pour offrir des conseils de bien-être et de l'assistance aux femmes enceintes.Objectif : Encourager le bien-être général et fournir des informations non médicales.Contrainte Éthique et Sécurité : Le modèle est strictement configuré pour NE PAS fournir de recommandations sur des médicaments ou des traitements médicaux. Son rôle est d'inciter la patiente à consulter son médecin en cas de problème de santé.B. 🔬 Vue de Prédiction du Risque de Santé MaternelleCette vue expose un service d'analyse prédictive qui sert d'Outil d'Aide à la Décision Clinique pour les professionnels de la santé.Modèle Utilisé : Un modèle de Machine Learning entraîné pour évaluer le risque de la femme enceinte (Faible, Moyen, Élevé).Fonctionnalité pour le Clinicien :Le modèle analyse les données des visites passées pour fournir une vue d'ensemble de la tendance du risque.Pour chaque prédiction de visite, des explications claires sont fournies, identifiant le facteur clé (la donnée) qui a conduit à la décision de risque.Un graphique est généré pour visualiser l'évolution du risque au fil des rendez-vous.Données d'Entrée Utilisées pour le Modèle : Le modèle utilise les données statiques (de base) et celles relevées lors de chaque visite :VariableDescriptionUnitéÂgeÂge de la patiente.AnnéesTension Systolique (BP)Pression artérielle systolique.mmHgTension Diastolique (BP)Pression artérielle diastolique.mmHgGlycémie (BGS)Taux de sucre dans le sang.g/L ou mmol/LTempérature (°F)Température corporelle.Degrés Fahrenheit (°F)Fréquence CardiaqueBattements cardiaques par minute.Bpm3. 📂 Fichiers et Intégration du ModèleFichiers du Modèle et des Données :Le module modele_ia contient le modèle entraîné sous forme de fichier sérialisé : maternal_health.pkl.Le fichier des données utilisé pour l'entraînement est également inclus à des fins de référence : Maternal Health Risk Data Set.csv.Configuration des URLs :Le module modele_ia inclut son propre fichier urls.py définissant les routes (api/chatbot/ et la vue de prédiction).Ces chemins d'accès ont été ajoutés et inclus dans le fichier d'URLs principal (urls.py) du projet.
Création et Enregistrement de l'Application Django :

Un nouveau module Django nommé modele_ia a été créé via la commande django-admin startapp modele_ia.

Cette nouvelle application a été ajoutée à la liste INSTALLED_APPS dans le fichier settings.py.

## ** Gestion de la Clé d'API : **

Une nouvelle clé de configuration, GEMINI_API_KEY, a été ajoutée au fichier settings.py.

⚠️ Important : Pour une utilisation en production, cette clé doit être stockée dans un fichier de configuration sécurisé (.env) plutôt que directement dans settings.py.

## ** 2. 💡 Nouvelles Fonctionnalités Développées **

Le nouveau module modele_ia introduit deux vues principales exposant des services via des endpoints API.

## A. 💬 Chatbot de Bien-être et Conseils (API Endpoint: api/chatbot/)

Cette vue implémente un chatbot conçu pour offrir des conseils de bien-être et de l'assistance aux femmes enceintes.Objectif : Encourager le bien-être général et fournir des informations non médicales.Contrainte Éthique et Sécurité : Le modèle est strictement configuré pour NE PAS fournir de recommandations sur des médicaments ou des traitements médicaux. Son rôle est d'inciter la patiente à consulter son médecin en cas de problème de santé.

## B. 🔬 Vue de Prédiction du Risque de Santé Maternelle

Cette vue expose un service d'analyse prédictive qui sert d'Outil d'Aide à la Décision Clinique pour les professionnels de la santé.
### **Modèle Utilisé : ***

 Un modèle de Machine Learning entraîné pour évaluer le risque de la femme enceinte (Faible, Moyen, Élevé).
 
 ### Fonctionnalité pour le Clinicien :
 
 Le modèle analyse les données des visites passées pour fournir une vue d'ensemble de la tendance du risque.Pour chaque prédiction de visite, des explications claires sont fournies, identifiant le facteur clé (la donnée) qui a conduit à la décision de risque.Un graphique est généré pour visualiser l'évolution du risque au fil des rendez-vous.
 
 ## Données d'Entrée Utilisées pour le Modèle :
 
  Le modèle utilise les données statiques (de base) et celles relevées lors de chaque visite : Âge de la patiente, Tension Systolique (BP),Pression artérielle, systolique, Tension Diastolique (BP), Pression artérielle diastolique, Température corporelle
  
  ## 📂 Fichiers et Intégration du ModèleFichiers du Modèle et des Données :
  
  Le module modele_ia contient le modèle entraîné sous forme de fichier sérialisé  maternal_health.pkl.Le fichier des données utilisé pour l'entraînement est également inclus à des fins de référence : Maternal Health Risk Data Set.csv.
  
  ## Configuration des URLs :
  
  Le module modele_ia inclut son propre fichier urls.py définissant les routes (api/chatbot/ et la vue de prédiction).Ces chemins d'accès ont été ajoutés et inclus dans le fichier d'URLs principal (urls.py) du projet.
  
  ## 4. ▶️ Démarrage du ProjetPour exécuter le projet, il suffit de :
  
  Télécharger (dézipper) le projet.Lancer le serveur en local.Le projet devrait alors être fonctionnel et prêt à tester les nouvelles API.

## 5. 💻 Intégration de la Vue Frontend (Code React)

Cette section documente l'ajout du code client (frontend) qui permet d'afficher la vue de prédiction et d'analyse des risques pour le médecin.

Localisation du Code : Le code React pour cette vue est inclus dans le fichier .zip fourni, au sein du dossier : viacare-front.

Fonctionnalité : Ce code est déjà fonctionnel et interagit avec l'API de prédiction. Il est spécifiquement conçu pour être utilisé par le clinicien (le médecin).

Travail Restant (Amélioration) :

Le CSS doit être modifié pour être en conformité avec la charte graphique et le design system du site existant.

Le dossier viacare-front doit être ajouté au code frontend existant en ligne.

## Instruction Impérative pour le Déploiement

Lors de la mise en production du code frontend, il est obligatoire de modifier l'URL de l'API dans le fichier app.jsx pour qu'elle pointe vers le bon endpoint en production.

http://127.0.0.1:8000/api/predict/ en exemple: https://votre-domaine.com/api/predict/

cette ligne dois etre mis a jour const apiUrl = 'http://127.0.0.1:8000/api/predict/';

et le module necessaire sont deja inclu dans requirements.txt