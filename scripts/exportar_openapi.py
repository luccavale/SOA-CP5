"""Gera docs/openapi.yaml e docs/openapi.json a partir da aplicação.

Uso (na raiz do projeto):  python -m scripts.exportar_openapi
"""
import json
from pathlib import Path

import yaml

from app.main import app

DOCS = Path(__file__).resolve().parent.parent / "docs"


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    spec = dict(app.openapi())
    spec = {
        "openapi": spec["openapi"],
        "info": spec["info"],
        "servers": [{"url": "http://localhost:8000", "description": "Execução local"}],
        **{k: v for k, v in spec.items() if k not in ("openapi", "info")},
    }
    (DOCS / "openapi.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    (DOCS / "openapi.yaml").write_text(
        yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    print(f"Especificação OpenAPI gerada em {DOCS}")


if __name__ == "__main__":
    main()
