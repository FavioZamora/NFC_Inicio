import time
from typing import Optional

class ACR122USimple:
    """Versión simplificada para ACR122U - Modo Manual"""
    
    def __init__(self):
        self.reader = "ACS ACR122U PICC Interface 0"
        print("✅ Lector NFC ACR122U (Modo Manual)")
    
    def wait_for_card(self, timeout: int = 30) -> Optional[str]:
        """Esperar tarjeta - modo manual"""
        print("\n🎫 MODO MANUAL - Ingrese el UID de la tarjeta:")
        print("Tarjetas de prueba disponibles:")
        print("1. 04A1B2C3D4E5 - Ana Lopez (PIN: 1234)")
        print("2. 04F6G7H8I9J0 - Carlos Ruiz (PIN: 5678)") 
        print("3. 04K1L2M3N4O5 - Maria Torres (PIN: 9012)")
        print("4. A0F9001E - Tu tarjeta física (Registrar primero)")
        print("\nO ingrese manualmente el UID")
        
        choice = input("\nSeleccione (1-4) o ingrese UID: ").strip()
        
        cards = {
            "1": "04A1B2C3D4E5",
            "2": "04F6G7H8I9J0",
            "3": "04K1L2M3N4O5", 
            "4": "A0F9001E"
        }
        
        if choice in cards:
            uid = cards[choice]
            print(f"✅ Tarjeta seleccionada: {uid}")
            return uid
        elif len(choice) >= 8:  # Asumir que es un UID válido
            print(f"✅ UID ingresado: {choice.upper()}")
            return choice.upper()
        else:
            print("❌ Selección inválida")
            return None
    
    def connect_to_reader(self):
        return True
    
    def disconnect(self):
        pass

    # Métodos dummy para compatibilidad
    def initialize_reader(self):
        return True
    
    def read_nfc_card(self):
        return None
    
    def test_connection(self):
        return True