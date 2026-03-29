"""
forms/cita_form.py
Validación de formularios para Cita.
Sistema de Citas Médicas - Semana 15
"""

from datetime import date


class CitaForm:

    def __init__(self, data: dict):
        self.id_paciente = data.get('id_paciente', '')
        self.id_doctor   = data.get('id_doctor', '')
        self.fecha       = data.get('fecha', '').strip()
        self.hora        = data.get('hora', '').strip()
        self.motivo      = data.get('motivo', '').strip()
        self.errors      = []

    def validar(self) -> bool:
        self.errors = []
        if not self.id_paciente:
            self.errors.append("Debe seleccionar un paciente.")
        if not self.id_doctor:
            self.errors.append("Debe seleccionar un doctor.")
        if not self.fecha:
            self.errors.append("La fecha es obligatoria.")
        else:
            try:
                fecha_obj = date.fromisoformat(self.fecha)
                if fecha_obj < date.today():
                    self.errors.append("La fecha no puede ser en el pasado.")
            except ValueError:
                self.errors.append("La fecha no tiene un formato válido.")
        if not self.hora:
            self.errors.append("La hora es obligatoria.")
        if not self.motivo:
            self.errors.append("El motivo de la cita es obligatorio.")
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "id_paciente": int(self.id_paciente),
            "id_doctor":   int(self.id_doctor),
            "fecha":       self.fecha,
            "hora":        self.hora,
            "motivo":      self.motivo,
        }