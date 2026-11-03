import os, sys
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv
import pandas as pd

load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)
config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
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
    def __init__(self, ordenID, fecha, detalles: Detalle_orden):
        self.ordenID = ordenID
        self.fecha = datetime.now()
        self.detalles = []

    def total_orden(self) -> float:
        pass

    def addItemaddItem(detalleID, cantidad, producto:Producto):
        pass

    def imprimir(self):
        print(f"Orden ID: {self.ordenID}, Fecha: {self.fecha}, Total: {self.total_orden()}")
        for detalle in self.detalles:
            detalle.imprimir()

def main():
    pass

