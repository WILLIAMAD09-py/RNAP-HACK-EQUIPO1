from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Ticket:
    cliente: str = ""
    producto: str = ""
    cantidad: Optional[float] = None
    medida: str = ""
    hora_entrega: str = ""
    campo_dudoso: list = field(default_factory=list)
    transcripcion: str = ""

    def campos(self) -> dict:
        return {
            "cliente": self.cliente,
            "producto": self.producto,
            "cantidad": self.cantidad,
            "medida": self.medida,
            "hora_entrega": self.hora_entrega,
        }

    def esta_completo(self) -> bool:
        return all(
            [
                self.cliente,
                self.producto,
                self.cantidad is not None,
                self.medida,
                self.hora_entrega,
            ]
        )
