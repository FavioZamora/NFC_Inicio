import time
from typing import Optional

from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardConnection import CardConnection
import smartcard

class ACR122UReader:
    def __init__(self):
        self.reader = None
        self.connection = None
        self.initialize_reader()

    # ---------- util ----------
    @staticmethod
    def _normalize_uid(uid_bytes) -> str:
        # "A0F9001E" (sin espacios, mayúsculas)
        return ''.join(f'{b:02X}' for b in uid_bytes)

    # ---------- setup ----------
    def initialize_reader(self) -> bool:
        """Detecta el lector y selecciona el primero disponible."""
        try:
            available_readers = readers()
            if not available_readers:
                print("❌ No se encontraron lectores ACR122U conectados")
                return False

            print(f"✅ Lectores encontrados: {len(available_readers)}")
            for i, r in enumerate(available_readers):
                print(f"  {i+1}. {r}")

            self.reader = available_readers[0]
            print(f"🔌 Lector seleccionado: {self.reader}")
            return True
        except Exception as e:
            print(f"❌ Error inicializando lector: {e}")
            return False

    def connect_to_reader(self) -> bool:
        """Conecta al lector ACR122U usando T=1 (contactless)."""
        try:
            if not self.reader:
                print("❌ Lector no inicializado")
                return False

            self.connection = self.reader.createConnection()
            # CLAVE: T=1 para el ACR122U PICC interface
            self.connection.connect(CardConnection.T1_protocol)
            print("✅ Conectado al ACR122U (T=1) – listo para leer tarjetas")
            return True

        except smartcard.Exceptions.NoCardException:
            # Normal cuando aún no hay tarjeta
            print("🔴 No hay tarjeta en el lector – coloque una tarjeta NFC")
            return False
        except Exception as e:
            print(f"❌ Error conectando al lector: {e}")
            return False

    # ---------- lectura ----------
    def read_nfc_card(self) -> Optional[str]:
        """Lee una tarjeta NFC (UID). Devuelve None si no hay tarjeta."""
        try:
            if not self.connection:
                if not self.connect_to_reader():
                    return None

            # APDU para obtener UID (ACR122U)
            get_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = self.connection.transmit(get_uid)

            if (sw1, sw2) == (0x90, 0x00):
                uid_hex = self._normalize_uid(data)
                print(f"✅ Tarjeta detectada: UID {uid_hex}")
                return uid_hex
            else:
                # 63 00 u otro: no hay tarjeta o fallo en operación
                return None

        except smartcard.Exceptions.NoCardException:
            return None
        except smartcard.Exceptions.CardConnectionException as e:
            print(f"⚠️  Conexión caída, reintentando: {e}")
            self.connection = None
            return None
        except Exception as e:
            print(f"⚠️  Error leyendo tarjeta: {e}")
            return None

    def wait_for_card(self, timeout: int = 30) -> Optional[str]:
        """Espera una tarjeta hasta 'timeout' segundos y devuelve el UID."""
        print("\n🎫 COLOCA UNA TARJETA NFC EN EL LECTOR…")
        start = time.time()
        attempts = 0

        while time.time() - start < timeout:
            attempts += 1

            if not self.connection:
                if not self.connect_to_reader():
                    time.sleep(0.5)
                    continue

            uid = self.read_nfc_card()
            if uid:
                return uid

            if attempts % 10 == 0:
                elapsed = int(time.time() - start)
                print(f"⏳ Esperando tarjeta... ({elapsed}/{timeout}s)")

            time.sleep(0.3)

        print("⏰ Timeout esperando tarjeta")
        return None

    # ---------- pruebas / cierre ----------
    def test_connection_simple(self) -> bool:
        """Conexión básica (negocia protocolo automáticamente)."""
        print("🧪 PROBANDO CONEXIÓN SIMPLE…")
        if not self.reader:
            print("❌ No se detectó el lector")
            return False
        try:
            self.connection = self.reader.createConnection()
            self.connection.connect()  # auto-negociación; en ACR122U suele elegir T=1
            print("✅ Conexión básica establecida")
            return True
        except Exception as e:
            print(f"🔴 Error en conexión básica: {e}")
            return False

    def disconnect(self):
        try:
            if self.connection:
                self.connection.disconnect()
                self.connection = None
                print("🔌 Desconectado del ACR122U")
        except:
            pass
