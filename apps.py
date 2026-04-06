from flask import Flask, render_template, request, redirect, flash, session, url_for
from database import conectar

apps = Flask(__name__)
apps.secret_key = "clave_secreta"


#  MOSTRAR LOGIN
@apps.route('/')
def mostrar_login():
    return render_template("login.html")


#  INDEX (PROTEGIDO)
@apps.route('/index')
def index():
    if 'usuario' not in session:
        return redirect(url_for('mostrar_login'))

    con = conectar()
    cursor = con.cursor()

    sql = "SELECT * FROM usuarios"
    cursor.execute(sql)
    lista = cursor.fetchall()   # 

    return render_template("index.html", usuario=session['usuario'], lista=lista)

# PROCESAR LOGIN
@apps.route('/login', methods=["POST"])
def login_form():

    user = request.form['txtusuario']
    password = request.form['txtcontrasena']

    con = conectar()
    cursor = con.cursor()

    sql = "SELECT * FROM usuarios WHERE usuario = %s AND password = %s"
    cursor.execute(sql, (user, password))

    resultado = cursor.fetchone()

    if resultado:
        rol = resultado[3]

        #  GUARDAR SESIÓN
        session['usuario'] = user
        session['rol'] = rol

        if rol == "administrador":
            return redirect(url_for('index'))
        else:
            return "Bienvenido empleado"
    else:
        flash("Usuario o contraseña incorrecta", "danger")
        return redirect(url_for('mostrar_login'))


#  LOGOUT
@apps.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('mostrar_login'))


#  GUARDAR USUARIO
@apps.route('/guardar_usuario', methods=['POST'])
def guardar_usuario():
    if 'usuario' not in session:
        return redirect(url_for('mostrar_login'))

    usuario = request.form['txtusuario']
    password = request.form['txtcontrasena']
    rolusu = request.form['txtrol']
    documento = request.form['txtdocumento']

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE documento = %s", (documento,))
    existente = cursor.fetchone()

    if existente:
        flash("Usuario con este documento ya existe", "warning")
    else:
        sql = "INSERT INTO usuarios (usuario, password, rol, documento) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (usuario, password, rolusu, documento))
        con.commit()
        flash("Usuario registrado correctamente", "success")

    return redirect(url_for('index'))


if __name__ == '__main__':
    apps.run(debug=True)