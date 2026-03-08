from inventario.inventario import guardar_en_archivos, leer_txt, leer_json, leer_csv
from inventario.bd import db, CitaRegistro

def registrar_cita_completa(nombre, cedula, doctor, especialidad, fecha, hora, motivo, estado='Pendiente'):
    registro = {
        "nombre": nombre, "cedula": cedula,
        "doctor": doctor, "especialidad": especialidad,
        "fecha": fecha, "hora": hora,
        "motivo": motivo, "estado": estado,
    }
    guardar_en_archivos(registro)

    nueva = CitaRegistro(**registro)
    db.session.add(nueva)
    db.session.commit()
    return nueva

def obtener_datos_archivos():
    return {
        "txt":  leer_txt(),
        "json": leer_json(),
        "csv":  leer_csv(),
    }

def obtener_datos_bd():
    return [c.to_dict() for c in CitaRegistro.query.order_by(CitaRegistro.id.desc()).all()]