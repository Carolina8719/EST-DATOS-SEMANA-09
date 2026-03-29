"""
services/cita_service.py
Lógica de negocio para la entidad Cita.
Sistema de Citas Médicas - Semana 15
"""

import sqlite3
import os
from models.cita import Cita


class CitaService:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'citas_medicas.db')

    def __init__(self, paciente_service, doctor_service):
        self._citas            = {}
        self._paciente_service = paciente_service
        self._doctor_service   = doctor_service
        self._cargar()

    def _cargar(self):
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                for row in conn.execute("SELECT * FROM citas"):
                    c = Cita(**dict(row))
                    self._citas[c.id_cita] = c
        except Exception:
            pass

    def agendar(self, id_paciente, id_doctor, fecha, hora, motivo):
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO citas (id_paciente, id_doctor, fecha, hora, motivo, estado) "
                "VALUES (?, ?, ?, ?, ?, 'Pendiente')",
                (id_paciente, id_doctor, fecha, hora, motivo),
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
        c = Cita(nuevo_id, id_paciente, id_doctor, fecha, hora, motivo)
        self._citas[nuevo_id] = c
        return c

    def listar_detalle(self):
        resultado = []
        for cita in self._citas.values():
            paciente = self._paciente_service.obtener(cita.id_paciente)
            doctor   = self._doctor_service.obtener(cita.id_doctor)
            item = cita.to_dict()
            item["nombre_paciente"] = paciente.nombre     if paciente else "N/A"
            item["nombre_doctor"]   = doctor.nombre       if doctor   else "N/A"
            item["especialidad"]    = doctor.especialidad if doctor   else "N/A"
            resultado.append(item)
        resultado.sort(key=lambda x: (x["fecha"], x["hora"]))
        return resultado

    def actualizar_estado(self, id_cita, nuevo_estado):
        if id_cita not in self._citas or nuevo_estado not in Cita.ESTADOS:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("UPDATE citas SET estado=? WHERE id_cita=?", (nuevo_estado, id_cita))
            conn.commit()
        self._citas[id_cita].estado = nuevo_estado
        return True

    def eliminar(self, id_cita):
        if id_cita not in self._citas:
            return False
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("DELETE FROM citas WHERE id_cita=?", (id_cita,))
            conn.commit()
        del self._citas[id_cita]
        return True

    def estadisticas(self):
        conteo_estados = {estado: 0 for estado in Cita.ESTADOS}
        especialidades_activas = set()
        for c in self._citas.values():
            conteo_estados[c.estado] = conteo_estados.get(c.estado, 0) + 1
            doctor = self._doctor_service.obtener(c.id_doctor)
            if doctor:
                especialidades_activas.add(doctor.especialidad)
        return {
            "total_pacientes":        len(self._paciente_service.listar()),
            "total_doctores":         len(self._doctor_service.listar()),
            "total_citas":            len(self._citas),
            "especialidades_activas": list(especialidades_activas),
            "citas_por_estado":       conteo_estados,
        }