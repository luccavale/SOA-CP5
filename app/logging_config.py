"""Configuração de logs estruturados em JSON.

Cada linha de log é um objeto JSON com, no mínimo:
timestamp, level, operacao, message e requestId.
"""
import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone

# Guarda o requestId da requisição atual. É preenchido pelo middleware
# e lido automaticamente por qualquer log emitido durante a requisição.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

LOGGER_NAME = "pedidos-api"

# Campos opcionais que podem ser enviados via `extra={...}` nos logs.
CAMPOS_EXTRAS = ("pedidoId", "metodo", "caminho", "statusCode", "duracaoMs", "detalhes")


class JsonFormatter(logging.Formatter):
    """Formata cada registro de log como uma linha JSON."""

    def format(self, record: logging.LogRecord) -> str:
        registro = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "operacao": getattr(record, "operacao", "GERAL"),
            "message": record.getMessage(),
            "requestId": request_id_ctx.get(),
        }
        for campo in CAMPOS_EXTRAS:
            if hasattr(record, campo):
                registro[campo] = getattr(record, campo)
        if record.exc_info:
            registro["exception"] = self.formatException(record.exc_info)
        return json.dumps(registro, ensure_ascii=False)


def get_logger() -> logging.Logger:
    """Retorna o logger da aplicação, configurado uma única vez."""
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
