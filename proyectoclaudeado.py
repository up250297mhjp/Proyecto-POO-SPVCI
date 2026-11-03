import os, sys
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv
import pandas as pd

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
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
        return self.cantidad * self.producto.get_precio()

    def imprimir(self):
        print(f"Detalle ID: {self.detalleID}, Cantidad: {self.cantidad}, "
              f"Producto: {self.producto.descripcion}, Subtotal: {self.subtotal_detalle()}")


class Orden:
    def __init__(self, ordenID=None):
        self.ordenID = ordenID          # lo asigna la BD al guardar
        self.fecha = datetime.now()
        self.detalles = []

    def total_orden(self) -> float:
        return sum(d.subtotal_detalle() for d in self.detalles)

    def addItem(self, detalleID, cantidad, producto: Producto):
        # Solo agrega en memoria; NO toca la BD
        self.detalles.append(Detalle_orden(detalleID, cantidad, producto))

    def imprimir(self):
        print(f"Orden ID: {self.ordenID}, Fecha: {self.fecha}, Total: {self.total_orden()}")
        for detalle in self.detalles:
            detalle.imprimir()

    def insertar_orden(self) -> bool:
        """Guarda la orden, sus detalles y descuenta stock. Todo o nada."""
        try:
            cursor.execute("INSERT INTO Ordenes (fecha) VALUES (%s)", (self.fecha,))
            self.ordenID = cursor.lastrowid      # ID generado por MySQL

            for d in self.detalles:
                cursor.execute(
                    """INSERT INTO DetalleOrdenes
                       (ordenID, productoID, cantidad, precioUnitario)
                       VALUES (%s, %s, %s, %s)""",
                    (self.ordenID, d.producto.productoID, d.cantidad, d.producto.get_precio())
                )
                # Descuenta stock solo si todavía alcanza
                cursor.execute(
                    """UPDATE Productos SET stock = stock - %s
                       WHERE productoID = %s AND stock >= %s""",
                    (d.cantidad, d.producto.productoID, d.cantidad)
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


def buscar_producto(producto_id: int):
    cursor.execute(
        "SELECT productoID, descripcion, precio, stock FROM Productos WHERE productoID = %s",
        (producto_id,)
    )
    fila = cursor.fetchone()
    if fila is None:
        return None
    return Producto(fila["productoID"], fila["descripcion"], fila["precio"], fila["stock"])


def registrar_nueva_orden():
    print("\n--- REGISTRAR NUEVA ORDEN ---")
    orden = Orden()
    contador = 1   # detalleID temporal; el real lo genera la BD

    while True:
        entrada = input("\nID del producto (Enter para terminar): ").strip()
        if entrada == "":
            break
        if not entrada.isdigit():
            print("El ID debe ser un número.")
            continue

        producto = buscar_producto(int(entrada))
        if producto is None:
            print("No existe un producto con ese ID.")
            continue

        producto.imprimir()
        print(f"Stock disponible: {producto.stock}")

        texto = input("Cantidad: ").strip()
        if not texto.isdigit() or int(texto) <= 0:
            print("Cantidad inválida.")
            continue
        cantidad = int(texto)

        # Considera lo que ya agregaste de este mismo producto en la orden
        ya_pedido = sum(d.cantidad for d in orden.detalles
                        if d.producto.productoID == producto.productoID)
        if cantidad + ya_pedido > producto.stock:
            print(f"Stock insuficiente. Disponible: {producto.stock - ya_pedido}")
            continue

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
    orden_id = input("Ingrese el ID de la orden que desea consultar: ").strip()
    print(f"\n{'Orden ID:':<15} {'Producto ID':<15} {'Cantidad':<10} {'Precio Unitario ':<10} {'Subtotal':>10}")
    print(f"{'-'*15} | {'-'*15} | {'-'*10} | {'-'*10} | {'-'*10}")


def main():
    while True:
        Menu()
        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            registrar_nueva_orden()
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