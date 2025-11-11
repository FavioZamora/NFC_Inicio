from acr122u_reader import ACR122UReader
import time

def test_acr122u():
    print("🧪 TESTEO DE CONEXIÓN ACR122U")
    print("=" * 50)
    
    # Crear instancia del lector
    reader = ACR122UReader()
    
    if reader.reader:
        print("✅ ACR122U DETECTADO CORRECTAMENTE")
        print(f"📋 Lector: {reader.reader}")
        
        if reader.connect_to_reader():
            print("✅ CONEXIÓN ESTABLECIDA")
            print("\n🔴 COLOCAR TARJETA NFC EN EL LECTOR...")
            print("   (La luz debe estar parpadeando)")
            
            # Esperar tarjeta
            card_uid = reader.wait_for_card(20)
            if card_uid:
                print(f"🎉 ¡ÉXITO! Tarjeta leída: {card_uid}")
            else:
                print("❌ No se pudo leer tarjeta")
            
            reader.disconnect()
        else:
            print("❌ No se pudo conectar al lector")
    else:
        print("❌ ACR122U NO DETECTADO")
        print("\n🔧 SOLUCIÓN DE PROBLEMAS:")
        print("1. Conecta el ACR122U por USB")
        print("2. Instala controladores si es necesario")
        print("3. Reinicia VS Code")
        print("4. Prueba en otro puerto USB")

if __name__ == "__main__":
    test_acr122u()
    
    # Mantener la ventana abierta
    input("\nPresiona Enter para salir...")