from django.shortcuts import render

# Create your views here.
# views.py
import json
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from google import genai
from google.genai import types

import joblib
import pandas as pd
import numpy as np
import shap

from django.utils.decorators import method_decorator
from django.views import View

import os


# --- CONFIGURATION DU JOURNAL DE BORD (LOGGING) ---
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='chatbot.log',
    filemode='a'
)

# --- CONFIGURATION API ET PROMPT SYSTÈME ---
client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """
Ton rôle est d'agir comme un assistant de bien-être pour les femmes enceintes. 
Tes conseils doivent se limiter à des recommandations de bien-être général (repos, hydratation, alimentation équilibrée, exercice léger approuvé).

CONTRAINTES DE FORMAT ET D'ACCUEIL :
1. Toutes tes réponses doivent être concises et ne jamais dépasser 300 caractères (espaces inclus).
2. Si l'utilisateur dit simplement "bonjour", "salut", "hello", réponds par une formule d'accueil très courte comme : "Bonjour ! Je suis votre assistant de bien-être. Comment puis-je vous aider aujourd'hui ?"

INSTRUCTIONS STRICTES (Sécurité) :
1. Tu ne dois JAMAIS donner de conseils sur des médicaments, des diagnostics,  ou des traitements médicaux.
2. Tu ne dois JAMAIS recommander une action qui pourrait être dangereuse sans l'avis d'un professionnel de la santé.

GESTION DES AVIS DE NON-RESPONSABILITÉ (CRITIQUE) :
1. **OMETS L'AVIS LÉGAL COMPLET** pour les salutations ou les questions de **bien-être général** (repos, hydratation, rôle du partenaire, etc.).
2. Pour les questions portant sur des **symptômes** ou des **diagnostics** (vertiges, douleurs), tu dois refuser de répondre en dirigeant l'utilisateur vers son professionnel de la santé, mais tu **OMETS L'AVIS LÉGAL COMPLET** (juste une phrase courte de refus).
3. **APPLIQUE L'AVIS LÉGAL COMPLET** seulement et uniquement si la question concerne des **médicaments, des produits, des compléments alimentaires, ou des traitements**.
4. L'avis légal complet (lorsqu'il est appliqué) doit être **reformulé à chaque fois** et doit être clair (ex: "Il est impératif de demander conseil à votre médecin" ou "Consultez toujours votre professionnel de la santé.").
"""


def get_gemini_config():
    """Crée l'objet de configuration avec le prompt système."""
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT
    )

def convert_history_to_dicts(history):
    """
    ULTIMATE FIX: Converts the history (Content/UserContent objects) into a list 
    of serializable dictionaries using the reliable dict() conversion.
    """
    serializable_history = []
    for content in history:
        
        serializable_history.append({
            'role': content.role,
           
            'parts': [{'text': part.text} for part in content.parts if hasattr(part, 'text')]
        })
    return serializable_history

