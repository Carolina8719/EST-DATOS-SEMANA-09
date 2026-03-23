from werkzeug.security import generate_password_hash, check_password_hash
from conexion.conexion import get_connection

def registrar_usuario_mysql(nombre, mail, password, rol='recepcionista'):
    hashed = generate_password_hash(password)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_usuario FROM usuarios WHERE mail = %s", (mail,))
            if cursor.fetchone():
                return False, "El correo ya está registrado."
            cursor.execute(
                "INSERT INTO usuarios (nombre, mail, password, rol) VALUES (%s, %s, %s, %s)",
                (nombre, mail, hashed, rol)
            )
            conn.commit()
            return True, "Usuario registrado correctamente."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def autenticar_usuario_mysql(mail, password):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT id_usuario, nombre, mail, password, rol FROM usuarios WHERE mail = %s",
                (mail,)
            )
            usuario = cursor.fetchone()
            if usuario and check_password_hash(usuario['password'], password):
                return usuario
            return None
    except Exception as e:
        print(f"Error al autenticar: {e}")
        return None
    finally:
        conn.close()

def obtener_usuario_por_id(id_usuario):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT id_usuario, nombre, mail, password, rol FROM usuarios WHERE id_usuario = %s",
                (id_usuario,)
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None
    finally:
        conn.close()