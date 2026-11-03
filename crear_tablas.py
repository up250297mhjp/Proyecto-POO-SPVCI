from conexion import Conexion

cnx = Conexion.conectar()
cursor = cnx.cursor()

with open("esquema.sql", "r", encoding="utf-8") as f:
    sql = f.read()

for sentencia in sql.split(";"):
    if sentencia.strip():
        cursor.execute(sentencia)

cnx.commit()
cursor.close()
cnx.close()
print("Tablas creadas")