from flask import Flask, render_template

app = Flask(__name__)

productos = [
    {"id": 1, "nombre": "Paracetamol 500mg",  "precio": 5.50,  "stock": 100},
    {"id": 2, "nombre": "Ibuprofeno 400mg",    "precio": 8.00,  "stock": 50},
    {"id": 3, "nombre": "Amoxicilina 500mg",   "precio": 12.00, "stock": 30},
    {"id": 4, "nombre": "Omeprazol 20mg",      "precio": 7.50,  "stock": 60},
]

clientes = [
    {"id": 1, "nombre": "Ana García",   "email": "ana@email.com",   "ciudad": "Guayaquil"},
    {"id": 2, "nombre": "Luis Pérez",   "email": "luis@email.com",  "ciudad": "Quito"},
    {"id": 3, "nombre": "María Torres", "email": "maria@email.com", "ciudad": "Cuenca"},
]

facturas = [
    {"id": "F-001", "cliente": "Ana García",   "total": 25.50, "fecha": "2025-01-10"},
    {"id": "F-002", "cliente": "Luis Pérez",   "total": 48.00, "fecha": "2025-01-15"},
    {"id": "F-003", "cliente": "María Torres", "total": 19.50, "fecha": "2025-01-20"},
]

@app.route("/")
def index():
    return render_template("index.html",
        total_productos=len(productos),
        total_clientes=len(clientes),
        total_facturas=len(facturas))

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

if __name__ == "__main__":
    app.run(debug=True)
