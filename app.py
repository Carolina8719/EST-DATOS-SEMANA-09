"""
Sistema de Citas Médicas - Semana 11
Integración de POO, Colecciones, SQLite y CRUD
Autor: Carolina8719
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'citas_medicas_secret_key_2024'

# ============================================================
#  CAPA DE POO - CLASES DEL DOMINIO
# ============================================================

class Paciente:
    """
    Clase que representa a un paciente del sistema.
    Utiliza atributos privados con getters y setters (encapsulamiento).
    """

    # Conjunto para rastrear IDs únicos en memoria (colección: set)
    _ids_registrados = set()

    def __init__(self, id_paciente: int, nombre: str, cedula: str,
                 telefono: str, correo: str, fecha_nacimiento: str):
        self.__id_paciente     = id_paciente
        self.__nombre          = nombre
        self.__cedula          = cedula
        self.__telefono        = telefono
        self.__correo          = correo
        self.__fecha_nacimiento = fecha_nacimiento
        Paciente._ids_registrados.add(id_paciente)

    # --- Getters ---
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

    # --- Setters ---
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
        """Convierte el paciente a diccionario (colección: dict)."""
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
    """
    Clase que representa a un médico del sistema.
    """

    # Tupla con especialidades válidas (colección inmutable: tuple)
    ESPECIALIDADES_VALIDAS = (
        "Medicina General", "Pediatría", "Cardiología",
        "Dermatología", "Ginecología", "Traumatología",
        "Neurología", "Oftalmología", "Psiquiatría", "Odontología"
    )

    def __init__(self, id_doctor: int, nombre: str, especialidad: str,
                 telefono: str, correo: str):
        self.__id_doctor   = id_doctor
        self.__nombre      = nombre
        self.__especialidad = especialidad
        self.__telefono    = telefono
        self.__correo      = correo

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
            raise ValueError(f"Especialidad inválida. Opciones: {Doctor.ESPECIALIDADES_VALIDAS}")
        self.__especialidad = valor

    def to_dict(self) -> dict:
        return {
            "id_doctor":   self.__id_doctor,
            "nombre":      self.__nombre,
            "especialidad": self.__especialidad,
            "telefono":    self.__telefono,
            "correo":      self.__correo,
        }

    def __repr__(self):
        return f"<Doctor id={self.__id_doctor} nombre='{self.__nombre}' esp='{self.__especialidad}'>"


class Cita:
    """
    Clase que representa una cita médica.
    Relaciona un paciente con un doctor en una fecha/hora específica.
    """

    # Lista de estados posibles (colección: list)
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
            raise ValueError(f"Estado inválido. Opciones: {Cita.ESTADOS}")
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
        return f"<Cita id={self.__id_cita} fecha='{self.__fecha}' estado='{self.__estado}'>"


# ============================================================
#  CAPA DE REPOSITORIO - GESTIÓN CON COLECCIONES + SQLITE
# ============================================================

class GestorInventario:
    """
    Clase principal que gestiona el inventario del sistema de citas.
    Utiliza diccionarios como colección principal para búsqueda O(1).
    Conecta con SQLite para persistencia de datos.
    """

    DB_PATH = os.path.join(os.path.dirname(__file__), 'citas_medicas.db')

    def __init__(self):
        # Diccionarios en memoria para acceso rápido (colección: dict)
        self._pacientes: dict[int, Paciente] = {}
        self._doctores:  dict[int, Doctor]   = {}
        self._citas:     dict[int, Cita]     = {}
        self._inicializar_db()
        self._cargar_datos()

    # ---- Inicialización de base de datos ----
    def _inicializar_db(self):
        """Crea las tablas si no existen."""
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
        """Carga todos los registros de SQLite a los diccionarios en memoria."""
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

    # ==========================
    #  CRUD PACIENTES
    # ==========================

    def agregar_paciente(self, nombre, cedula, telefono, correo, fecha_nacimiento) -> Paciente:
        """CREATE - Inserta un paciente en SQLite y en el diccionario."""
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pacientes (nombre, cedula, telefono, correo, fecha_nacimiento) "
                "VALUES (?, ?, ?, ?, ?)",
                (nombre, cedula, telefono, correo, fecha_nacimiento)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid

        p = Paciente(nuevo_id, nombre, cedula, telefono, correo, fecha_nacimiento)
        self._pacientes[nuevo_id] = p
        return p

    def obtener_paciente(self, id_paciente: int):
        """READ - Retorna un paciente por ID desde el diccionario (O(1))."""
        return self._pacientes.get(id_paciente)

    def listar_pacientes(self) -> list:
        """READ - Retorna lista de todos los pacientes."""
        return list(self._pacientes.values())

    def buscar_pacientes_por_nombre(self, nombre: str) -> list:
        """READ - Búsqueda por nombre (colección: list comprehension)."""
        nombre_lower = nombre.lower()
        return [p for p in self._pacientes.values()
                if nombre_lower in p.nombre.lower()]

    def actualizar_paciente(self, id_paciente, nombre, telefono, correo) -> bool:
        """UPDATE - Actualiza datos en SQLite y en el diccionario."""
        if id_paciente not in self._pacientes:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                "UPDATE pacientes SET nombre=?, telefono=?, correo=? WHERE id_paciente=?",
                (nombre, telefono, correo, id_paciente)
            )
            conn.commit()
        p = self._pacientes[id_paciente]
        p.nombre   = nombre
        p.telefono = telefono
        p.correo   = correo
        return True

    def eliminar_paciente(self, id_paciente: int) -> bool:
        """DELETE - Elimina paciente de SQLite y del diccionario."""
        if id_paciente not in self._pacientes:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas    WHERE id_paciente=?", (id_paciente,))
            conn.execute("DELETE FROM pacientes WHERE id_paciente=?", (id_paciente,))
            conn.commit()
        # Eliminar citas del dict también
        citas_a_borrar = [cid for cid, c in self._citas.items() if c.id_paciente == id_paciente]
        for cid in citas_a_borrar:
            del self._citas[cid]
        del self._pacientes[id_paciente]
        return True

    # ==========================
    #  CRUD DOCTORES
    # ==========================

    def agregar_doctor(self, nombre, especialidad, telefono, correo) -> Doctor:
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO doctores (nombre, especialidad, telefono, correo) VALUES (?, ?, ?, ?)",
                (nombre, especialidad, telefono, correo)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
        d = Doctor(nuevo_id, nombre, especialidad, telefono, correo)
        self._doctores[nuevo_id] = d
        return d

    def listar_doctores(self) -> list:
        return list(self._doctores.values())

    def obtener_doctor(self, id_doctor: int):
        return self._doctores.get(id_doctor)

    def actualizar_doctor(self, id_doctor, nombre, especialidad, telefono, correo) -> bool:
        if id_doctor not in self._doctores:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                "UPDATE doctores SET nombre=?, especialidad=?, telefono=?, correo=? WHERE id_doctor=?",
                (nombre, especialidad, telefono, correo, id_doctor)
            )
            conn.commit()
        d = self._doctores[id_doctor]
        self._doctores[id_doctor] = Doctor(id_doctor, nombre, especialidad, telefono, correo)
        return True

    def eliminar_doctor(self, id_doctor: int) -> bool:
        if id_doctor not in self._doctores:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas   WHERE id_doctor=?", (id_doctor,))
            conn.execute("DELETE FROM doctores WHERE id_doctor=?", (id_doctor,))
            conn.commit()
        citas_a_borrar = [cid for cid, c in self._citas.items() if c.id_doctor == id_doctor]
        for cid in citas_a_borrar:
            del self._citas[cid]
        del self._doctores[id_doctor]
        return True

    # ==========================
    #  CRUD CITAS
    # ==========================

    def agendar_cita(self, id_paciente, id_doctor, fecha, hora, motivo) -> Cita:
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO citas (id_paciente, id_doctor, fecha, hora, motivo, estado) "
                "VALUES (?, ?, ?, ?, ?, 'Pendiente')",
                (id_paciente, id_doctor, fecha, hora, motivo)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
        c = Cita(nuevo_id, id_paciente, id_doctor, fecha, hora, motivo)
        self._citas[nuevo_id] = c
        return c

    def listar_citas_detalle(self) -> list:
        """
        READ - Retorna citas enriquecidas con nombre de paciente y doctor.
        Utiliza list comprehension + dict lookup O(1).
        """
        resultado = []
        for cita in self._citas.values():
            paciente = self._pacientes.get(cita.id_paciente)
            doctor   = self._doctores.get(cita.id_doctor)
            item = cita.to_dict()
            item["nombre_paciente"]  = paciente.nombre if paciente else "N/A"
            item["nombre_doctor"]    = doctor.nombre   if doctor   else "N/A"
            item["especialidad"]     = doctor.especialidad if doctor else "N/A"
            resultado.append(item)
        # Ordenar por fecha y hora (tupla como clave de ordenamiento)
        resultado.sort(key=lambda x: (x["fecha"], x["hora"]))
        return resultado

    def actualizar_estado_cita(self, id_cita: int, nuevo_estado: str) -> bool:
        if id_cita not in self._citas or nuevo_estado not in Cita.ESTADOS:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("UPDATE citas SET estado=? WHERE id_cita=?", (nuevo_estado, id_cita))
            conn.commit()
        self._citas[id_cita].estado = nuevo_estado
        return True

    def eliminar_cita(self, id_cita: int) -> bool:
        if id_cita not in self._citas:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas WHERE id_cita=?", (id_cita,))
            conn.commit()
        del self._citas[id_cita]
        return True

    def estadisticas(self) -> dict:
        """Genera estadísticas usando conjuntos y conteos."""
        especialidades_activas = {
            self._doctores[c.id_doctor].especialidad
            for c in self._citas.values()
            if c.id_doctor in self._doctores
        }  # set comprehension
        conteo_estados = {estado: 0 for estado in Cita.ESTADOS}
        for c in self._citas.values():
            conteo_estados[c.estado] = conteo_estados.get(c.estado, 0) + 1

        return {
            "total_pacientes":       len(self._pacientes),
            "total_doctores":        len(self._doctores),
            "total_citas":           len(self._citas),
            "especialidades_activas": list(especialidades_activas),
            "citas_por_estado":      conteo_estados,
        }


# ============================================================
#  INSTANCIA GLOBAL DEL GESTOR
# ============================================================
gestor = GestorInventario()


# ============================================================
#  RUTAS FLASK
# ============================================================

@app.route('/')
def index():
    stats = gestor.estadisticas()
    citas = gestor.listar_citas_detalle()[:5]   # últimas 5 para el dashboard
    return render_template('index.html', stats=stats, citas_recientes=citas)


# ---------- PACIENTES ----------
@app.route('/pacientes')
def pacientes():
    busqueda = request.args.get('q', '').strip()
    if busqueda:
        lista = gestor.buscar_pacientes_por_nombre(busqueda)
    else:
        lista = gestor.listar_pacientes()
    return render_template('pacientes/lista.html',
                           pacientes=[p.to_dict() for p in lista],
                           busqueda=busqueda)

@app.route('/pacientes/nuevo', methods=['GET', 'POST'])
def paciente_nuevo():
    if request.method == 'POST':
        try:
            gestor.agregar_paciente(
                nombre           = request.form['nombre'],
                cedula           = request.form['cedula'],
                telefono         = request.form['telefono'],
                correo           = request.form['correo'],
                fecha_nacimiento = request.form['fecha_nacimiento'],
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
            gestor.actualizar_paciente(
                id_paciente = id,
                nombre      = request.form['nombre'],
                telefono    = request.form['telefono'],
                correo      = request.form['correo'],
            )
            flash('✅ Paciente actualizado.', 'success')
            return redirect(url_for('pacientes'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('pacientes/formulario.html',
                           paciente=paciente.to_dict(), accion='Actualizar')

@app.route('/pacientes/eliminar/<int:id>', methods=['POST'])
def paciente_eliminar(id):
    if gestor.eliminar_paciente(id):
        flash('🗑️ Paciente eliminado.', 'success')
    else:
        flash('❌ No se pudo eliminar el paciente.', 'danger')
    return redirect(url_for('pacientes'))


# ---------- DOCTORES ----------
@app.route('/doctores')
def doctores():
    lista = gestor.listar_doctores()
    return render_template('doctores/lista.html',
                           doctores=[d.to_dict() for d in lista])

@app.route('/doctores/nuevo', methods=['GET', 'POST'])
def doctor_nuevo():
    if request.method == 'POST':
        try:
            gestor.agregar_doctor(
                nombre       = request.form['nombre'],
                especialidad = request.form['especialidad'],
                telefono     = request.form['telefono'],
                correo       = request.form['correo'],
            )
            flash('✅ Doctor registrado correctamente.', 'success')
            return redirect(url_for('doctores'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('doctores/formulario.html',
                           doctor=None, accion='Registrar',
                           especialidades=Doctor.ESPECIALIDADES_VALIDAS)

@app.route('/doctores/editar/<int:id>', methods=['GET', 'POST'])
def doctor_editar(id):
    doctor = gestor.obtener_doctor(id)
    if not doctor:
        flash('Doctor no encontrado.', 'warning')
        return redirect(url_for('doctores'))
    if request.method == 'POST':
        try:
            gestor.actualizar_doctor(
                id_doctor    = id,
                nombre       = request.form['nombre'],
                especialidad = request.form['especialidad'],
                telefono     = request.form['telefono'],
                correo       = request.form['correo'],
            )
            flash('✅ Doctor actualizado.', 'success')
            return redirect(url_for('doctores'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    return render_template('doctores/formulario.html',
                           doctor=doctor.to_dict(), accion='Actualizar',
                           especialidades=Doctor.ESPECIALIDADES_VALIDAS)

@app.route('/doctores/eliminar/<int:id>', methods=['POST'])
def doctor_eliminar(id):
    if gestor.eliminar_doctor(id):
        flash('🗑️ Doctor eliminado.', 'success')
    else:
        flash('❌ No se pudo eliminar el doctor.', 'danger')
    return redirect(url_for('doctores'))


# ---------- CITAS ----------
@app.route('/citas')
def citas():
    lista  = gestor.listar_citas_detalle()
    return render_template('citas/lista.html',
                           citas=lista, estados=Cita.ESTADOS)

@app.route('/citas/nueva', methods=['GET', 'POST'])
def cita_nueva():
    if request.method == 'POST':
        try:
            gestor.agendar_cita(
                id_paciente = int(request.form['id_paciente']),
                id_doctor   = int(request.form['id_doctor']),
                fecha       = request.form['fecha'],
                hora        = request.form['hora'],
                motivo      = request.form['motivo'],
            )
            flash('✅ Cita agendada correctamente.', 'success')
            return redirect(url_for('citas'))
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')
    pacientes_lista = [p.to_dict() for p in gestor.listar_pacientes()]
    doctores_lista  = [d.to_dict() for d in gestor.listar_doctores()]
    return render_template('citas/formulario.html',
                           pacientes=pacientes_lista,
                           doctores=doctores_lista)

@app.route('/citas/estado/<int:id>', methods=['POST'])
def cita_estado(id):
    nuevo_estado = request.form.get('estado')
    if gestor.actualizar_estado_cita(id, nuevo_estado):
        flash(f'✅ Estado actualizado a "{nuevo_estado}".', 'success')
    else:
        flash('❌ No se pudo actualizar el estado.', 'danger')
    return redirect(url_for('citas'))

@app.route('/citas/eliminar/<int:id>', methods=['POST'])
def cita_eliminar(id):
    if gestor.eliminar_cita(id):
        flash('🗑️ Cita eliminada.', 'success')
    else:
        flash('❌ No se pudo eliminar la cita.', 'danger')
    return redirect(url_for('citas'))

# ---------- API JSON (bonus) ----------
@app.route('/api/estadisticas')
def api_estadisticas():
    return jsonify(gestor.estadisticas())


if __name__ == '__main__':
    app.run(debug=True)
