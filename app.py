"""
Sistema de Citas Médicas - Semana 13
Persistencia con TXT, JSON, CSV, SQLAlchemy y MySQL
Autor: Carolina8719
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os

# ── SQLAlchemy (Semana 12) ──────────────────────────────────────────────
from inventario.bd import db, CitaRegistro
from inventario.productos import registrar_cita_completa, obtener_datos_archivos, obtener_datos_bd

# ── MySQL (Semana 13) ───────────────────────────────────────────────────
from conexion.mysql_crud import (
    insertar_usuario, obtener_usuarios,
    actualizar_usuario, eliminar_usuario,
    insertar_paciente_mysql, obtener_pacientes_mysql,
    obtener_paciente_mysql, actualizar_paciente_mysql, eliminar_paciente_mysql,
    insertar_doctor_mysql, obtener_doctores_mysql,
    obtener_doctor_mysql, actualizar_doctor_mysql, eliminar_doctor_mysql,
    insertar_cita_mysql, obtener_citas_detalle_mysql,
    actualizar_estado_cita_mysql, eliminar_cita_mysql,
    estadisticas_mysql,
)

app = Flask(__name__)
app.secret_key = 'citas_medicas_secret_key_2024'

# ── Configuración SQLAlchemy ────────────────────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(BASE_DIR, 'citas_sqlalchemy.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


# ============================================================
#  CAPA DE POO - CLASES DEL DOMINIO
# ============================================================

class Paciente:
    _ids_registrados = set()

    def __init__(self, id_paciente: int, nombre: str, cedula: str,
                 telefono: str, correo: str, fecha_nacimiento: str):
        self.__id_paciente      = id_paciente
        self.__nombre           = nombre
        self.__cedula           = cedula
        self.__telefono         = telefono
        self.__correo           = correo
        self.__fecha_nacimiento = fecha_nacimiento
        Paciente._ids_registrados.add(id_paciente)

    @property
    def id_paciente(self):      return self.__id_paciente
    @property
    def nombre(self):           return self.__nombre
    @property
    def cedula(self):           return self.__cedula
    @property
    def telefono(self):         return self.__telefono
    @property
    def correo(self):           return self.__correo
    @property
    def fecha_nacimiento(self): return self.__fecha_nacimiento

    @nombre.setter
    def nombre(self, valor):
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    @telefono.setter
    def telefono(self, valor):
        self.__telefono = valor.strip()

    @correo.setter
    def correo(self, valor):
        self.__correo = valor.strip()

    def to_dict(self) -> dict:
        return {
            "id_paciente":      self.__id_paciente,
            "nombre":           self.__nombre,
            "cedula":           self.__cedula,
            "telefono":         self.__telefono,
            "correo":           self.__correo,
            "fecha_nacimiento": self.__fecha_nacimiento,
        }

    def __repr__(self):
        return f"<Paciente id={self.__id_paciente} nombre='{self.__nombre}'>"


class Doctor:
    ESPECIALIDADES_VALIDAS = (
        "Medicina General", "Pediatría", "Cardiología",
        "Dermatología", "Ginecología", "Traumatología",
        "Neurología", "Oftalmología", "Psiquiatría", "Odontología"
    )

    def __init__(self, id_doctor: int, nombre: str, especialidad: str,
                 telefono: str, correo: str):
        self.__id_doctor    = id_doctor
        self.__nombre       = nombre
        self.__especialidad = especialidad
        self.__telefono     = telefono
        self.__correo       = correo

    @property
    def id_doctor(self):    return self.__id_doctor
    @property
    def nombre(self):       return self.__nombre
    @property
    def especialidad(self): return self.__especialidad
    @property
    def telefono(self):     return self.__telefono
    @property
    def correo(self):       return self.__correo

    @especialidad.setter
    def especialidad(self, valor):
        if valor not in Doctor.ESPECIALIDADES_VALIDAS:
            raise ValueError(f"Especialidad inválida.")
        self.__especialidad = valor

    def to_dict(self) -> dict:
        return {
            "id_doctor":    self.__id_doctor,
            "nombre":       self.__nombre,
            "especialidad": self.__especialidad,
            "telefono":     self.__telefono,
            "correo":       self.__correo,
        }

    def __repr__(self):
        return f"<Doctor id={self.__id_doctor} nombre='{self.__nombre}'>"


class Cita:
    ESTADOS = ["Pendiente", "Confirmada", "Completada", "Cancelada"]

    def __init__(self, id_cita: int, id_paciente: int, id_doctor: int,
                 fecha: str, hora: str, motivo: str, estado: str = "Pendiente"):
        self.__id_cita     = id_cita
        self.__id_paciente = id_paciente
        self.__id_doctor   = id_doctor
        self.__fecha       = fecha
        self.__hora        = hora
        self.__motivo      = motivo
        self.__estado      = estado if estado in Cita.ESTADOS else "Pendiente"

    @property
    def id_cita(self):     return self.__id_cita
    @property
    def id_paciente(self): return self.__id_paciente
    @property
    def id_doctor(self):   return self.__id_doctor
    @property
    def fecha(self):       return self.__fecha
    @property
    def hora(self):        return self.__hora
    @property
    def motivo(self):      return self.__motivo
    @property
    def estado(self):      return self.__estado

    @estado.setter
    def estado(self, valor):
        if valor not in Cita.ESTADOS:
            raise ValueError(f"Estado inválido.")
        self.__estado = valor

    def to_dict(self) -> dict:
        return {
            "id_cita":     self.__id_cita,
            "id_paciente": self.__id_paciente,
            "id_doctor":   self.__id_doctor,
            "fecha":       self.__fecha,
            "hora":        self.__hora,
            "motivo":      self.__motivo,
            "estado":      self.__estado,
        }

    def __repr__(self):
        return f"<Cita id={self.__id_cita} fecha='{self.__fecha}'>"


# ============================================================
#  GESTOR
# ============================================================

class GestorInventario:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'citas_medicas.db')

    def __init__(self):
        self._pacientes: dict[int, Paciente] = {}
        self._doctores:  dict[int, Doctor]   = {}
        self._citas:     dict[int, Cita]     = {}
        self._inicializar_db()
        self._cargar_datos()

    def _inicializar_db(self):
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id_paciente      INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre           TEXT    NOT NULL,
                    cedula           TEXT    UNIQUE NOT NULL,
                    telefono         TEXT,
                    correo           TEXT,
                    fecha_nacimiento TEXT
                );
                CREATE TABLE IF NOT EXISTS doctores (
                    id_doctor    INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre       TEXT NOT NULL,
                    especialidad TEXT NOT NULL,
                    telefono     TEXT,
                    correo       TEXT
                );
                CREATE TABLE IF NOT EXISTS citas (
                    id_cita     INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_paciente INTEGER NOT NULL,
                    id_doctor   INTEGER NOT NULL,
                    fecha       TEXT    NOT NULL,
                    hora        TEXT    NOT NULL,
                    motivo      TEXT,
                    estado      TEXT    DEFAULT 'Pendiente',
                    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
                    FOREIGN KEY (id_doctor)   REFERENCES doctores(id_doctor)
                );
            """)
            conn.commit()

    def _cargar_datos(self):
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            for row in cursor.execute("SELECT * FROM pacientes"):
                p = Paciente(**dict(row))
                self._pacientes[p.id_paciente] = p
            for row in cursor.execute("SELECT * FROM doctores"):
                d = Doctor(**dict(row))
                self._doctores[d.id_doctor] = d
            for row in cursor.execute("SELECT * FROM citas"):
                c = Cita(**dict(row))
                self._citas[c.id_cita] = c

    def agregar_paciente(self, nombre, cedula, telefono, correo, fecha_nacimiento):
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pacientes (nombre,cedula,telefono,correo,fecha_nacimiento) VALUES (?,?,?,?,?)",
                (nombre, cedula, telefono, correo, fecha_nacimiento)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
        p = Paciente(nuevo_id, nombre, cedula, telefono, correo, fecha_nacimiento)
        self._pacientes[nuevo_id] = p
        return p

    def obtener_paciente(self, id_paciente):
        return self._pacientes.get(id_paciente)

    def listar_pacientes(self):
        return list(self._pacientes.values())

    def buscar_pacientes_por_nombre(self, nombre):
        nombre_lower = nombre.lower()
        return [p for p in self._pacientes.values() if nombre_lower in p.nombre.lower()]

    def actualizar_paciente(self, id_paciente, nombre, telefono, correo):
        if id_paciente not in self._pacientes:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                "UPDATE pacientes SET nombre=?,telefono=?,correo=? WHERE id_paciente=?",
                (nombre, telefono, correo, id_paciente)
            )
            conn.commit()
        p = self._pacientes[id_paciente]
        p.nombre = nombre; p.telefono = telefono; p.correo = correo
        return True

    def eliminar_paciente(self, id_paciente):
        if id_paciente not in self._pacientes:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas     WHERE id_paciente=?", (id_paciente,))
            conn.execute("DELETE FROM pacientes WHERE id_paciente=?", (id_paciente,))
            conn.commit()
        citas_a_borrar = [cid for cid, c in self._citas.items() if c.id_paciente == id_paciente]
        for cid in citas_a_borrar:
            del self._citas[cid]
        del self._pacientes[id_paciente]
        return True

    def agregar_doctor(self, nombre, especialidad, telefono, correo):
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO doctores (nombre,especialidad,telefono,correo) VALUES (?,?,?,?)",
                (nombre, especialidad, telefono, correo)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
        d = Doctor(nuevo_id, nombre, especialidad, telefono, correo)
        self._doctores[nuevo_id] = d
        return d

    def listar_doctores(self):
        return list(self._doctores.values())

    def obtener_doctor(self, id_doctor):
        return self._doctores.get(id_doctor)

    def actualizar_doctor(self, id_doctor, nombre, especialidad, telefono, correo):
        if id_doctor not in self._doctores:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                "UPDATE doctores SET nombre=?,especialidad=?,telefono=?,correo=? WHERE id_doctor=?",
                (nombre, especialidad, telefono, correo, id_doctor)
            )
            conn.commit()
        self._doctores[id_doctor] = Doctor(id_doctor, nombre, especialidad, telefono, correo)
        return True

    def eliminar_doctor(self, id_doctor):
        if id_doctor not in self._doctores:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas    WHERE id_doctor=?", (id_doctor,))
            conn.execute("DELETE FROM doctores WHERE id_doctor=?", (id_doctor,))
            conn.commit()
        citas_a_borrar = [cid for cid, c in self._citas.items() if c.id_doctor == id_doctor]
        for cid in citas_a_borrar:
            del self._citas[cid]
        del self._doctores[id_doctor]
        return True

    def agendar_cita(self, id_paciente, id_doctor, fecha, hora, motivo):
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO citas (id_paciente,id_doctor,fecha,hora,motivo,estado) VALUES (?,?,?,?,?,'Pendiente')",
                (id_paciente, id_doctor, fecha, hora, motivo)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
        c = Cita(nuevo_id, id_paciente, id_doctor, fecha, hora, motivo)
        self._citas[nuevo_id] = c
        return c

    def listar_citas_detalle(self):
        resultado = []
        for cita in self._citas.values():
            paciente = self._pacientes.get(cita.id_paciente)
            doctor   = self._doctores.get(cita.id_doctor)
            item = cita.to_dict()
            item["nombre_paciente"] = paciente.nombre if paciente else "N/A"
            item["nombre_doctor"]   = doctor.nombre   if doctor   else "N/A"
            item["especialidad"]    = doctor.especialidad if doctor else "N/A"
            resultado.append(item)
        resultado.sort(key=lambda x: (x["fecha"], x["hora"]))
        return resultado

    def actualizar_estado_cita(self, id_cita, nuevo_estado):
        if id_cita not in self._citas or nuevo_estado not in Cita.ESTADOS:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("UPDATE citas SET estado=? WHERE id_cita=?", (nuevo_estado, id_cita))
            conn.commit()
        self._citas[id_cita].estado = nuevo_estado
        return True

    def eliminar_cita(self, id_cita):
        if id_cita not in self._citas:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas WHERE id_cita=?", (id_cita,))
            conn.commit()
        del self._citas[id_cita]
        return True

    def estadisticas(self):
        especialidades_activas = {
            self._doctores[c.id_doctor].especialidad
            for c in self._citas.values()
            if c.id_doctor in self._doctores
        }
        conteo_estados = {estado: 0 for estado in Cita.ESTADOS}
        for c in self._citas.values():
            conteo_estados[c.estado] = conteo_estados.get(c.estado, 0) + 1
        return {
            "total_pacientes":        len(self._pacientes),
            "total_doctores":         len(self._doctores),
            "total_citas":            len(self._citas),
            "especialidades_activas": list(especialidades_activas),
            "citas_por_estado":       conteo_estados,
        }


