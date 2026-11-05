import csv
from pathlib import Path
from typing import Optional

from .config import CATALOG_PATH


class Catalogo:
    def __init__(self, ruta: str | Path = CATALOG_PATH):
        self.ruta = Path(ruta)
        self.productos: list[dict] = []

    def cargar(self) -> list[dict]:
        return self.productos

    def buscar_por_id(self, id_producto: str) -> Optional[dict]:
        return None

    def buscar_por_nombre(self, nombre: str, umbral: float = 0.6) -> Optional[dict]:
        return None
