"""
models/doctor.py
Modelo de datos para la entidad Doctor.
Sistema de Citas Médicas - Semana 15
"""


class Doctor:
    ESPECIALIDADES_VALIDAS = (
        "Medicina General", "Pediatría", "Cardiología", "Dermatología",
        "Ginecología", "Traumatología", "Neurología", "Oftalmología",
        "Psiquiatría", "Odontología",
    )

    def __init__(self, id_doctor, nombre, especialidad, telefono, correo):
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
            raise ValueError("Especialidad inválida.")
        self.__especialidad = valor

    def to_dict(self):
        return {
            "id_doctor":    self.__id_doctor,
            "nombre":       self.__nombre,
            "especialidad": self.__especialidad,
            "telefono":     self.__telefono,
            "correo":       self.__correo,
        }

    def __repr__(self):
        return f"<Doctor id={self.__id_doctor} nombre='{self.__nombre}'>"