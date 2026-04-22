import mysql.connector

def conectar():
        #conectarse a la base de datos
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='empresa'
    )
    if conn.is_connected():
        print('Conexión Realizada')
    return conn
conectar()