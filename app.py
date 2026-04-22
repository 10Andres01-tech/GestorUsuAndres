from flask import Flask, render_template, request, redirect, flash, session, url_for
from database import conectar

app = Flask(__name__)
app.secret_key = "clave_super_segura"

# ================= LOGIN =================

@app.route('/')
def login():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_form():
    user = request.form['txtusuario']
    password = request.form['txtcontrasena']

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND password = %s", (user, password))
    resultado = cursor.fetchone()

    if resultado:
        session['usuario'] = user
        session['rol'] = resultado[3]
        session['documento'] = resultado[4]

        if resultado[3] == "admin":
            return redirect(url_for('index'))
        else:
            return redirect(url_for('perfil_empleado'))
    else:
        flash("Usuario o contraseña incorrecta", "danger")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================= PERFIL EMPLEADO =================

@app.route('/perfil_empleado')
def perfil_empleado():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM empleados WHERE documento = %s", (session['documento'],))
    empleado = cursor.fetchone()

    return render_template("perfil_empleado.html", emp=empleado)
#actualizar perfil 

@app.route('/actualizar_perfil', methods=['POST'])
def actualizar_perfil():
    id = request.form['id']
    nombre = request.form['txtnombre']
    apellido = request.form['txtapellido']
    cargo = request.form['txtcargo'].strip().lower()
    id_dep = request.form['txtid_dep']

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT horasextras, bonificacion FROM empleados WHERE id=%s", (id,))
    datos = cursor.fetchone()

    horas = datos[0]
    bonificacion = datos[1]

    
    if cargo == "gerente":
        salariobase = 5000000
    elif cargo == "administrador":
        salariobase = 3500000
    elif cargo == "contador":
        salariobase = 2800000
    else:
        salariobase = 1800000

    totalExtras = horas * 3000
    salariobruto = float(salariobase + totalExtras + bonificacion)
    salud = salariobruto * 0.04
    pension = salariobruto * 0.04
    salarioneto = salariobruto - salud - pension

    cursor.execute("""
        UPDATE empleados 
        SET nombre=%s, apellido=%s, cargo=%s, id_dep=%s,
            salariobase=%s, salud=%s, pension=%s, salarioneto=%s
        WHERE id=%s
    """, (
        nombre, apellido, cargo, id_dep,
        salariobase, int(salud), int(pension), int(salarioneto),
        id
    ))

    con.commit()

    flash("Datos actualizados correctamente", "success")
    return redirect(url_for('perfil_empleado'))
# ================= INDEX =================

@app.route('/index')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if session['rol'] != 'admin':
        return redirect(url_for('perfil_empleado'))

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM usuarios")
    lista = cursor.fetchall()

    cursor.execute("SELECT * FROM empleados")
    empleados = cursor.fetchall()

    empleados_calculados = []

    for e in empleados:
        empleados_calculados.append({
            "id": e[0],
            "documento": e[1],
            "nombre": e[2],
            "apellido": e[3],
            "cargo": e[4],
            "salario_base": e[5],
            "horas": e[6],
            "bonificacion": e[7],
            "salud": e[8],
            "pension": e[9],
            "salario_neto": e[10]
        })

    return render_template("index.html", lista=lista, empleados=empleados_calculados)
# ================= USUARIOS =================

@app.route('/guardar_usuario', methods=['POST'])
def guardar_usuario():
    usuario = request.form['txtusuario']
    password = request.form['txtcontrasena']
    rol = request.form['txtrol']
    documento = request.form['txtdocumento']

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE documento=%s", (documento,))
    if cursor.fetchone():
        flash("Usuario ya existe", "warning")
    else:
        cursor.execute(
            "INSERT INTO usuarios (usuario,password,rol,documento) VALUES (%s,%s,%s,%s)",
            (usuario, password, rol, documento)
        )
        con.commit()
        flash("Usuario registrado", "success")

    return redirect(url_for('index'))


