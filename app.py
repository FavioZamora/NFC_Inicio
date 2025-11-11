from flask import Flask, render_template, request, redirect, url_for
import time

app = Flask(__name__)

# --- Base de datos temporal en memoria ---
USUARIOS_DB = {}

# --- Variables Globales para Control de Intentos ---
intentos_fallidos = {}
MAX_INTENTOS = 3
TIEMPO_BLOQUEO_SEGUNDOS = 300  # 5 minutos
# ----------------------------------------------------


@app.route('/')
def home():
    return render_template('Home.html')


@app.route('/registro')
def registro_usuario():
    mensaje = request.args.get('mensaje')
    return render_template('registro_usuario.html', mensaje_exito=mensaje)


@app.route('/submit_registro', methods=['POST'])
def submit_registro():
    nfc_id = request.form.get('nfc_id').strip().upper()
    nombre_completo = request.form.get('nombre_completo').strip()
    departamento = request.form.get('departamento')
    security_level = request.form.get('security_level')
    pin_correcto = request.form.get('pin_correcto')

    if not (nfc_id and nombre_completo and pin_correcto and len(pin_correcto) == 4):
        return redirect(url_for('registro_usuario', mensaje="Error: Faltan datos o PIN inválido."))

    if nfc_id in USUARIOS_DB:
        return redirect(url_for('registro_usuario', mensaje="Error: El UID NFC ya está registrado."))

    USUARIOS_DB[nfc_id] = {
        "pin_correcto": pin_correcto,
        "nombre_completo": nombre_completo,
        "departamento": departamento,
        "security_level": security_level,
    }

    print(f"✅ Usuario registrado: {nombre_completo} ({nfc_id})")
    return redirect(url_for('registro_usuario', mensaje=f"Usuario {nombre_completo} registrado correctamente."))


@app.route('/pin_verification')
def pin_verification():
    return render_template('pin_verification.html')


@app.route('/verify_manual_login', methods=['POST'])
def verify_manual_login():
    nfc_id = request.form.get('nfc_id').strip().upper()
    pin = request.form.get('pin')

    if nfc_id not in USUARIOS_DB:
        return render_template('pin_verification.html', error_msg="Usuario no registrado.")

    datos_intento = intentos_fallidos.get(nfc_id, {"intentos": 0, "bloqueado_hasta": 0})
    ahora = time.time()

    if ahora < datos_intento["bloqueado_hasta"]:
        minutos_restantes = int((datos_intento["bloqueado_hasta"] - ahora) / 60)
        return render_template('pin_verification.html', error_msg=f"Cuenta bloqueada. Intente en {minutos_restantes} min.")

    if pin == USUARIOS_DB[nfc_id]["pin_correcto"]:
        intentos_fallidos.pop(nfc_id, None)
        nombre = USUARIOS_DB[nfc_id]["nombre_completo"]
        return f"✅ Bienvenido {nombre}. Acceso concedido."
    else:
        datos_intento["intentos"] += 1
        if datos_intento["intentos"] >= MAX_INTENTOS:
            datos_intento["bloqueado_hasta"] = ahora + TIEMPO_BLOQUEO_SEGUNDOS
            datos_intento["intentos"] = 0
            intentos_fallidos[nfc_id] = datos_intento
            return render_template('pin_verification.html', error_msg="Demasiados intentos fallidos. Usuario bloqueado.")
        else:
            intentos_fallidos[nfc_id] = datos_intento
            return render_template('pin_verification.html', error_msg="PIN incorrecto.")


if __name__ == '__main__':
    app.run(debug=True)
