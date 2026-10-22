"""Contratos JSON da API (entrada e saída), validados com Pydantic."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain import Pedido, StatusPedido


class PedidoEntrada(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "cliente": "Maria Silva",
                    "descricao": "1x Notebook Dell Inspiron 15",
                    "valor": 4599.90,
                }
            ]
        },
    )

    cliente: str = Field(..., min_length=1, max_length=120, description="Nome ou identificação do cliente")
    descricao: str = Field(..., min_length=1, max_length=500, description="Descrição do pedido")
    valor: float = Field(..., gt=0, description="Valor total do pedido (maior que zero)")


class PedidoResposta(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "3f2b8c1e-7a4d-4e1b-9c2a-5d6e7f8a9b0c",
                    "cliente": "Maria Silva",
                    "descricao": "1x Notebook Dell Inspiron 15",
                    "valor": 4599.90,
                    "status": "CRIADO",
                    "criadoEm": "2026-10-21T22:15:03.512Z",
                }
            ]
        }
    )

    id: str = Field(..., description="Identificador único do pedido (UUID)")
    cliente: str
    descricao: str
    valor: float
    status: StatusPedido
    criadoEm: datetime = Field(..., description="Data/hora de criação (UTC)")

    @classmethod
    def de_pedido(cls, pedido: Pedido) -> "PedidoResposta":
        return cls(
            id=pedido.id,
            cliente=pedido.cliente,
            descricao=pedido.descricao,
            valor=pedido.valor,
            status=pedido.status,
            criadoEm=pedido.criado_em,
        )


class ErroResposta(BaseModel):
    erro: str = Field(..., description="Código do erro")
    mensagem: str = Field(..., description="Descrição legível do erro")
    requestId: str = Field(..., description="Identificador da requisição (também enviado no header X-Request-ID)")
    detalhes: list[dict] | None = Field(None, description="Detalhes de validação, quando houver")
