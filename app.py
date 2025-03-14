from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import bcrypt  # Importa BCrypt para hashing seguro

app = Flask(__name__)
app.secret_key = 'root'  # Configura una clave secreta para sesiones

#Inicializar python app.py

# Configura la conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        database='Analisis'
    )

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():

    #if 'register' in request.form:
        #return redirect(url_for('register'))  # Redirige a la página de registro
    
    email = request.form['email']
    password = request.form['password'].encode('utf-8')  # Convierte la contraseña ingresada a bytes
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserId, email, password, role FROM security.AppUser WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            hashed_password = user[2].encode('utf-8')  # Convierte la contraseña almacenada en la BD a bytes
            
            # Verifica la contraseña con BCrypt
            if bcrypt.checkpw(password, hashed_password):
                session['user_id'] = user[0]  # Guarda el ID del usuario en la sesión

                if user[3] == 1:
                    return redirect(url_for('admin'))
                elif user[3] == 2:
                    return redirect(url_for('home'))
                else:
                    return render_template('login.html', error="Usuario no autorizado")
            else:
                return render_template('login.html', error="Correo o contraseña incorrectos")
        else:
            return render_template('login.html', error="Correo o contraseña incorrectos")
    except Error as e:
        return str(e)
    finally:
        if conn:
            conn.close()

# Función para registrar un usuario (ejemplo)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')  # Convierte la contraseña a bytes
        
        # Genera el hash de la contraseña con BCrypt
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Inserta el usuario en la base de datos
            cursor.execute("INSERT INTO security.AppUser (email, password, role) VALUES (%s, %s, %s)", 
                           (email, hashed_password, 1))  # Role 2 por defecto (usuario normal)
            conn.commit()

            # Después de registrar al usuario, lo redirigimos al login
            return redirect(url_for('index'))
        except Error as e:
            return str(e)
        finally:
            if conn:
                conn.close()

    # Si es un GET, renderiza el formulario de registro
    return render_template('register.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('inicio.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Si no hay usuario logueado, redirigir a login
    return render_template('inicio.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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
    app.run(debug=True)
