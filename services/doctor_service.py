"""
services/doctor_service.py
Lógica de negocio para la entidad Doctor.
Sistema de Citas Médicas - Semana 15
"""

import sqlite3
import os
from models.doctor import Doctor


class DoctorService:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'citas_medicas.db')

    def __init__(self):
        self._doctores = {}
        self._cargar()

    def _cargar(self):
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                for row in conn.execute("SELECT * FROM doctores"):
                    d = Doctor(**dict(row))
                    self._doctores[d.id_doctor] = d
        except Exception:
            pass

    def agregar(self, nombre, especialidad, telefono, correo):
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO doctores (nombre, especialidad, telefono, correo) VALUES (?, ?, ?, ?)",
                (nombre, especialidad, telefono, correo),
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
        d = Doctor(nuevo_id, nombre, especialidad, telefono, correo)
        self._doctores[nuevo_id] = d
        return d

    def obtener(self, id_doctor):
        return self._doctores.get(id_doctor)

    def listar(self):
        return list(self._doctores.values())

    def actualizar(self, id_doctor, nombre, especialidad, telefono, correo):
        if id_doctor not in self._doctores:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                "UPDATE doctores SET nombre=?, especialidad=?, telefono=?, correo=? WHERE id_doctor=?",
                (nombre, especialidad, telefono, correo, id_doctor),
            )
            conn.commit()
        self._doctores[id_doctor] = Doctor(id_doctor, nombre, especialidad, telefono, correo)
        return True

    def eliminar(self, id_doctor):
        if id_doctor not in self._doctores:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas    WHERE id_doctor=?", (id_doctor,))
            conn.execute("DELETE FROM doctores WHERE id_doctor=?", (id_doctor,))
            conn.commit()
        del self._doctores[id_doctor]
        return True