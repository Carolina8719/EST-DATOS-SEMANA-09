"""
forms/doctor_form.py
Validación de formularios para Doctor.
Sistema de Citas Médicas - Semana 15
"""

ESPECIALIDADES_VALIDAS = (
    "Medicina General", "Pediatría", "Cardiología", "Dermatología",
    "Ginecología", "Traumatología", "Neurología", "Oftalmología",
    "Psiquiatría", "Odontología",
)


class DoctorForm:

    def __init__(self, data: dict):
        self.nombre       = data.get('nombre', '').strip()
        self.especialidad = data.get('especialidad', '').strip()
        self.telefono     = data.get('telefono', '').strip()
        self.correo       = data.get('correo', '').strip()
        self.errors       = []

    def validar(self) -> bool:
        self.errors = []
        if not self.nombre:
            self.errors.append("El nombre es obligatorio.")
        if not self.especialidad:
            self.errors.append("La especialidad es obligatoria.")
        if self.especialidad not in ESPECIALIDADES_VALIDAS:
            self.errors.append("La especialidad seleccionada no es válida.")
        if self.correo and '@' not in self.correo:
            self.errors.append("El correo no tiene un formato válido.")
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "nombre":       self.nombre,
            "especialidad": self.especialidad,
            "telefono":     self.telefono,
            "correo":       self.correo,
        }