@app.route('/eliminar/<int:id>')
def eliminarusu(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT rol FROM usuarios WHERE id_usu = %s", (id,))
    usuario = cursor.fetchone()

    if usuario:
        if usuario[0] == 'admin':
            flash("No se puede eliminar el administrador", "danger")
        else:
            cursor.execute("DELETE FROM usuarios WHERE id_usu = %s", (id,))
            con.commit()
            flash("Usuario eliminado correctamente", "success")

    return redirect(url_for('index'))

# ================= EDITAR USUARIO =================

@app.route('/editarusu/<int:id>')
def editarusu(id):
    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usu = %s", (id,))
    usuario = cursor.fetchone()

    return render_template("editarusuario.html", usu=usuario)


@app.route('/actualizar_usuario', methods=['POST'])
def actualizar_usuario():
    id = request.form['id']
    usuario = request.form['txtusuario']
    password = request.form['txtpassword']

    con = conectar()
    cursor = con.cursor()

    cursor.execute(
        "UPDATE usuarios SET usuario=%s, password=%s WHERE id_usu=%s",
        (usuario, password, id)
    )
    con.commit()

    flash("Usuario actualizado correctamente", "success")
    return redirect(url_for('index'))

# ================= EMPLEADOS =================

@app.route('/guardar_empleado', methods=['POST'])
def guardar_empleado():
    documento = request.form['txtdocumento']
    nombre = request.form['txtnombre']
    apellido = request.form['txtapellido']
    cargo = request.form['txtcargo']
    horas = int(request.form['txthorasextras'])
    bonificacion = float(request.form['txtbonificacion'])
    area = request.form['txtarea']

    if cargo.lower() == "gerente":
        salariobase = 5000000
    elif cargo.lower() == "administrador":
        salariobase = 3500000
    elif cargo.lower() == "contador":
        salariobase = 2800000
    else:
        salariobase = 1800000

    totalExtras = horas * 3000
    salariobruto = salariobase + totalExtras + bonificacion
    salud = salariobruto * 0.04
    pension = salariobruto * 0.04
    salarioneto = salariobruto - salud - pension

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM empleados WHERE documento=%s", (documento,))
    
    if cursor.fetchone():
        flash("Empleado ya existe", "warning")
    else:
        cursor.execute("""
            INSERT INTO empleados 
            (documento, nombre, apellido, cargo, salariobase, horasextras, bonificacion, salud, pension, salarioneto, id_dep)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (documento, nombre, apellido, cargo, salariobase, horas, bonificacion, int(salud), int(pension), int(salarioneto), area))

        con.commit()
        flash("Empleado registrado correctamente", "success")

    return redirect(url_for('index'))

# ================= ELIMINAR EMPLEADO =================

@app.route('/eliminaremple/<int:id>')
def eliminaremple(id):
    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT documento FROM empleados WHERE id = %s", (id,))
    empleado = cursor.fetchone()

    if empleado:
        documento = empleado[0]

        cursor.execute("DELETE FROM empleados WHERE id = %s", (id,))
        cursor.execute("DELETE FROM usuarios WHERE documento = %s", (documento,))
        con.commit()

        flash("Empleado y usuario eliminados correctamente", "success")

    return redirect(url_for('index'))

# ================= EDITAR EMPLEADO (ADMIN) =================

@app.route('/editaremple/<int:id>')
def editaremple(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))

    if session['rol'] != 'admin':
        return redirect(url_for('perfil_empleado'))

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM empleados WHERE id = %s", (id,))
    empleado = cursor.fetchone()

    cursor.execute("SELECT * FROM departamentos")
    departamentos = cursor.fetchall()

    return render_template("editarempleado.html", emp=empleado, departamentos=departamentos)

#actualizar:)

@app.route('/actualizar_empleado', methods=['POST'])
def actualizar_empleado():
    id = request.form['id']
    nombre = request.form['txtnombre']
    apellido = request.form['txtapellido']
    cargo = request.form['txtcargo'].strip().lower()
    horas = int(request.form['txthorasextras'])
    bonificacion = float(request.form['txtbonificacion'])

    # 🔧 calcular salario base correctamente
    if cargo == "gerente":
        salariobase = 5000000
    elif cargo == "administrador":
        salariobase = 3500000
    elif cargo == "contador":
        salariobase = 2800000
    else:
        salariobase = 1800000

    totalExtras = horas * 3000
    salariobruto = salariobase + totalExtras + bonificacion
    salud = salariobruto * 0.04
    pension = salariobruto * 0.04
    salarioneto = salariobruto - salud - pension

    con = conectar()
    cursor = con.cursor()

    cursor.execute("""
        UPDATE empleados 
        SET nombre=%s, apellido=%s, cargo=%s, salariobase=%s,
            horasextras=%s, bonificacion=%s, salud=%s, pension=%s, salarioneto=%s
        WHERE id=%s
    """, (
        nombre, apellido, cargo, salariobase,
        horas, bonificacion,
        int(salud), int(pension), int(salarioneto),
        id
    ))

    con.commit()

    flash("Empleado actualizado correctamente", "success")
    return redirect(url_for('index'))

# =============== EDITAR PERFIL EMPLEADO ================

@app.route('/editar_perfil_empleado/<int:id>')
def editar_perfil_empleado(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM empleados WHERE id = %s", (id,))
    empleado = cursor.fetchone()

    return render_template("editar_perfil_empleado.html", emp=empleado)

# ================= RUN =================

if __name__ == '__main__':
    app.run(debug=True)