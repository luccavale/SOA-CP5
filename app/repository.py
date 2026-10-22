"""Camada de armazenamento: repositório de pedidos em memória."""
from threading import Lock

from app.domain import Pedido


class PedidoRepository:
    """Guarda os pedidos em um dicionário em memória (id -> Pedido).

    Os dados são perdidos quando a aplicação é reiniciada, conforme o enunciado
    (sem dependência de banco externo).
    """

    def __init__(self) -> None:
        self._pedidos: dict[str, Pedido] = {}
        self._lock = Lock()

    def salvar(self, pedido: Pedido) -> Pedido:
        with self._lock:
            self._pedidos[pedido.id] = pedido
        return pedido

    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        with self._lock:
            return self._pedidos.get(pedido_id)
