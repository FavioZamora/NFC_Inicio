# server.py

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import time

# --- Módulos de tu proyecto ---
# Asume que DatabaseManager puede consultar usuarios y verificar PINs.
# Asume que BlockchainSimulated registra el intento.
from database import DatabaseManager
from blockchain_simulated import BlockchainSimulated

# --- Configuración Inicial ---
app = FastAPI()
db_manager = DatabaseManager()
blockchain = BlockchainSimulated()
templates = Jinja2Templates(directory="templates") # Asume que index.html está en una carpeta 'templates'

# --- Simulación de Usuario (Información obtenida de la DB tras lectura NFC) ---
# Usamos el dato de Ana Lopez (UID: 04A1B2C3D4E5, Nivel 3)
TEST_NFC_ID = "04A1B2C3D4E5"
TEST_PIN = "1234" # Pin de prueba de Ana Lopez
DEVICE_ID = "ACR122U-STATION-01"

# --------------------------------------------------------------------
# 1. RUTA PARA MOSTRAR EL FORMULARIO DE PIN
# (Se ejecuta después de que el lector NFC envía el UID al servidor)
# --------------------------------------------------------------------
@app.get("/auth_pin/{nfc_id}", response_class=HTMLResponse)
async def show_pin_form(request: Request, nfc_id: str):
    """
    Simula la carga de la página después de que la tarjeta NFC ha sido leída.
    Busca los datos del usuario en la DB y rellena el HTML.
    """
    user_data = db_manager.get_user_by_nfc_id(nfc_id)
    
    if not user_data:
        # Si la tarjeta no está registrada
        context = {
            "request": request, 
            "result_state": "DENIED",
            "message": "Tarjeta NFC no registrada o inactiva."
        }
        return templates.TemplateResponse("result.html", context)


    # Rellenar los placeholders del index.html
    context = {
        "request": request,
        "nombre_completo": user_data['full_name'],
        "departamento": user_data['department'],
        "security_level": user_data['security_level'],
        "nfc_id": user_data['nfc_id']
    }
    
    # Renderiza el archivo HTML con los datos
    # Asume que el HTML (index.html) fue renombrado a 'pin_form.html'
    return templates.TemplateResponse("pin_form.html", context)


# --------------------------------------------------------------------
# 2. RUTA PARA PROCESAR EL FORMULARIO Y VERIFICAR EL PIN
# (Esta es la ruta que causaba el error 404 en el navegador)
# --------------------------------------------------------------------
@app.post("/verify_pin", response_class=HTMLResponse)
async def verify_pin(request: Request, nfc_id: str = Form(...), pin: str = Form(...)):
    """
    Recibe el UID y el PIN, verifica la autenticación y registra en DB/Blockchain.
    """
    
    user_data = db_manager.get_user_by_nfc_id(nfc_id)
    
    # 1. Verificar si el usuario existe y si el PIN es correcto (Simulación)
    # En un sistema real, el PIN no se almacenaría directamente, sino un hash
    
    # Simulación de la verificación del PIN
    is_success = (user_data and pin == TEST_PIN) 

    # 2. Registrar el intento en la Blockchain Simulada
    tx_hash = blockchain.record_auth_attempt(
        user_id=user_data['username'] if user_data else "UNKNOWN",
        timestamp=datetime.now().timestamp(),
        device_id=DEVICE_ID,
        nfc_id=nfc_id,
        success=is_success
    )
    
    # 3. Registrar el intento en la Base de Datos
    db_manager.log_auth_attempt(
        user_id=user_data['id'] if user_data else 0, # Usar el ID de la DB
        nfc_id=nfc_id,
        device_id=DEVICE_ID,
        success=is_success,
        tx_hash=tx_hash,
        failure_reason="PIN Incorrecto" if not is_success and user_data else "Tarjeta Invalida"
    )

    # 4. Mostrar el resultado
    if is_success:
        result_state = "PERMITTED"
        message = f"Acceso Concedido para {user_data['full_name']}."
    else:
        result_state = "DENIED"
        message = "Acceso Denegado. PIN o Tarjeta inválida."

    context = {
        "request": request, 
        "result_state": result_state, 
        "message": message,
        "nfc_id": nfc_id,
        "tx_hash": tx_hash
    }
    
    # Renderiza la página de resultado (usamos un HTML diferente o la misma plantilla)
    return templates.TemplateResponse("result.html", context)

# --------------------------------------------------------------------
# CÓMO EJECUTAR ESTE SERVIDOR:
# Guardas esto como server.py
# Creas una carpeta llamada 'templates' y pones tu HTML dentro (ej: pin_form.html y result.html)
# Ejecutas en la terminal: uvicorn server:app --reload
# --------------------------------------------------------------------