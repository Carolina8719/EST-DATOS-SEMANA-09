"""
services/paciente_service.py
Lógica de negocio para la entidad Paciente.
Sistema de Citas Médicas - Semana 15
"""

import sqlite3
import os
from models.paciente import Paciente


class PacienteService:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'citas_medicas.db')

    def __init__(self):
        self._pacientes = {}
        self._cargar()

    def _cargar(self):
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                for row in conn.execute("SELECT * FROM pacientes"):
                    p = Paciente(**dict(row))
                    self._pacientes[p.id_paciente] = p
        except Exception:
            pass

    def agregar(self, nombre, cedula, telefono, correo, fecha_nacimiento):
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pacientes (nombre, cedula, telefono, correo, fecha_nacimiento) "
                "VALUES (?, ?, ?, ?, ?)",
                (nombre, cedula, telefono, correo, fecha_nacimiento),
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
        p = Paciente(nuevo_id, nombre, cedula, telefono, correo, fecha_nacimiento)
        self._pacientes[nuevo_id] = p
        return p

    def obtener(self, id_paciente):
        return self._pacientes.get(id_paciente)

    def listar(self):
        return list(self._pacientes.values())

    def buscar_por_nombre(self, nombre):
        return [p for p in self._pacientes.values() if nombre.lower() in p.nombre.lower()]

    def actualizar(self, id_paciente, nombre, telefono, correo):
        if id_paciente not in self._pacientes:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                "UPDATE pacientes SET nombre=?, telefono=?, correo=? WHERE id_paciente=?",
                (nombre, telefono, correo, id_paciente),
            )
            conn.commit()
        p = self._pacientes[id_paciente]
        p.nombre   = nombre
        p.telefono = telefono
        p.correo   = correo
        return True

    def eliminar(self, id_paciente):
        if id_paciente not in self._pacientes:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas     WHERE id_paciente=?", (id_paciente,))
            conn.execute("DELETE FROM pacientes WHERE id_paciente=?", (id_paciente,))
            conn.commit()
        del self._pacientes[id_paciente]
        return True