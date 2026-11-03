import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class Conexion:
    @staticmethod
    def conectar():
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl_ca=os.getenv("DB_SSL_CA", "ca.pem"),
        )


if __name__ == "__main__":
    cnx = Conexion.conectar()
    print("Conectado:", cnx.is_connected())
    cnx.close()