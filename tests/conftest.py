import pytest
from fastapi.testclient import TestClient

from app.api import get_pedido_service
from app.main import app
from app.repository import PedidoRepository
from app.service import PedidoService


@pytest.fixture
def client():
    """Cliente HTTP de teste com um repositório em memória novo para cada teste."""
    service = PedidoService(PedidoRepository())
    app.dependency_overrides[get_pedido_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