@csrf_exempt
def chat_view(request):
    """
    Vue Django pour gérer la conversation avec Gemini.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest(json.dumps({'error': 'Méthode non autorisée. Utilisez POST.'}), content_type="application/json")

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
    except json.JSONDecodeError:
        logging.warning("Tentative de requête avec JSON invalide.")
        return HttpResponseBadRequest(json.dumps({'error': 'Format JSON invalide.'}), content_type="application/json")

    if not user_message:
        return JsonResponse({'response': 'Veuillez envoyer un message.'})

    # --- 1. HISTORIQUE  ---
    session_history_dicts = request.session.get('chat_history', [])
    
    # 2. Reconstruct Chat Object
    try:
        
        history_to_pass = [
            types.Content(role=item['role'], parts=[types.Part.from_text(p['text']) for p in item['parts']])
            for item in session_history_dicts
        ]
        
    
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=get_gemini_config(),
            history=history_to_pass 
        )
        
      
        response = chat.send_message(user_message)
        response_text = response.text

      
        new_history_objects = chat.get_history()
       
        request.session['chat_history'] = convert_history_to_dicts(new_history_objects)
        
    except Exception as e:
       
        logging.error(f"Erreur Gemini sur la session {request.session.session_key}: {e}", exc_info=True)
        return JsonResponse({'response': 'Désolé, une erreur de l\'API est survenue. Veuillez réessayer.'})

    return JsonResponse({'response': response_text})





import os
import joblib
import pandas as pd
import shap
import json
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# --- 1. CONFIGURATION ET VARIABLES GLOBALES ---
# Les features attendues par le modèle
EXPECTED_FEATURES = ['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate']

# 🚨 BORNES CLINIQUES ACCEPTABLES pour la validation (Valeurs min/max réalistes) 🚨
# Toute donnée hors de ces bornes sera rejetée avec un code 400.
# Ces valeurs doivent être ajustées selon les normes médicales exactes que vous ciblez.
RANGES_CLINIQUES_ACCEPTABLES = {
    'Age': (15, 60),           # Âge (années)
    'SystolicBP': (70, 250),   # Tension artérielle systolique (mmHg)
    'DiastolicBP': (40, 150),  # Tension artérielle diastolique (mmHg)
    'BS': (1.0, 30.0),         # Glycémie (Blood Sugar)
    'BodyTemp': (90.0, 104.0), # Température corporelle (°F) 
    'HeartRate': (40, 180)     # Fréquence Cardiaque (BPM)
}

# Chemins d'accès aux fichiers (ajustés à votre structure)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "maternal_health.pkl")
DATA_PATH = os.path.join(os.path.dirname(__file__), "Maternal Health Risk Data Set.csv") # Pour SHAP background

model = None
explainer = None

# --- 2. CHARGEMENT DU MODÈLE ET SHAP ---
try:
    # Chargement du modèle
    model = joblib.load(MODEL_PATH)
    
    # Préparation du background pour SHAP
    data_originale = pd.read_csv(DATA_PATH)
    X_background = data_originale[EXPECTED_FEATURES].sample(n=100, random_state=42) 
    
    # Initialisation de l'explainer SHAP
    explainer = shap.Explainer(model.predict, X_background) 
    print("Modèle et SHAP Explainer chargés avec succès.")
except Exception as e:
    print(f"Erreur lors du chargement du modèle ou des données SHAP: {e}")
    model = None
    explainer = None


# FONCTION DE VALIDATION DES DONNÉES  
def validate_visits_data(visits):
    """
    Valide que la liste des visites contient les features attendues, 
    que les valeurs sont numériques et qu'elles sont dans les bornes cliniques acceptables.
    """
    errors = []
    
    if not isinstance(visits, list) or not visits:
        return ["La liste 'visits' est manquante ou vide. Elle doit contenir au moins un enregistrement."]

    for i, visit in enumerate(visits):
        visit_index = i + 1
        
        if not isinstance(visit, dict):
            errors.append(f"Visite #{visit_index} : Le format est incorrect.")
            continue

        # Vérification des clés manquantes
        missing_features = [f for f in EXPECTED_FEATURES if f not in visit]
        if missing_features:
            errors.append(f"Visite #{visit_index} : Colonnes manquantes : {', '.join(missing_features)}")
            
        # Vérification des types et des plages
        for feature in EXPECTED_FEATURES:
            if feature in visit:
                value = visit[feature]
                
                if value is None:
                     errors.append(f"Visite #{visit_index}, feature '{feature}' : La valeur ne peut pas être nulle.")
                     continue
                
                try:
                    num_value = float(value)
                    
                    # Vérification des bornes cliniques
                    min_val, max_val = RANGES_CLINIQUES_ACCEPTABLES[feature]
                    
                    if not (min_val <= num_value <= max_val):
                         errors.append(
                            f"Visite #{visit_index}, feature '{feature}' : Valeur '{value}' hors des limites cliniques ({min_val} - {max_val}) voyez si c'est une erreur de saisie."
                         )

                except (TypeError, ValueError):
                    errors.append(f"Visite #{visit_index}, feature '{feature}' : La valeur '{value}' doit être un nombre.")

    return errors


# --- 4. CLASSE VUE DJANGO ---
@method_decorator(csrf_exempt, name='dispatch')
class PredictionView(View):
    """
    Vue Django pour recevoir les données de visite, effectuer la prédiction et l'explication SHAP.
    """
    def post(self, request, *args, **kwargs):
        # 0. Vérification de l'initialisation du Modèle/Explainer
        if not model or not explainer:
            return JsonResponse({
                'status': 'Reseillez une erreur est survenue',
                
            }, status=500)
            
        try:
            data = json.loads(request.body)
            visits = data.get('visits', [])
            
            # 1. Validation des données d'entrée 🚨 (Utilise la fonction mise à jour)
            validation_errors = validate_visits_data(visits)
            
            if validation_errors:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erreur de validation des données fournies.',
                    'details': validation_errors
                }, status=400)
            
            # Création du DataFrame et ordonnancement des colonnes
            X_visites = pd.DataFrame(visits, columns=EXPECTED_FEATURES)
            
            # Conversion forcée des types en float pour le modèle
            X_visites = X_visites.astype(float)
            
            # 2. Prédictions
            predictions = model.predict(X_visites)
            
            # 3. Résumé global
            risque_moyen = predictions.mean()
            risque_max = predictions.max()
            tendance = predictions[-1] - predictions[0]

            if tendance > 0:
                tendance_str = "Le risque augmente"
            elif tendance < 0:
                tendance_str = "Le risque diminue"
            else:
                tendance_str = "Risque stable"
            
            global_summary = {
                "risque_moyen": float(risque_moyen),
                "risque_max": float(risque_max),
                "tendance": tendance_str
            }
            
            # 4. Explications SHAP
            shap_values = explainer(X_visites)
            shap_explanations = []
            features = list(X_visites.columns)
            
            for i in range(len(X_visites)):
                contributions = {}
                for col_index, col_name in enumerate(features):
                    contributions[col_name] = float(shap_values.values[i][col_index])
                    
                base_value = float(shap_values.base_values[i]) if hasattr(shap_values.base_values, '__len__') and len(shap_values.base_values) > i else float(shap_values.base_values)

                shap_explanations.append({
                    "base_value": base_value,
                    "contributions": contributions
                })

            # 5. Réponse de Succès 🎉
            response_data = {
                "status": "success",
                "predictions": predictions.tolist(),
                "global_summary": global_summary,
                "shap_explanations": shap_explanations
            }
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            # Erreur JSON (mauvaise syntaxe)
            return JsonResponse({
                'status': 'error', 
                'message': 'Format JSON invalide. Assurez-vous que le corps de la requête est un JSON valide.',
                'details': []
            }, status=400)
            
        except Exception as e:
            # Toute autre erreur non gérée
            error_message = f'Erreur interne du serveur lors du traitement ML : {e}'
            print(f"Erreur lors du traitement de la requête: {error_message}")
            return JsonResponse({
                'status': 'error', 
                'message': error_message,
                'details': ['Une erreur inattendue s\'est produite après la validation des données.']
            }, status=500)