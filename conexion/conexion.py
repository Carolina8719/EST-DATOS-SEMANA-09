"""
Conexión a MySQL - Semana 13
Sistema de Citas Médicas
Autor: Carolina8719
"""

import mysql.connector
from mysql.connector import Error


# ── Parámetros de conexión ──────────────────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Kmelie1987*',
    'database': 'citas_medicas',
    'port':     3306,
    'charset':  'utf8mb4',
}


def get_connection():
    """Retorna una conexión activa a MySQL. Lanza Error si falla."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise RuntimeError(f"No se pudo conectar a MySQL: {e}")


def test_connection():
    """Verifica la conexión e imprime el resultado. Útil para depuración."""
    try:
        conn = get_connection()
        if conn.is_connected():
            info = conn.get_server_info()
            print(f"✅ Conexión exitosa. Versión MySQL: {info}")
        conn.close()
        return True
    except RuntimeError as e:
        print(f"❌ {e}")
        return False


if __name__ == '__main__':
    test_connection()