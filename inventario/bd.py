from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CitaRegistro(db.Model):
    __tablename__ = 'citas_registro'

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre       = db.Column(db.String(120), nullable=False)
    cedula       = db.Column(db.String(20),  nullable=False)
    doctor       = db.Column(db.String(120), nullable=False)
    especialidad = db.Column(db.String(80),  nullable=False)
    fecha        = db.Column(db.String(20),  nullable=False)
    hora         = db.Column(db.String(10),  nullable=False)
    motivo       = db.Column(db.String(255), nullable=True)
    estado       = db.Column(db.String(30),  default='Pendiente')

    def to_dict(self):
        return {
            "id": self.id, "nombre": self.nombre,
            "cedula": self.cedula, "doctor": self.doctor,
            "especialidad": self.especialidad, "fecha": self.fecha,
            "hora": self.hora, "motivo": self.motivo, "estado": self.estado,
        }