gestor = GestorInventario()


# ============================================================
#  RUTAS FLASK - Semana 11
# ============================================================

@app.route('/')
def index():
    stats = gestor.estadisticas()
    citas = gestor.listar_citas_detalle()[:5]
    return render_template('index.html', stats=stats, citas_recientes=citas)

@app.route('/pacientes')
def pacientes():
    busqueda = request.args.get('q', '').strip()
    lista = gestor.buscar_pacientes_por_nombre(busqueda) if busqueda else gestor.listar_pacientes()
    return render_template('pacientes/lista.html',
                           pacientes=[p.to_dict() for p in lista], busqueda=busqueda)

@app.route('/pacientes/nuevo', methods=['GET', 'POST'])
def paciente_nuevo():
    if request.method == 'POST':
        try:
            gestor.agregar_paciente(
                nombre=request.form['nombre'], cedula=request.form['cedula'],
                telefono=request.form['telefono'], correo=request.form['correo'],
                fecha_nacimiento=request.form['fecha_nacimiento'],
            )
            flash('✅ Paciente registrado correctamente.', 'success')
            return redirect(url_for('pacientes'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('pacientes/formulario.html', paciente=None, accion='Registrar')

@app.route('/pacientes/editar/<int:id>', methods=['GET', 'POST'])
def paciente_editar(id):
    paciente = gestor.obtener_paciente(id)
    if not paciente:
        flash('Paciente no encontrado.', 'warning')
        return redirect(url_for('pacientes'))
    if request.method == 'POST':
        try:
            gestor.actualizar_paciente(id_paciente=id, nombre=request.form['nombre'],
                                       telefono=request.form['telefono'], correo=request.form['correo'])
            flash('✅ Paciente actualizado.', 'success')
            return redirect(url_for('pacientes'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('pacientes/formulario.html', paciente=paciente.to_dict(), accion='Actualizar')

@app.route('/pacientes/eliminar/<int:id>', methods=['POST'])
def paciente_eliminar(id):
    gestor.eliminar_paciente(id)
    flash('🗑️ Paciente eliminado.', 'success')
    return redirect(url_for('pacientes'))

@app.route('/doctores')
def doctores():
    return render_template('doctores/lista.html',
                           doctores=[d.to_dict() for d in gestor.listar_doctores()])

@app.route('/doctores/nuevo', methods=['GET', 'POST'])
def doctor_nuevo():
    if request.method == 'POST':
        try:
            gestor.agregar_doctor(nombre=request.form['nombre'],
                                  especialidad=request.form['especialidad'],
                                  telefono=request.form['telefono'],
                                  correo=request.form['correo'])
            flash('✅ Doctor registrado correctamente.', 'success')
            return redirect(url_for('doctores'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('doctores/formulario.html', doctor=None, accion='Registrar',
                           especialidades=Doctor.ESPECIALIDADES_VALIDAS)

@app.route('/doctores/editar/<int:id>', methods=['GET', 'POST'])
def doctor_editar(id):
    doctor = gestor.obtener_doctor(id)
    if not doctor:
        flash('Doctor no encontrado.', 'warning')
        return redirect(url_for('doctores'))
    if request.method == 'POST':
        try:
            gestor.actualizar_doctor(id_doctor=id, nombre=request.form['nombre'],
                                     especialidad=request.form['especialidad'],
                                     telefono=request.form['telefono'], correo=request.form['correo'])
            flash('✅ Doctor actualizado.', 'success')
            return redirect(url_for('doctores'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('doctores/formulario.html', doctor=doctor.to_dict(), accion='Actualizar',
                           especialidades=Doctor.ESPECIALIDADES_VALIDAS)

@app.route('/doctores/eliminar/<int:id>', methods=['POST'])
def doctor_eliminar(id):
    gestor.eliminar_doctor(id)
    flash('🗑️ Doctor eliminado.', 'success')
    return redirect(url_for('doctores'))

@app.route('/citas')
def citas():
    return render_template('citas/lista.html',
                           citas=gestor.listar_citas_detalle(), estados=Cita.ESTADOS)

@app.route('/citas/nueva', methods=['GET', 'POST'])
def cita_nueva():
    if request.method == 'POST':
        try:
            gestor.agendar_cita(
                id_paciente=int(request.form['id_paciente']),
                id_doctor=int(request.form['id_doctor']),
                fecha=request.form['fecha'], hora=request.form['hora'],
                motivo=request.form['motivo'],
            )
            flash('✅ Cita agendada correctamente.', 'success')
            return redirect(url_for('citas'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('citas/formulario.html',
                           pacientes=[p.to_dict() for p in gestor.listar_pacientes()],
                           doctores=[d.to_dict() for d in gestor.listar_doctores()])

@app.route('/citas/estado/<int:id>', methods=['POST'])
def cita_estado(id):
    nuevo_estado = request.form.get('estado')
    gestor.actualizar_estado_cita(id, nuevo_estado)
    flash(f'✅ Estado actualizado a "{nuevo_estado}".', 'success')
    return redirect(url_for('citas'))

@app.route('/citas/eliminar/<int:id>', methods=['POST'])
def cita_eliminar(id):
    gestor.eliminar_cita(id)
    flash('🗑️ Cita eliminada.', 'success')
    return redirect(url_for('citas'))

@app.route('/api/estadisticas')
def api_estadisticas():
    return jsonify(gestor.estadisticas())


# ============================================================
#  RUTAS FLASK - Semana 12
# ============================================================

@app.route('/datos')
def datos_ver():
    archivos = obtener_datos_archivos()
    datos_bd = obtener_datos_bd()
    return render_template('datos.html',
        datos_txt=archivos['txt'],
        datos_json=archivos['json'],
        datos_csv=archivos['csv'],
        datos_bd=datos_bd,
        especialidades=Doctor.ESPECIALIDADES_VALIDAS,
    )

@app.route('/datos/guardar', methods=['POST'])
def datos_guardar():
    try:
        registrar_cita_completa(
            nombre       = request.form['nombre'],
            cedula       = request.form['cedula'],
            doctor       = request.form['doctor'],
            especialidad = request.form['especialidad'],
            fecha        = request.form['fecha'],
            hora         = request.form['hora'],
            motivo       = request.form.get('motivo', ''),
        )
        flash('✅ Cita guardada en TXT, JSON, CSV y SQLite.', 'success')
    except Exception as e:
        flash(f'❌ Error: {e}', 'danger')
    return redirect(url_for('datos_ver'))


# ============================================================
#  RUTAS FLASK - Semana 13 - MySQL
# ============================================================

# ── USUARIOS ───────────────────────────────────────────────

@app.route('/mysql/usuarios')
def mysql_usuarios():
    usuarios = obtener_usuarios()
    return render_template('mysql/usuarios/lista.html', usuarios=usuarios)

@app.route('/mysql/usuarios/nuevo', methods=['GET', 'POST'])
def mysql_usuario_nuevo():
    ROLES = ['admin', 'recepcionista', 'medico']
    if request.method == 'POST':
        try:
            insertar_usuario(
                nombre   = request.form['nombre'],
                mail     = request.form['mail'],
                password = request.form['password'],
                rol      = request.form.get('rol', 'recepcionista'),
            )
            flash('✅ Usuario creado en MySQL.', 'success')
            return redirect(url_for('mysql_usuarios'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('mysql/usuarios/formulario.html',
                           usuario=None, accion='Registrar', roles=ROLES)

@app.route('/mysql/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def mysql_usuario_editar(id):
    ROLES = ['admin', 'recepcionista', 'medico']
    usuarios = obtener_usuarios()
    usuario  = next((u for u in usuarios if u['id_usuario'] == id), None)
    if not usuario:
        flash('Usuario no encontrado.', 'warning')
        return redirect(url_for('mysql_usuarios'))
    if request.method == 'POST':
        try:
            actualizar_usuario(
                id_usuario = id,
                nombre     = request.form['nombre'],
                mail       = request.form['mail'],
                rol        = request.form.get('rol', 'recepcionista'),
            )
            flash('✅ Usuario actualizado.', 'success')
            return redirect(url_for('mysql_usuarios'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('mysql/usuarios/formulario.html',
                           usuario=usuario, accion='Actualizar', roles=ROLES)

@app.route('/mysql/usuarios/eliminar/<int:id>', methods=['POST'])
def mysql_usuario_eliminar(id):
    eliminar_usuario(id)
    flash('🗑️ Usuario eliminado.', 'success')
    return redirect(url_for('mysql_usuarios'))


# ── PACIENTES MySQL ────────────────────────────────────────

@app.route('/mysql/pacientes')
def mysql_pacientes():
    pacientes = obtener_pacientes_mysql()
    return render_template('mysql/pacientes/lista.html', pacientes=pacientes)

@app.route('/mysql/pacientes/nuevo', methods=['GET', 'POST'])
def mysql_paciente_nuevo():
    if request.method == 'POST':
        try:
            insertar_paciente_mysql(
                nombre           = request.form['nombre'],
                cedula           = request.form['cedula'],
                telefono         = request.form['telefono'],
                correo           = request.form['correo'],
                fecha_nacimiento = request.form['fecha_nacimiento'],
            )
            flash('✅ Paciente guardado en MySQL.', 'success')
            return redirect(url_for('mysql_pacientes'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('mysql/pacientes/formulario.html',
                           paciente=None, accion='Registrar')

@app.route('/mysql/pacientes/editar/<int:id>', methods=['GET', 'POST'])
def mysql_paciente_editar(id):
    paciente = obtener_paciente_mysql(id)
    if not paciente:
        flash('Paciente no encontrado.', 'warning')
        return redirect(url_for('mysql_pacientes'))
    if request.method == 'POST':
        try:
            actualizar_paciente_mysql(
                id_paciente = id,
                nombre      = request.form['nombre'],
                telefono    = request.form['telefono'],
                correo      = request.form['correo'],
            )
            flash('✅ Paciente actualizado en MySQL.', 'success')
            return redirect(url_for('mysql_pacientes'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('mysql/pacientes/formulario.html',
                           paciente=paciente, accion='Actualizar')

@app.route('/mysql/pacientes/eliminar/<int:id>', methods=['POST'])
def mysql_paciente_eliminar(id):
    eliminar_paciente_mysql(id)
    flash('🗑️ Paciente eliminado de MySQL.', 'success')
    return redirect(url_for('mysql_pacientes'))


# ── DOCTORES MySQL ─────────────────────────────────────────

@app.route('/mysql/doctores')
def mysql_doctores():
    doctores = obtener_doctores_mysql()
    return render_template('mysql/doctores/lista.html', doctores=doctores)

@app.route('/mysql/doctores/nuevo', methods=['GET', 'POST'])
def mysql_doctor_nuevo():
    if request.method == 'POST':
        try:
            insertar_doctor_mysql(
                nombre       = request.form['nombre'],
                especialidad = request.form['especialidad'],
                telefono     = request.form['telefono'],
                correo       = request.form['correo'],
            )
            flash('✅ Doctor guardado en MySQL.', 'success')
            return redirect(url_for('mysql_doctores'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('mysql/doctores/formulario.html',
                           doctor=None, accion='Registrar',
                           especialidades=Doctor.ESPECIALIDADES_VALIDAS)

@app.route('/mysql/doctores/editar/<int:id>', methods=['GET', 'POST'])
def mysql_doctor_editar(id):
    doctor = obtener_doctor_mysql(id)
    if not doctor:
        flash('Doctor no encontrado.', 'warning')
        return redirect(url_for('mysql_doctores'))
    if request.method == 'POST':
        try:
            actualizar_doctor_mysql(
                id_doctor    = id,
                nombre       = request.form['nombre'],
                especialidad = request.form['especialidad'],
                telefono     = request.form['telefono'],
                correo       = request.form['correo'],
            )
            flash('✅ Doctor actualizado en MySQL.', 'success')
            return redirect(url_for('mysql_doctores'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('mysql/doctores/formulario.html',
                           doctor=doctor, accion='Actualizar',
                           especialidades=Doctor.ESPECIALIDADES_VALIDAS)

@app.route('/mysql/doctores/eliminar/<int:id>', methods=['POST'])
def mysql_doctor_eliminar(id):
    eliminar_doctor_mysql(id)
    flash('🗑️ Doctor eliminado de MySQL.', 'success')
    return redirect(url_for('mysql_doctores'))


# ── CITAS MySQL ────────────────────────────────────────────

@app.route('/mysql/citas')
def mysql_citas():
    citas = obtener_citas_detalle_mysql()
    return render_template('mysql/citas/lista.html',
                           citas=citas, estados=Cita.ESTADOS)

@app.route('/mysql/citas/nueva', methods=['GET', 'POST'])
def mysql_cita_nueva():
    if request.method == 'POST':
        try:
            insertar_cita_mysql(
                id_paciente = int(request.form['id_paciente']),
                id_doctor   = int(request.form['id_doctor']),
                fecha       = request.form['fecha'],
                hora        = request.form['hora'],
                motivo      = request.form['motivo'],
            )
            flash('✅ Cita agendada en MySQL.', 'success')
            return redirect(url_for('mysql_citas'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('mysql/citas/formulario.html',
                           pacientes=obtener_pacientes_mysql(),
                           doctores=obtener_doctores_mysql())

@app.route('/mysql/citas/estado/<int:id>', methods=['POST'])
def mysql_cita_estado(id):
    nuevo_estado = request.form.get('estado')
    actualizar_estado_cita_mysql(id, nuevo_estado)
    flash(f'✅ Estado actualizado a "{nuevo_estado}".', 'success')
    return redirect(url_for('mysql_citas'))

@app.route('/mysql/citas/eliminar/<int:id>', methods=['POST'])
def mysql_cita_eliminar(id):
    eliminar_cita_mysql(id)
    flash('🗑️ Cita eliminada de MySQL.', 'success')
    return redirect(url_for('mysql_citas'))

@app.route('/api/mysql/estadisticas')
def api_mysql_estadisticas():
    return jsonify(estadisticas_mysql())


if __name__ == '__main__':
    app.run(debug=True)