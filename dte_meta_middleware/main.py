# -- coding: utf-8 --
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel, EmailStr
import hmac
import hashlib
import requests
import os
from typing import Optional
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

app = FastAPI(
    title="DTE Meta Middleware", 
    description="Capa perimetral de seguridad y pre-procesamiento para DTE Bolivia",
    version="1.0"
)

def verificar_firma_meta(payload: bytes, signature: str):
    """ Verifica mediante HMAC-SHA256 que la petición provenga auténticamente de Meta """
    if not signature:
        raise HTTPException(status_code=401, detail="Falta la firma de seguridad X-Hub-Signature-256")
    
    secret = os.getenv("META_APP_SECRET", "").encode('utf-8')
    expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    actual_signature = signature.replace("sha256=", "")
    
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise HTTPException(status_code=401, detail="Firma de Meta inválida. Acceso denegado.")

@app.get("/v1/meta/webhook")
def verificar_webhook(request: Request):
    """ Endpoint requerido por Meta para validar la activación del Webhook (Handshake) """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == os.getenv("META_VERIFY_TOKEN"):
            # Meta espera recibir exactamente el valor entero de 'challenge' enviado
            return int(challenge)
        raise HTTPException(status_code=403, detail="Token de verificación inválido")
    raise HTTPException(status_code=400, detail="Parámetros insuficientes")

@app.post("/v1/meta/webhook")
async def recibir_evento_meta(request: Request, x_hub_signature_256: Optional[str] = Header(None)):
    """ Recibe los payloads de interacciones de Meta en tiempo real """
    body_bytes = await request.body()
    
    # 1. Validar firma de seguridad perimetral
    verificar_firma_meta(body_bytes, x_hub_signature_256)
    
    # 2. Simulación de mapeo y limpieza del payload complejo que envía Meta
    # Nota: El desarrollador final extraerá los campos reales del JSON (request.json())
    clean_lead = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "phone": "+59171234567",
        "email": "juan.perez@example.com",
        "channel": "whatsapp",
        "campaign": "Campaña_Bolivia_2026",
        "message": "Hola, estoy interesado en sus servicios de software."
    }
    
    # 3. Retransmitir al controlador web de Odoo utilizando autenticación por Token
    odoo_url = os.getenv("ODOO_WEBHOOK_URL")
    headers = {
        "Authorization": f"Bearer {os.getenv('ODOO_BEARER_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(odoo_url, json=clean_lead, headers=headers, timeout=10)
        return {
            "status": "success", 
            "message": "Evento procesado y enviado a Odoo", 
            "odoo_status_code": response.status_code
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"No se pudo conectar con el ERP Odoo: {str(e)}")

@app.get("/v1/health")
def health_check():
    """ Endpoint de diagnóstico rápido consultado por el botón 'Probar Conexión' de Odoo """
    return {"status": "online", "service": "DTE Meta Middleware"}