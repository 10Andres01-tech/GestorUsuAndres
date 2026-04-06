from flask import Flask, render_template, request, redirect, flash
from database import conectar
from apps import login_bp   

app = Flask(__name__)
app.secret_key = "mi_clave_super_segura_y_unica_123"

# REGISTRAR EL BLUEPRINT
app.register_blueprint(login_bp)

# ruta principal
@app.route('/')
def inicio():
    return render_template("index.html")

# guardar usuario
@app.route('/guardar_usuario', methods=['POST'])
def guardar_usuario():
    usuario = request.form['txtusuario']
    password = request.form['txtcontrasena']
    rolusu = request.form['txtrol']
    documento = request.form['txtdocumento']

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE documento = %s", (documento,))
    existente = cursor.fetchone()

    if existente:
        flash("Usuario con este documento ya existe.", "warning")
    else:
        sql = "INSERT INTO usuarios (usuario, password, rol, documento) VALUES (%s, %s, %s, %s)"
        valores = (usuario, password, rolusu, documento)
        cursor.execute(sql, valores)
        con.commit()
        flash("Usuario registrado correctamente.", "success")

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)