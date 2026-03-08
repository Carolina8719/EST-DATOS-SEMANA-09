import os, json, csv

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'Data')

RUTA_TXT  = os.path.join(DATA_DIR, 'datos.txt')
RUTA_JSON = os.path.join(DATA_DIR, 'datos.json')
RUTA_CSV  = os.path.join(DATA_DIR, 'datos.csv')

CSV_CAMPOS = ['nombre','cedula','doctor','especialidad','fecha','hora','motivo','estado']

# ── TXT ──────────────────────────────────────────
def guardar_txt(r):
    with open(RUTA_TXT, 'a', encoding='utf-8') as f:
        f.write(f"Paciente: {r['nombre']} | Cédula: {r['cedula']} | "
                f"Doctor: {r['doctor']} ({r['especialidad']}) | "
                f"Fecha: {r['fecha']} {r['hora']} | "
                f"Motivo: {r['motivo']} | Estado: {r['estado']}\n")

def leer_txt():
    if not os.path.exists(RUTA_TXT): return []
    with open(RUTA_TXT, 'r', encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip()]

# ── JSON ─────────────────────────────────────────
def guardar_json(r):
    datos = leer_json()
    datos.append(r)
    with open(RUTA_JSON, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def leer_json():
    if not os.path.exists(RUTA_JSON): return []
    with open(RUTA_JSON, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except: return []

# ── CSV ──────────────────────────────────────────
def guardar_csv(r):
    nuevo = not os.path.exists(RUTA_CSV)
    with open(RUTA_CSV, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=CSV_CAMPOS)
        if nuevo: w.writeheader()
        w.writerow({k: r.get(k,'') for k in CSV_CAMPOS})

def leer_csv():
    if not os.path.exists(RUTA_CSV): return []
    with open(RUTA_CSV, 'r', newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# ── Guardar en los 3 formatos ────────────────────
def guardar_en_archivos(r):
    guardar_txt(r)
    guardar_json(r)
    guardar_csv(r)