"""Entidade de domínio: Pedido."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StatusPedido(str, Enum):
    CRIADO = "CRIADO"


@dataclass(frozen=True)
class Pedido:
    id: str
    cliente: str
    descricao: str
    valor: float
    status: StatusPedido
    criado_em: datetime
