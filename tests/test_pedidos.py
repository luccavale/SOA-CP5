"""Testes automatizados da API de Pedidos (pytest + TestClient do FastAPI)."""
import io
import json
import logging

from app.logging_config import JsonFormatter, get_logger

PEDIDO_VALIDO = {
    "cliente": "Maria Silva",
    "descricao": "1x Notebook Dell Inspiron 15",
    "valor": 4599.90,
}


def test_criar_pedido_retorna_201_com_status_criado(client):
    resposta = client.post("/pedidos", json=PEDIDO_VALIDO)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"]
    assert corpo["cliente"] == "Maria Silva"
    assert corpo["descricao"] == "1x Notebook Dell Inspiron 15"
    assert corpo["valor"] == 4599.90
    assert corpo["status"] == "CRIADO"
    assert resposta.headers["Location"] == f"/pedidos/{corpo['id']}"


def test_consultar_pedido_existente_retorna_200(client):
    criado = client.post("/pedidos", json=PEDIDO_VALIDO).json()

    resposta = client.get(f"/pedidos/{criado['id']}")

    assert resposta.status_code == 200
    assert resposta.json() == criado


def test_consultar_pedido_inexistente_retorna_404(client):
    resposta = client.get("/pedidos/id-que-nao-existe")

    assert resposta.status_code == 404
    corpo = resposta.json()
    assert corpo["erro"] == "PEDIDO_NAO_ENCONTRADO"
    assert corpo["requestId"] == resposta.headers["X-Request-ID"]


def test_criar_pedido_com_valor_invalido_retorna_422(client):
    resposta = client.post("/pedidos", json={**PEDIDO_VALIDO, "valor": 0})

    assert resposta.status_code == 422
    corpo = resposta.json()
    assert corpo["erro"] == "REQUISICAO_INVALIDA"
    assert corpo["detalhes"][0]["campo"] == "valor"


def test_criar_pedido_gera_log_estruturado_em_json(client):
    saida = io.StringIO()
    handler = logging.StreamHandler(saida)
    handler.setFormatter(JsonFormatter())
    logger = get_logger()
    logger.addHandler(handler)
    try:
        resposta = client.post("/pedidos", json=PEDIDO_VALIDO, headers={"X-Request-ID": "teste-123"})
    finally:
        logger.removeHandler(handler)

    logs = [json.loads(linha) for linha in saida.getvalue().splitlines()]
    log_criacao = next(log for log in logs if log["operacao"] == "CRIAR_PEDIDO")

    assert log_criacao["level"] == "INFO"
    assert log_criacao["timestamp"]
    assert log_criacao["message"] == "Pedido criado com sucesso"
    assert log_criacao["requestId"] == "teste-123"
    assert log_criacao["pedidoId"] == resposta.json()["id"]
