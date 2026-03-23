from flask_login import UserMixin

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, mail, password, rol='recepcionista'):
        self.id       = id_usuario
        self.nombre   = nombre
        self.mail     = mail
        self.password = password
        self.rol      = rol

    def get_id(self):
        return str(self.id)