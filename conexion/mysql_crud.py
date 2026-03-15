"""
Operaciones CRUD en MySQL - Semana 13
Sistema de Citas Médicas
Autor: Carolina8719
"""

from conexion.conexion import get_connection


# ============================================================
#  USUARIOS
# ============================================================

def insertar_usuario(nombre: str, mail: str, password: str, rol: str = 'recepcionista'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre, mail, password, rol) VALUES (%s, %s, %s, %s)",
        (nombre, mail, password, rol)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close(); conn.close()
    return nuevo_id


def obtener_usuarios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_usuario, nombre, mail, rol, created_at FROM usuarios ORDER BY nombre")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def actualizar_usuario(id_usuario: int, nombre: str, mail: str, rol: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET nombre=%s, mail=%s, rol=%s WHERE id_usuario=%s",
        (nombre, mail, rol, id_usuario)
    )
    conn.commit()
    afectadas = cursor.rowcount
    cursor.close(); conn.close()
    return afectadas > 0


def eliminar_usuario(id_usuario: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    conn.commit()
    afectadas = cursor.rowcount
    cursor.close(); conn.close()
    return afectadas > 0


# ============================================================
#  PACIENTES
# ============================================================

def insertar_paciente_mysql(nombre, cedula, telefono, correo, fecha_nacimiento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO pacientes (nombre, cedula, telefono, correo, fecha_nacimiento)
           VALUES (%s, %s, %s, %s, %s)""",
        (nombre, cedula, telefono, correo, fecha_nacimiento)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close(); conn.close()
    return nuevo_id


def obtener_pacientes_mysql():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pacientes ORDER BY nombre")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def obtener_paciente_mysql(id_paciente: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pacientes WHERE id_paciente=%s", (id_paciente,))
    row = cursor.fetchone()
    cursor.close(); conn.close()
    return row


def actualizar_paciente_mysql(id_paciente, nombre, telefono, correo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pacientes SET nombre=%s, telefono=%s, correo=%s WHERE id_paciente=%s",
        (nombre, telefono, correo, id_paciente)
    )
    conn.commit()
    ok = cursor.rowcount > 0
    cursor.close(); conn.close()
    return ok


def eliminar_paciente_mysql(id_paciente: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pacientes WHERE id_paciente=%s", (id_paciente,))
    conn.commit()
    ok = cursor.rowcount > 0
    cursor.close(); conn.close()
    return ok


# ============================================================
#  DOCTORES
# ============================================================

def insertar_doctor_mysql(nombre, especialidad, telefono, correo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO doctores (nombre, especialidad, telefono, correo) VALUES (%s, %s, %s, %s)",
        (nombre, especialidad, telefono, correo)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close(); conn.close()
    return nuevo_id


def obtener_doctores_mysql():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctores ORDER BY nombre")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def obtener_doctor_mysql(id_doctor: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctores WHERE id_doctor=%s", (id_doctor,))
    row = cursor.fetchone()
    cursor.close(); conn.close()
    return row


def actualizar_doctor_mysql(id_doctor, nombre, especialidad, telefono, correo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE doctores SET nombre=%s, especialidad=%s, telefono=%s, correo=%s WHERE id_doctor=%s",
        (nombre, especialidad, telefono, correo, id_doctor)
    )
    conn.commit()
    ok = cursor.rowcount > 0
    cursor.close(); conn.close()
    return ok


def eliminar_doctor_mysql(id_doctor: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctores WHERE id_doctor=%s", (id_doctor,))
    conn.commit()
    ok = cursor.rowcount > 0
    cursor.close(); conn.close()
    return ok


# ============================================================
#  CITAS
# ============================================================

def insertar_cita_mysql(id_paciente, id_doctor, fecha, hora, motivo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO citas (id_paciente, id_doctor, fecha, hora, motivo, estado)
           VALUES (%s, %s, %s, %s, %s, 'Pendiente')""",
        (id_paciente, id_doctor, fecha, hora, motivo)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close(); conn.close()
    return nuevo_id


def obtener_citas_detalle_mysql():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id_cita, c.fecha, c.hora, c.motivo, c.estado,
               p.nombre AS nombre_paciente, p.cedula,
               d.nombre AS nombre_doctor, d.especialidad
        FROM   citas c
        JOIN   pacientes p ON c.id_paciente = p.id_paciente
        JOIN   doctores  d ON c.id_doctor   = d.id_doctor
        ORDER  BY c.fecha, c.hora
    """)
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def actualizar_estado_cita_mysql(id_cita: int, nuevo_estado: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE citas SET estado=%s WHERE id_cita=%s",
        (nuevo_estado, id_cita)
    )
    conn.commit()
    ok = cursor.rowcount > 0
    cursor.close(); conn.close()
    return ok


def eliminar_cita_mysql(id_cita: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM citas WHERE id_cita=%s", (id_cita,))
    conn.commit()
    ok = cursor.rowcount > 0
    cursor.close(); conn.close()
    return ok


# ============================================================
#  ESTADÍSTICAS
# ============================================================

def estadisticas_mysql():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM pacientes")
    total_pacientes = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM doctores")
    total_doctores = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM citas")
    total_citas = cursor.fetchone()['total']

    cursor.execute("""
        SELECT estado, COUNT(*) AS cantidad
        FROM citas GROUP BY estado
    """)
    citas_por_estado = {row['estado']: row['cantidad'] for row in cursor.fetchall()}

    cursor.close(); conn.close()
    return {
        'total_pacientes':  total_pacientes,
        'total_doctores':   total_doctores,
        'total_citas':      total_citas,
        'citas_por_estado': citas_por_estado,
    }