from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde el frontend

# Configuración de Flask-Mail para enviar correos electrónicos
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor SMTP (ejemplo con Gmail)
app.config['MAIL_PORT'] = 587  # Puerto seguro
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tucorreo@gmail.com'  # Cambia esto con tu correo
app.config['MAIL_PASSWORD'] = 'tucontraseña'  # Usa una contraseña segura o App Password

mail = Mail(app)

# 📌 Función para inicializar la base de datos SQLite
def init_db():
    with sqlite3.connect("mensajes.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                asunto TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()  # Crear la base de datos si no existe

# 📌 Ruta para recibir mensajes del formulario
@app.route('/contacto', methods=['POST'])
def recibir_mensaje():
    try:
        data = request.json
        nombre = data.get('nombre')
        email = data.get('email')
        asunto = data.get('asunto')
        mensaje = data.get('mensaje')

        # Validación básica
        if not nombre or not email or not asunto or not mensaje:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        # Guardar mensaje en la base de datos
        with sqlite3.connect("mensajes.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO mensajes (nombre, email, asunto, mensaje) VALUES (?, ?, ?, ?)",
                           (nombre, email, asunto, mensaje))
            conn.commit()

        # Enviar correo de notificación
        msg = Message(f"Nuevo Mensaje de {nombre}", sender=email, recipients=["tucorreo@gmail.com"])
        msg.body = f"Nombre: {nombre}\nEmail: {email}\nAsunto: {asunto}\n\nMensaje:\n{mensaje}"
        mail.send(msg)

        return jsonify({"message": "Mensaje enviado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
