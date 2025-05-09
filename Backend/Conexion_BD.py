import pymysql

def get_db_connection():
    try:
        mydb = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            db="borrador",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return mydb
    except pymysql.Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def close_db_connection(connection):
    if connection and connection.open:
        connection.close()
