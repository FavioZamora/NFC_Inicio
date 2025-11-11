from database import DatabaseManager

# Registrar tu tarjeta NFC física
db = DatabaseManager()

tu_tarjeta = "A0F9001E"  # El UID que leímos anteriormente
tu_usuario = "aimee"     # Cambia por tu usuario
tu_nombre = "Aimee"      # Cambia por tu nombre
tu_departamento = "Desarrollo"

if db.register_nfc_user(tu_tarjeta, tu_usuario, tu_nombre, tu_departamento, 2):
    print(f"✅ Tarjeta {tu_tarjeta} registrada para {tu_nombre}")
    print("🔐 PIN asignado: 0000")  # Usaremos este PIN
else:
    print("❌ Error al registrar tarjeta")