"""
forms/paciente_form.py
Validación de formularios para Paciente.
Sistema de Citas Médicas - Semana 15
"""


class PacienteForm:

    def __init__(self, data: dict):
        self.nombre           = data.get('nombre', '').strip()
        self.cedula           = data.get('cedula', '').strip()
        self.telefono         = data.get('telefono', '').strip()
        self.correo           = data.get('correo', '').strip()
        self.fecha_nacimiento = data.get('fecha_nacimiento', '').strip()
        self.errors           = []

    def validar(self) -> bool:
        self.errors = []
        if not self.nombre:
            self.errors.append("El nombre es obligatorio.")
        if not self.cedula:
            self.errors.append("La cédula es obligatoria.")
        if len(self.cedula) < 6:
            self.errors.append("La cédula debe tener al menos 6 caracteres.")
        if self.correo and '@' not in self.correo:
            self.errors.append("El correo no tiene un formato válido.")
        if not self.fecha_nacimiento:
            self.errors.append("La fecha de nacimiento es obligatoria.")
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "nombre":           self.nombre,
            "cedula":           self.cedula,
            "telefono":         self.telefono,
            "correo":           self.correo,
            "fecha_nacimiento": self.fecha_nacimiento,
        }