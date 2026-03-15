"""
Script de creación de tablas MySQL - Semana 13
Sistema de Citas Médicas
Autor: Carolina8719

Ejecutar UNA VEZ para inicializar la base de datos MySQL.
    python conexion/crear_tablas.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conexion.conexion import get_connection

TABLAS_SQL = [
    # ── Tabla requerida por la tarea ───────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario  INT          AUTO_INCREMENT PRIMARY KEY,
        nombre      VARCHAR(100) NOT NULL,
        mail        VARCHAR(150) NOT NULL UNIQUE,
        password    VARCHAR(255) NOT NULL,
        rol         ENUM('admin','recepcionista','medico') DEFAULT 'recepcionista',
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    # ── Pacientes ──────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS pacientes (
        id_paciente      INT          AUTO_INCREMENT PRIMARY KEY,
        nombre           VARCHAR(100) NOT NULL,
        cedula           VARCHAR(20)  NOT NULL UNIQUE,
        telefono         VARCHAR(20),
        correo           VARCHAR(150),
        fecha_nacimiento DATE,
        created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    # ── Doctores ───────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS doctores (
        id_doctor    INT          AUTO_INCREMENT PRIMARY KEY,
        nombre       VARCHAR(100) NOT NULL,
        especialidad VARCHAR(80)  NOT NULL,
        telefono     VARCHAR(20),
        correo       VARCHAR(150),
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,

    # ── Citas ──────────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS citas (
        id_cita     INT  AUTO_INCREMENT PRIMARY KEY,
        id_paciente INT  NOT NULL,
        id_doctor   INT  NOT NULL,
        fecha       DATE NOT NULL,
        hora        TIME NOT NULL,
        motivo      TEXT,
        estado      ENUM('Pendiente','Confirmada','Completada','Cancelada')
                    DEFAULT 'Pendiente',
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_cita_paciente FOREIGN KEY (id_paciente)
            REFERENCES pacientes(id_paciente) ON DELETE CASCADE,
        CONSTRAINT fk_cita_doctor FOREIGN KEY (id_doctor)
            REFERENCES doctores(id_doctor) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
]


def crear_tablas():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        nombres = ['usuarios', 'pacientes', 'doctores', 'citas']
        for sql, nombre in zip(TABLAS_SQL, nombres):
            cursor.execute(sql)
            print(f"✅ Tabla '{nombre}' creada / verificada.")
        conn.commit()
        cursor.close()
        conn.close()
        print("\n🎉 Todas las tablas están listas.")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")


if __name__ == '__main__':
    crear_tablas()