import sqlite3
from datetime import datetime
import hashlib

class DatabaseManager:
    def __init__(self, db_name="nfc_auth_system.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Inicializar la base de datos con todas las tablas"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla de usuarios NFC
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nfc_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nfc_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL,
                security_level INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de registros de autenticación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                nfc_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                auth_success BOOLEAN NOT NULL,
                auth_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blockchain_tx_hash TEXT,
                failure_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES nfc_users (id)
            )
        ''')
        
        # Insertar usuarios de prueba
        test_users = [
            ("04A1B2C3D4E5", "analopez", "Ana Lopez", "Inteligencia", 3),
            ("04F6G7H8I9J0", "carlosruiz", "Carlos Ruiz", "Analisis", 2),
            ("04K1L2M3N4O5", "mariatorres", "Maria Torres", "Operaciones", 2),
        ]
        
        for nfc_id, username, full_name, department, security_level in test_users:
            cursor.execute('''
                INSERT OR IGNORE INTO nfc_users (nfc_id, username, full_name, department, security_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (nfc_id, username, full_name, department, security_level))
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    
    def register_nfc_user(self, nfc_id: str, username: str, full_name: str, 
                         department: str, security_level: int = 1) -> bool:
        """Registrar nuevo usuario NFC"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO nfc_users (nfc_id, username, full_name, department, security_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (nfc_id, username, full_name, department, security_level))
            
            conn.commit()
            print(f"✅ Usuario {full_name} registrado con NFC: {nfc_id}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"❌ Error: La tarjeta NFC {nfc_id} ya está registrada")
            return False
        finally:
            conn.close()
    
    def get_user_by_nfc(self, nfc_id: str):
        """Obtener usuario por ID NFC"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nfc_id, username, full_name, department, security_level, is_active
            FROM nfc_users 
            WHERE nfc_id = ? AND is_active = TRUE
        ''', (nfc_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'nfc_id': result[1],
                'username': result[2],
                'full_name': result[3],
                'department': result[4],
                'security_level': result[5],
                'is_active': bool(result[6])
            }
        return None
    
    def log_auth_attempt(self, user_id: int, nfc_id: str, device_id: str, 
                        success: bool, blockchain_tx_hash: str = None, 
                        failure_reason: str = None):
        """Registrar intento de autenticación"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO auth_logs 
            (user_id, nfc_id, device_id, auth_success, blockchain_tx_hash, failure_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, nfc_id, device_id, success, blockchain_tx_hash, failure_reason))
        
        conn.commit()
        conn.close()
        
        status = "EXITOSA" if success else "FALLIDA"
        print(f"📝 Autenticación {status} registrada para NFC: {nfc_id}")
    
    def get_auth_logs(self, limit: int = 50):
        """Obtener últimos registros de autenticación"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                al.auth_timestamp,
                u.full_name,
                u.department,
                al.nfc_id,
                al.device_id,
                al.auth_success,
                al.blockchain_tx_hash,
                al.failure_reason
            FROM auth_logs al
            JOIN nfc_users u ON al.user_id = u.id
            ORDER BY al.auth_timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'timestamp': row[0],
                'full_name': row[1],
                'department': row[2],
                'nfc_id': row[3],
                'device_id': row[4],
                'success': bool(row[5]),
                'blockchain_tx': row[6],
                'failure_reason': row[7]
            })
        
        conn.close()
        return logs

if __name__ == "__main__":
    db = DatabaseManager()
    print("✅ Base de datos creada exitosamente")