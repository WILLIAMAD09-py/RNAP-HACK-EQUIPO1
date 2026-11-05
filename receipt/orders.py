from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ticket:
    cliente: str
    producto: str
    cantidad: str
    medida: str
    hora_entrega: str


@dataclass
class ConfirmedOrder:
    ticket: Ticket
    source_audio: str = ""


confirmed_orders: list[ConfirmedOrder] = []


def add_order(ticket: Ticket, source_audio: str = "") -> None:
    confirmed_orders.append(ConfirmedOrder(ticket=ticket, source_audio=source_audio))
