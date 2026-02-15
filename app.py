from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return '<h1>🏥 Bienvenido al Sistema de Citas Médicas – Clínica Salud+</h1>'

@app.route('/cita/<paciente>')
def cita(paciente):
    return f'<h2>👤 Hola, {paciente}. Tu cita médica está registrada con éxito.</h2>'

if __name__ == "__main__":
    app.run(debug=True)
