"""
models/cita.py
Modelo de datos para la entidad Cita.
Sistema de Citas Médicas - Semana 15
"""


class Cita:
    ESTADOS = ["Pendiente", "Confirmada", "Completada", "Cancelada"]

    def __init__(self, id_cita, id_paciente, id_doctor, fecha, hora, motivo, estado="Pendiente"):
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
            raise ValueError("Estado inválido.")
        self.__estado = valor

    def to_dict(self):
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