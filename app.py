from flask import Flask, render_template

app = Flask(__name__)

# ── Datos de ejemplo (sin base de datos por ahora) ──────────────────────────
productos = [
    {"id": 1, "nombre": "Laptop Lenovo",   "precio": 850.00, "stock": 10},
    {"id": 2, "nombre": "Mouse Inalámbrico","precio":  25.50, "stock": 50},
    {"id": 3, "nombre": "Teclado Mecánico", "precio":  75.00, "stock": 30},
    {"id": 4, "nombre": "Monitor 24\"",     "precio": 220.00, "stock": 15},
]

clientes = [
    {"id": 1, "nombre": "Ana García",    "email": "ana@email.com",    "ciudad": "Guayaquil"},
    {"id": 2, "nombre": "Luis Pérez",    "email": "luis@email.com",   "ciudad": "Quito"},
    {"id": 3, "nombre": "María Torres",  "email": "maria@email.com",  "ciudad": "Cuenca"},
]

facturas = [
    {"id": "F-001", "cliente": "Ana García",   "total": 875.50, "fecha": "2025-01-10"},
    {"id": "F-002", "cliente": "Luis Pérez",   "total": 295.00, "fecha": "2025-01-15"},
    {"id": "F-003", "cliente": "María Torres", "total": 100.50, "fecha": "2025-01-20"},
]

# ── Rutas ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    total_productos = len(productos)
    total_clientes  = len(clientes)
    total_facturas  = len(facturas)
    return render_template(
        "index.html",
        total_productos=total_productos,
        total_clientes=total_clientes,
        total_facturas=total_facturas,
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/productos")
def lista_productos():
    return render_template("productos.html", productos=productos)

@app.route("/clientes")
def lista_clientes():
    return render_template("clientes.html", clientes=clientes)

@app.route("/facturas")
def lista_facturas():
    return render_template("facturas.html", facturas=facturas)

# ── Arranque ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)



