"""Camada HTTP: rotas REST de pedidos."""
from fastapi import APIRouter, Depends, Path, Response, status

from app.repository import PedidoRepository
from app.schemas import ErroResposta, PedidoEntrada, PedidoResposta
from app.service import PedidoService

# Instâncias únicas da aplicação (armazenamento em memória compartilhado).
_repositorio = PedidoRepository()
_service = PedidoService(_repositorio)


def get_pedido_service() -> PedidoService:
    return _service


router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

EXEMPLO_PEDIDO = {
    "id": "3f2b8c1e-7a4d-4e1b-9c2a-5d6e7f8a9b0c",
    "cliente": "Maria Silva",
    "descricao": "1x Notebook Dell Inspiron 15",
    "valor": 4599.90,
    "status": "CRIADO",
    "criadoEm": "2026-10-21T22:15:03.512Z",
}

EXEMPLO_404 = {
    "erro": "PEDIDO_NAO_ENCONTRADO",
    "mensagem": "Pedido '00000000-0000-0000-0000-000000000000' não encontrado",
    "requestId": "b7e9a1d2-4c3f-4a8e-9f10-2d3c4b5a6e7f",
    "detalhes": None,
}

EXEMPLO_422 = {
    "erro": "REQUISICAO_INVALIDA",
    "mensagem": "Dados de entrada inválidos",
    "requestId": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
    "detalhes": [
        {"campo": "valor", "mensagem": "Input should be greater than 0"},
        {"campo": "cliente", "mensagem": "Field required"},
    ],
}


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PedidoResposta,
    operation_id="criarPedido",
    summary="Criar pedido",
    description=(
        "Cria um novo pedido. O identificador (UUID), o status inicial (`CRIADO`) "
        "e a data de criação são definidos pelo servidor."
    ),
    responses={
        201: {
            "description": "Pedido criado com sucesso",
            "headers": {
                "Location": {
                    "description": "URL do pedido criado",
                    "schema": {"type": "string", "example": "/pedidos/3f2b8c1e-7a4d-4e1b-9c2a-5d6e7f8a9b0c"},
                }
            },
            "content": {"application/json": {"example": EXEMPLO_PEDIDO}},
        },
        422: {
            "model": ErroResposta,
            "description": "Corpo da requisição inválido (campo ausente, vazio ou valor menor/igual a zero)",
            "content": {"application/json": {"example": EXEMPLO_422}},
        },
    },
)
def criar_pedido(
    entrada: PedidoEntrada,
    response: Response,
    service: PedidoService = Depends(get_pedido_service),
) -> PedidoResposta:
    pedido = service.criar(entrada.cliente, entrada.descricao, entrada.valor)
    response.headers["Location"] = f"/pedidos/{pedido.id}"
    return PedidoResposta.de_pedido(pedido)


@router.get(
    "/{pedido_id}",
    response_model=PedidoResposta,
    operation_id="consultarPedido",
    summary="Consultar pedido por identificador",
    responses={
        200: {
            "description": "Pedido encontrado",
            "content": {"application/json": {"example": EXEMPLO_PEDIDO}},
        },
        404: {
            "model": ErroResposta,
            "description": "Não existe pedido com o identificador informado",
            "content": {"application/json": {"example": EXEMPLO_404}},
        },
    },
)
def consultar_pedido(
    pedido_id: str = Path(..., description="Identificador único do pedido (UUID retornado na criação)"),
    service: PedidoService = Depends(get_pedido_service),
) -> PedidoResposta:
    pedido = service.buscar_por_id(pedido_id)
    return PedidoResposta.de_pedido(pedido)
