import os
from datetime import datetime
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
config = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Conexión
conn = mysql.connector.connect(**config)
cursor = conn.cursor(dictionary=True)  # dictionary=True → resultados como dict
class Producto:
    def __init__(self, productoID, descripcion, precio, stock):
        self.productoID = productoID
        self.descripcion = descripcion
        self.__precio = precio
        self.stock = stock

    def get_precio(self):
        return self.__precio

    def imprimir(self):
        print(f"Producto ID: {self.productoID}, Descripción: {self.descripcion}, Precio: {self.__precio}")

class Detalle_orden:
    def __init__(self, detalleID, cantidad, producto: Producto):
        self.detalleID = detalleID
        self.cantidad = cantidad
        self.producto = producto

    def subtotal_detalle(self) -> float:
        subtotal = self.cantidad * self.producto.get_precio()
        return subtotal

    def insertar_detalle(self, ordenID):
        precio_unitario = self.producto.get_precio()
        print("Se imprime el precio unitario: ", precio_unitario)
        id_generado = cursor.lastrowid  # Obtener el ID generado por la base de datos
        sql = "INSERT INTO detalleordenes (ordenID, productoID, cantidad, precioUnitario) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (ordenID, self.producto.productoID, self.cantidad, precio_unitario))
        conn.commit()
        self.imprimir()

    def imprimir(self):
        print(f"Detalle ID: {self.detalleID}, Cantidad: {self.cantidad}, Producto: {self.producto.descripcion}")

class Orden:
    def __init__(self, ordenID, detalles: Detalle_orden):
        self.ordenID = ordenID
        self.fecha = datetime.now()
        self.detalles = []

    def total_orden(self) -> float:
        total = sum(detalle.subtotal_detalle() for detalle in self.detalles)
        return total

    def addItem(self, detalleID, cantidad, producto: Producto):
        self.detalles.append(Detalle_orden(detalleID, cantidad, producto))

    def imprimir(self):
        print(f"Orden ID: {self.ordenID}, Fecha: {self.fecha}, Total: {self.total_orden()}")
        for detalle in self.detalles:
            detalle.imprimir()

    def insertar_orden(self) -> bool:
        """Guarda la orden, sus detalles y descuenta stock. Todo o nada."""
        try:
            sql = "INSERT INTO ordenes (fecha) VALUES (%s)"
            cursor.execute(sql, (self.fecha,))
            #cursor.execute("INSERT INTO ordenes (fecha) VALUES (%s)", (self.fecha,))
            self.ordenID = cursor.lastrowid      # ID generado por MySQL

            for d in self.detalles:
                cursor.execute(
                    """INSERT INTO detalleordenes
                       (ordenID, productoID, cantidad, precioUnitario)
                       VALUES (%s, %s, %s, %s)""",
                    (self.ordenID, d.producto.productoID, d.cantidad, d.producto.get_precio())
                )
                # Descuenta stock solo si todavía alcanza
                cursor.execute(
                    """UPDATE Productos SET stock = stock - %s
                       WHERE productoID = %s""",
                    (d.cantidad, d.producto.productoID)
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Stock insuficiente para '{d.producto.descripcion}'")

            conn.commit()
            print(f"\nOrden #{self.ordenID} registrada correctamente.")
            return True
        except Exception as e:
            conn.rollback()   # deshace TODO lo de esta orden
            print(f"\nNo se pudo guardar la orden: {e}")
            return False


def Menu():
    print("\n==============================")
    print("   SISTEMA DE GESTIÓN DE ÓRDENES")
    print("==============================")
    print("1. Registrar nueva orden")
    print("2. Ver órdenes")
    print("3. Salir")

#todo Se visualiza la tabla con la orden que seleccione el ususario
def ver_ordenes():
    print("\n------- VER ÓRDENES --------")
    try:
        orden_id = int(input("Ingrese el ID de la orden que desea consultar: ").strip())
    except ValueError:
        print("El ID de la orden debe ser un número entero.")
        return

    cursor.execute(
        "SELECT ordenID, productoID, cantidad, precioUnitario FROM detalleordenes WHERE ordenID = %s",
        (orden_id,)
    )
    filas = cursor.fetchall()

    if not filas:
        print(f"No se encontraron registros para la orden ID: {orden_id}")
        return

    print(f"\n{'Orden ID':<10} | {'Producto ID':<12} | {'Cantidad':<10} | {'Precio Unit.':<12} | {'Subtotal':<10}")
    print("-" * 65)

    acumulado = 0
    for fila in filas:
        subtotal = fila['cantidad'] * fila['precioUnitario']
        acumulado += subtotal
        print(f"{fila['ordenID']:<10} | {fila['productoID']:<12} | {fila['cantidad']:<10} | {fila['precioUnitario']:<12.2f} | {subtotal:<10.2f}")
    
    print("-" * 65)
    print(f"Acumulado total de la orden: {acumulado:.2f}\n")

def buscar_producto(producto_id: int):
    cursor.execute(
        "SELECT productoID, descripcion, precio, stock FROM Productos WHERE productoID = %s",
        (producto_id,)
    )
    fila = cursor.fetchone()
    if fila is None:
        return None
    return Producto(fila["productoID"], fila["descripcion"], fila["precio"], fila["stock"])

#Registro de las ordenes
def registrar_orden():
    print("\n--- REGISTRAR NUEVA ORDEN ---")
    orden = Orden(datetime.now(), [])
    contador = 1   # detalleID temporal; el real lo genera la BD

    while True:
        id_producto = input("\nID del producto (Enter para terminar): ").strip()
        if id_producto == "":
            break
        if not id_producto.isdigit():
            print("El ID debe ser un número.")
            continue

        producto = buscar_producto(int(id_producto))
        if producto is None:
            print("No existe un producto con ese ID.")
            continue

        producto.imprimir()

        cant = input("Cantidad: ").strip()
        cantidad = int(cant)

        # Considera lo que ya agregaste de este mismo producto en la orden aqui iba lo de ya pedido XD

        orden.addItem(contador, cantidad, producto)
        contador += 1
        print("Producto agregado.")

    if not orden.detalles:
        print("\nOrden vacía, no se registró nada.")
        return

    print("\n--- RESUMEN ---")
    orden.imprimir()

    if input("\n¿Confirmar orden? (s/n): ").strip().lower() == "s":
        orden.insertar_orden()      # aquí se guarda, una sola vez
    else:
        print("\nOrden cancelada.")

def main():
    while True:
        Menu()
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            registrar_orden()
        elif opcion == "2":
            ver_ordenes()
        elif opcion == "3":
            print("\nSaliendo del sistema...")
            break
        else:
            print("\nOpción inválida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()
    print("\n. . . H e c h o")

