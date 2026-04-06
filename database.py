import mysql.connector

def conectar():
# conectar a la base de datos
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="empresa"
)
    if  conn.is_connected():
        print("Conexion a la base de datos")

    return conn 
