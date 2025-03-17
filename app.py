from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pymysql
import re
import logging
import sys

app = Flask(__name__)
app.secret_key = 'clave-secreta-para-produccion'  # Cambiar en producción
bcrypt = Bcrypt(app)

# Configuración CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "supports_credentials": True,
        "methods": ["GET", "POST", "OPTIONS"]
    }
})

# Configuración de logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuración de Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://"
)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='Analisis',
        cursorclass=pymysql.cursors.DictCursor
    )

def validate_password(password):
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r"[A-Z]", password):
        return "Debe contener al menos una mayúscula"
    if not re.search(r"\d", password):
        return "Debe incluir un número"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Debe contener un carácter especial"
    return None

# ------------------- RUTAS DE REGISTRO -------------------
@app.route('/registro', methods=['GET'])
def mostrar_registro():
    return render_template('registro.html')

@app.route('/registro', methods=['POST'])
@limiter.limit("5 per minute")
def registro():
    conn = None
    try:
        data = request.get_json()
        required_fields = ['name', 'email', 'password', 'role']
        
        # Validación básica
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Campos incompletos"}), 400
            
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
            return jsonify({"status": "error", "message": "Email no válido"}), 400
            
        if error_msg := validate_password(data['password']):
            return jsonify({"status": "error", "message": error_msg}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar email existente
        cur.execute('SELECT UserId FROM security.AppUser WHERE Email = %s', (data['email'],))
        if cur.fetchone():
            return jsonify({"status": "error", "message": "Email ya registrado"}), 409

        # Generar UserId manualmente
        cur.execute('SELECT MAX(UserId) AS max_id FROM security.AppUser')
        max_user_id = cur.fetchone()['max_id'] or 0
        user_id = max_user_id + 1

        # Insertar usuario
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        role = 2 if data['role'] == 'host' else 1

        cur.execute('''
            INSERT INTO security.AppUser 
            (UserId, Name, Email, Password, Role)
            VALUES (%s, %s, %s, %s, %s)
        ''', (user_id, data['name'], data['email'], hashed_pw, role))

        # Lógica para hosts
        if data['role'] == 'host':
            if not data.get('companyName') or not data.get('hostName'):
                conn.rollback()
                return jsonify({"status": "error", "message": "Datos de empresa/host requeridos"}), 400

            # Generar CompanyId
            cur.execute('SELECT MAX(CompanyId) AS max_id FROM business.Company')
            company_id = (cur.fetchone()['max_id'] or 0) + 1
            cur.execute('INSERT INTO business.Company (CompanyId, CompanyName) VALUES (%s, %s)', 
                       (company_id, data['companyName']))

            # Generar HostId
            cur.execute('SELECT MAX(HostId) AS max_id FROM business.Host')
            host_id = (cur.fetchone()['max_id'] or 0) + 1
            cur.execute('''
                INSERT INTO business.Host 
                (HostId, HostName, HostMail, CompanyId)
                VALUES (%s, %s, %s, %s)
            ''', (host_id, data['hostName'], data['email'], company_id))

        conn.commit()
        return jsonify({
            "status": "success", 
            "message": "Registro exitoso", 
            "redirect": "/login"
        }), 201

    except pymysql.IntegrityError as e:
        conn.rollback() if conn else None
        logging.error(f"Error de integridad: {str(e)}")
        return jsonify({"status": "error", "message": "Error en la base de datos"}), 500
    except Exception as e:
        conn.rollback() if conn else None
        logging.error(f"Error general: {str(e)}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# ------------------- RUTAS DE LOGIN -------------------
@app.route('/login', methods=['GET'])
def mostrar_login():
    try:
        # Pasar variables vacías si no existen
        logging.debug("Cargando la página de login...")
        message = request.args.get('message', '')
        error = request.args.get('error', '')
        return render_template('login.html', message=message, error=error)
    except Exception as e:
        logging.error(f"Error al mostrar el login: {str(e)}")
        return jsonify({"status": "error", "message": "Error al mostrar el login"}), 500

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"status": "error", "message": "Campos requeridos"}), 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT UserId, Email, Password, Role 
                FROM security.AppUser 
                WHERE Email = %s
            """, (email,))
            user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['Password'], password):
            session['user_id'] = user['UserId']
            session['user_role'] = user['Role']
            
            return jsonify({
                "status": "success",
                "redirect": "/"
            }), 200
            
        return jsonify({"status": "error", "message": "Credenciales inválidas"}), 401
        
    except Exception as e:
        logging.error(f"Error en login: {str(e)}")
        return jsonify({"status": "error", "message": "Error en el servidor"}), 500

# ------------------- RUTAS PROTEGIDAS -------------------
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('mostrar_login'))
    return render_template('inicio.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('mostrar_login'))

@app.route('/musica')
def musica():
    return render_template('musica.html')

@app.route('/cultura')
def cultura():
    return render_template('cultura.html')

@app.route('/tecnologia')
def tecnologia():
    return render_template('tecnologia.html')

@app.route('/deportes')
def deportes():
    return render_template('deportes.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)