# sms_sender/services.py
import logging
import random
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def _normalize_mobile_numbers(mobile_numbers):
    if isinstance(mobile_numbers, (list, tuple)):
        return ",".join(str(m).strip() for m in mobile_numbers)
    return str(mobile_numbers).strip()

def send_sms_via_md(message, mobile_numbers, sender_id=None,
                   is_unicode=None, is_flash=None, data_coding=None,
                   schedule_time=None, group_id=None):
    """
    Appelle l'API MD SMS (GET).
    Retourne un dict structuré contenant:
      - success: bool
      - http_status: code HTTP si disponible
      - api_error_code / api_error_description si l'API MD retourne une erreur
      - data si tout ok
      - error_type et error (message lisible) en cas d'erreur réseau/config
    """
    base = getattr(settings, "MD_SMS_BASE_URL")
    api_key = getattr(settings, "MD_SMS_API_KEY")
    client_id = getattr(settings, "MD_SMS_CLIENT_ID")

    
    if not api_key or not client_id:
        return {
            "success": False,
            "error_type": "config",
            "error": "Missing ApiKey or ClientId in settings",
            "http_status": None
        }

    if sender_id is None:
        sender_id = "VIACAREME"  # valeur par défaut si non fourni

    params = {
        "ApiKey": api_key,
        "ClientId": client_id,
        "SenderId": sender_id,
        "Message": message,
        "MobileNumbers": _normalize_mobile_numbers(mobile_numbers),
    }
    if is_unicode is not None:
        params["Is_Unicode"] = str(bool(is_unicode)).lower()
    if is_flash is not None:
        params["Is_Flash"] = str(bool(is_flash)).lower()
    if data_coding is not None:
        params["DataCoding"] = str(data_coding)
    if schedule_time:
        params["ScheduleTime"] = schedule_time
    if group_id:
        params["GroupId"] = group_id

    headers = {"Content-Type": "application/json", "Type": "json"}
    timeout = getattr(settings, "MD_SMS_TIMEOUT", 10)

    try:
        resp = requests.get(base, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        logger.exception("Timeout contacting MD SMS")
        return {"success": False, "error_type": "timeout", "error": "Connection timed out", "http_status": 504}
    except requests.exceptions.ConnectionError:
        logger.exception("Connection error contacting MD SMS")
        return {"success": False, "error_type": "connection", "error": "Connection error to MD SMS host", "http_status": None}
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        text = exc.response.text if exc.response is not None else ""
        return {"success": False, "error_type": "http_error", "error": f"Upstream HTTP error {status}", "http_status": status, "raw": text}

    # parse response JSON (ou XML si nécessaire)
    try:
        data = resp.json()
    except ValueError:
        # réponse non-json (renvoie texte brut)
        return {"success": False, "error_type": "invalid_response", "error": "Invalid response format from MD SMS", "http_status": resp.status_code, "raw_text": resp.text}

    # Le format attendu: { "ErrorCode": 0, "ErrorDescription": "Success", "Data": [...] }
    err_code = data.get("ErrorCode")
    err_desc = data.get("ErrorDescription")
    if err_code is None:
        # structure inattendue
        return {"success": False, "error_type": "invalid_structure", "error": "Missing ErrorCode in response", "http_status": resp.status_code, "raw": data}

    if int(err_code) != 0:
        # Priorité: retourner le code d'erreur renvoyé par MD SMS + description
        return {
            "success": False,
            "error_type": "api_error",
            "api_error_code": int(err_code),
            "api_error_description": err_desc,
            "http_status": resp.status_code,
            "raw": data
        }

    # succès
    return {"success": True, "http_status": resp.status_code, "data": data.get("Data")}
