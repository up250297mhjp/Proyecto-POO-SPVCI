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
        subtotal = self.cantidad * self.producto.get_precio()
        return subtotal

    def imprimir(self):
        print(f"Detalle ID: {self.detalleID}, Cantidad: {self.cantidad}, Producto: {self.producto.descripcion}, Subtotal: {self.subtotal_detalle()}")

class Orden:
    def __init__(self, ordenID, detalles: Detalle_orden):
        self.ordenID = ordenID
        self.fecha = datetime.now()
        self.detalles = []

    def total_orden(self) -> float:
        total = sum(detalle.subtotal_detalle() for detalle in self.detalles)
        return total

    def addItem(self, detalleID, cantidad, producto: Producto):
        detalle = Detalle_orden(detalleID, cantidad, producto)
        self.detalles.append(detalle)

    def imprimir(self):
        print(f"Orden ID: {self.ordenID}, Fecha: {self.fecha}, Total: {self.total_orden()}")
        for detalle in self.detalles:
            detalle.imprimir()

def registrar_nueva_orden():
    print("\n--- REGISTRAR NUEVA ORDEN ---")

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

