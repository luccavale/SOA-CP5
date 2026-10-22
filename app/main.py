"""Ponto de entrada da aplicação: cria o app FastAPI, middleware e tratamento de erros."""
import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.api import router
from app.logging_config import get_logger, request_id_ctx
from app.schemas import ErroResposta
from app.service import PedidoNaoEncontradoError

logger = get_logger()

app = FastAPI(
    title="API de Pedidos",
    version="1.0.0",
    description=(
        "API REST simples para gerenciamento de pedidos de um e-commerce "
        "(CP5 - Arquitetura Orientada a Serviço - FIAP).\n\n"
        "Todas as respostas trazem o header `X-Request-ID`. O cliente pode enviar "
        "o próprio `X-Request-ID`; caso contrário, a API gera um UUID."
    ),
)
app.include_router(router)


def gerar_openapi() -> dict:
    """Gera a especificação OpenAPI removendo o 422 automático da rota GET.

    O FastAPI adiciona um 422 genérico em toda rota com parâmetros; na consulta
    por id isso nunca acontece (qualquer id inexistente retorna 404), então ele
    é retirado para a documentação refletir o comportamento real.
    """
    if app.openapi_schema:
        return app.openapi_schema
    spec = get_openapi(
        title=app.title, version=app.version, description=app.description, routes=app.routes
    )
    spec["paths"]["/pedidos/{pedido_id}"]["get"]["responses"].pop("422", None)
    for schema_padrao in ("HTTPValidationError", "ValidationError"):
        spec["components"]["schemas"].pop(schema_padrao, None)
    app.openapi_schema = spec
    return spec


app.openapi = gerar_openapi


@app.middleware("http")
async def contexto_da_requisicao(request: Request, call_next):
    """Gera o requestId, mede a duração e registra um log por requisição."""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    token = request_id_ctx.set(request_id)
    inicio = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Erro inesperado ao processar a requisição", extra={"operacao": "ERRO_INTERNO"})
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErroResposta(
                erro="ERRO_INTERNO", mensagem="Erro interno no servidor", requestId=request_id
            ).model_dump(),
        )

    response.headers["X-Request-ID"] = request_id
    logger.log(
        logging.ERROR if response.status_code >= 500 else logging.INFO,
        "Requisição HTTP concluída",
        extra={
            "operacao": "HTTP_REQUEST",
            "metodo": request.method,
            "caminho": request.url.path,
            "statusCode": response.status_code,
            "duracaoMs": round((time.perf_counter() - inicio) * 1000, 2),
        },
    )
    request_id_ctx.reset(token)
    return response


@app.exception_handler(PedidoNaoEncontradoError)
async def tratar_pedido_nao_encontrado(request: Request, exc: PedidoNaoEncontradoError):
    corpo = ErroResposta(
        erro="PEDIDO_NAO_ENCONTRADO", mensagem=str(exc), requestId=request_id_ctx.get()
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=corpo.model_dump())


@app.exception_handler(RequestValidationError)
async def tratar_validacao(request: Request, exc: RequestValidationError):
    detalhes = [
        {
            "campo": ".".join(str(parte) for parte in erro["loc"][1:]) or "body",
            "mensagem": erro["msg"],
        }
        for erro in exc.errors()
    ]
    logger.warning(
        "Requisição com dados inválidos",
        extra={"operacao": "VALIDAR_REQUISICAO", "detalhes": detalhes},
    )
    corpo = ErroResposta(
        erro="REQUISICAO_INVALIDA",
        mensagem="Dados de entrada inválidos",
        requestId=request_id_ctx.get(),
        detalhes=detalhes,
    )
    return JSONResponse(status_code=422, content=corpo.model_dump())
