"""Camada de negócio: regras para criar e consultar pedidos."""
from datetime import datetime, timezone
from uuid import uuid4

from app.domain import Pedido, StatusPedido
from app.logging_config import get_logger
from app.repository import PedidoRepository

logger = get_logger()


class PedidoNaoEncontradoError(Exception):
    def __init__(self, pedido_id: str) -> None:
        super().__init__(f"Pedido '{pedido_id}' não encontrado")
        self.pedido_id = pedido_id


class PedidoService:
    def __init__(self, repositorio: PedidoRepository) -> None:
        self._repositorio = repositorio

    def criar(self, cliente: str, descricao: str, valor: float) -> Pedido:
        """Cria um pedido com id gerado pelo servidor e status inicial CRIADO."""
        pedido = Pedido(
            id=str(uuid4()),
            cliente=cliente,
            descricao=descricao,
            valor=round(valor, 2),
            status=StatusPedido.CRIADO,
            criado_em=datetime.now(timezone.utc),
        )
        self._repositorio.salvar(pedido)
        logger.info(
            "Pedido criado com sucesso",
            extra={"operacao": "CRIAR_PEDIDO", "pedidoId": pedido.id},
        )
        return pedido

    def buscar_por_id(self, pedido_id: str) -> Pedido:
        pedido = self._repositorio.buscar_por_id(pedido_id)
        if pedido is None:
            logger.warning(
                "Pedido não encontrado",
                extra={"operacao": "CONSULTAR_PEDIDO", "pedidoId": pedido_id},
            )
            raise PedidoNaoEncontradoError(pedido_id)
        logger.info(
            "Pedido consultado com sucesso",
            extra={"operacao": "CONSULTAR_PEDIDO", "pedidoId": pedido.id},
        )
        return pedido
