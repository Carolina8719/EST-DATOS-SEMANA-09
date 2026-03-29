"""
reportes/reporte_pdf.py
Generación de reportes en PDF con ReportLab.
Sistema de Citas Médicas - Semana 15
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable,
)


# ── Paleta de colores ──────────────────────────────────────
AZUL_OSCURO  = colors.HexColor("#1a3a5c")
AZUL_MEDIO   = colors.HexColor("#2980b9")
AZUL_CLARO   = colors.HexColor("#d6eaf8")
GRIS_TABLA   = colors.HexColor("#f2f3f4")
BLANCO       = colors.white
VERDE        = colors.HexColor("#1e8449")
ROJO         = colors.HexColor("#c0392b")
NARANJA      = colors.HexColor("#d35400")
GRIS_TEXTO   = colors.HexColor("#555555")


def generar_reporte_citas(citas: list, pacientes: list, doctores: list) -> bytes:
    """
    Genera un PDF con:
      1. Resumen estadístico
      2. Listado de citas
      3. Listado de pacientes
      4. Listado de doctores
    Retorna los bytes del PDF listo para enviar como respuesta Flask.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Reporte Sistema de Citas Médicas",
    )

    estilos = getSampleStyleSheet()
    elementos = []

    # ── Estilos ────────────────────────────────────────────
    estilo_titulo = ParagraphStyle(
        "titulo", parent=estilos["Title"],
        textColor=AZUL_OSCURO, fontSize=20, spaceAfter=4,
    )
    estilo_subtitulo = ParagraphStyle(
        "subtitulo", parent=estilos["Normal"],
        textColor=GRIS_TEXTO, fontSize=10, spaceAfter=2,
    )
    estilo_seccion = ParagraphStyle(
        "seccion", parent=estilos["Heading2"],
        textColor=AZUL_OSCURO, fontSize=13, spaceBefore=14, spaceAfter=6,
    )
    estilo_normal = ParagraphStyle(
        "normal", parent=estilos["Normal"],
        fontSize=9, textColor=GRIS_TEXTO,
    )

    # ── Encabezado ─────────────────────────────────────────
    elementos.append(Paragraph("Sistema de Citas Medicas", estilo_titulo))
    elementos.append(Paragraph(
        f"Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        estilo_subtitulo,
    ))
    elementos.append(HRFlowable(width="100%", thickness=2, color=AZUL_MEDIO, spaceAfter=10))

    # ── Resumen estadístico ────────────────────────────────
    elementos.append(Paragraph("Resumen Estadistico", estilo_seccion))

    from collections import Counter
    conteo_estados = Counter(c.get("estado", "") for c in citas)

    datos_resumen = [
        ["Indicador", "Valor"],
        ["Total de pacientes registrados", str(len(pacientes))],
        ["Total de doctores registrados",  str(len(doctores))],
        ["Total de citas agendadas",        str(len(citas))],
        ["Citas Pendientes",   str(conteo_estados.get("Pendiente",  0))],
        ["Citas Confirmadas",  str(conteo_estados.get("Confirmada", 0))],
        ["Citas Completadas",  str(conteo_estados.get("Completada", 0))],
        ["Citas Canceladas",   str(conteo_estados.get("Cancelada",  0))],
    ]
    tabla_resumen = Table(datos_resumen, colWidths=[10 * cm, 5 * cm])
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_OSCURO),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  10),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANCO, GRIS_TABLA]),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN",         (1, 0), (1, -1),  "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tabla_resumen)

    # ── Listado de Citas ───────────────────────────────────
    elementos.append(Paragraph("Listado de Citas", estilo_seccion))

    if citas:
        filas_citas = [["#", "Fecha", "Hora", "Paciente", "Doctor", "Especialidad", "Estado"]]
        for i, c in enumerate(citas, 1):
            filas_citas.append([
                str(i),
                str(c.get("fecha", "")),
                str(c.get("hora", "")),
                str(c.get("nombre_paciente", "")),
                str(c.get("nombre_doctor", "")),
                str(c.get("especialidad", "")),
                str(c.get("estado", "")),
            ])
        anchos_citas = [0.8*cm, 2.2*cm, 1.5*cm, 3.5*cm, 3.5*cm, 3*cm, 2.5*cm]
        tabla_citas = Table(filas_citas, colWidths=anchos_citas, repeatRows=1)
        tabla_citas.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_MEDIO),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANCO),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANCO, AZUL_CLARO]),
            ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tabla_citas)
    else:
        elementos.append(Paragraph("No hay citas registradas.", estilo_normal))

    # ── Listado de Pacientes ───────────────────────────────
    elementos.append(Paragraph("Listado de Pacientes", estilo_seccion))

    if pacientes:
        filas_pac = [["#", "Nombre", "Cedula", "Telefono", "Correo", "Fecha Nac."]]
        for i, p in enumerate(pacientes, 1):
            filas_pac.append([
                str(i),
                str(p.get("nombre", "")),
                str(p.get("cedula", "")),
                str(p.get("telefono", "")),
                str(p.get("correo", "")),
                str(p.get("fecha_nacimiento", "")),
            ])
        anchos_pac = [0.8*cm, 4*cm, 2.5*cm, 2.5*cm, 4*cm, 2.7*cm]
        tabla_pac = Table(filas_pac, colWidths=anchos_pac, repeatRows=1)
        tabla_pac.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_OSCURO),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANCO),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANCO, GRIS_TABLA]),
            ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
            ("ALIGN",         (0, 0), (0, -1),  "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tabla_pac)
    else:
        elementos.append(Paragraph("No hay pacientes registrados.", estilo_normal))

    # ── Listado de Doctores ────────────────────────────────
    elementos.append(Paragraph("Listado de Doctores", estilo_seccion))

    if doctores:
        filas_doc = [["#", "Nombre", "Especialidad", "Telefono", "Correo"]]
        for i, d in enumerate(doctores, 1):
            filas_doc.append([
                str(i),
                str(d.get("nombre", "")),
                str(d.get("especialidad", "")),
                str(d.get("telefono", "")),
                str(d.get("correo", "")),
            ])
        anchos_doc = [0.8*cm, 4*cm, 3.5*cm, 2.8*cm, 5.4*cm]
        tabla_doc = Table(filas_doc, colWidths=anchos_doc, repeatRows=1)
        tabla_doc.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_OSCURO),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANCO),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANCO, GRIS_TABLA]),
            ("FONTSIZE",      (0, 1), (-1, -1), 7.5),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#bbbbbb")),
            ("ALIGN",         (0, 0), (0, -1),  "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elementos.append(tabla_doc)
    else:
        elementos.append(Paragraph("No hay doctores registrados.", estilo_normal))

    # ── Pie de página ──────────────────────────────────────
    elementos.append(Spacer(1, 0.5 * cm))
    elementos.append(HRFlowable(width="100%", thickness=1, color=AZUL_MEDIO))
    elementos.append(Paragraph(
        "Sistema de Citas Medicas 2025 - Generado automaticamente",
        ParagraphStyle("pie", parent=estilos["Normal"], fontSize=7,
                       textColor=GRIS_TEXTO, alignment=1),
    ))

    doc.build(elementos)
    return buffer.getvalue()