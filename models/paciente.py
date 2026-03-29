"""
models/paciente.py
Modelo de datos para la entidad Paciente.
Sistema de Citas Médicas - Semana 15
"""


class Paciente:
    _ids_registrados = set()

    def __init__(self, id_paciente, nombre, cedula, telefono, correo, fecha_nacimiento):
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
    def telefono(self, valor): self.__telefono = valor.strip()

    @correo.setter
    def correo(self, valor): self.__correo = valor.strip()

    def to_dict(self):
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