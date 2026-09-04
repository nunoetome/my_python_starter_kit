# My Python Starter Kit

> Template minimalista para projetos Python — com `logging_template.py` reutilizável, rotação automática e livro de estilo para logs legíveis por humanos e IA.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Template](https://img.shields.io/badge/template-use%20this%20template-brightgreen)](https://github.com/nunoetome/my_python_starter_kit/generate)

> **A usar como template?** Vê [`.github/TEMPLATE_GUIDE.md`](.github/TEMPLATE_GUIDE.md) para criar um repo novo em 1 clique.

## O que inclui

- **`logging_template.py`** — módulo único, sem dependências (stdlib)
  - Níveis configuráveis por `LOG_LEVEL_GLOBAL / FILE / CONSOLE`
  - `Ultra debug mode` (formato extra `filename:func:lineno` só para `DEBUG`)
  - `RotatingFileHandler` por tamanho (`LOG_MAX_BYTES`) e/ou registos (`LOG_MAX_RECORDS`)
  - Prefixo `<<app>>` para filtragem em logs agregados
  - 9 estilos visuais documentados no próprio ficheiro
- **`requirements.txt`** — placeholder comentado
- **`.gitignore`** — Python curado (`__pycache__/`, `.venv/`, `log_files/`, `*.log`, etc.)

## Quick Start

```bash
git clone https://github.com/nunoetome/my_python_starter_kit.git meu_projeto
cd meu_projeto
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

```python
from logging_template import setup_logging
import time

logger = setup_logging()

logger.info("=" * 49)
logger.info(f"{' Minha App v1.0 a iniciar ':=^49}")
logger.info("=" * 49)

t = time.perf_counter()
logger.info("[app] A processar...")
time.sleep(0.1)
logger.info("[app] Concluído em %.2fs", time.perf_counter() - t)

logger.info("=" * 49)
logger.info(f"{' Minha App v1.0 finalizado ':=^49}")
logger.info("=" * 49)
```

Log gerado em `log_files/app.log` + consola.

## Configuração

Edita o topo de `logging_template.py`:

| Variável | Default | Descrição |
|---|---|---|
| `LOG_LEVEL_GLOBAL` | `INFO` | Nível global (sobrepõe file/console) |
| `LOG_LEVEL_FILE` | `INFO` | Nível ficheiro |
| `LOG_LEVEL_CONSOLE` | `INFO` | Nível consola |
| `LOG_FOLDER` | `log_files` | Pasta de logs (criada se não existir) |
| `LOG_OUTPUT_FILE` | `log_files/app.log` | Ficheiro atual |
| `LOG_OUTPUT_PREFIX` | `<<app>>` | Prefixo p/ `grep` |
| `LOG_MAX_BYTES` | `10485760` (10 MB) | 0 = sem rotação por tamanho |
| `LOG_MAX_RECORDS` | `5000` | 0 = sem rotação por registos |
| `LOG_MAX_BACKUP` | `10` | Nº de arquivos `app_1.log` … `app_N.log` |
| `FILE_ULTRA_DEBUG` | `True` | Formato alargado no ficheiro p/ `DEBUG` |
| `CONSOLE_ULTRA_DEBUG` | `True` | Formato alargado na consola p/ `DEBUG` |

Rotação: quando `app.log` atinge `LOG_MAX_BYTES` **ou** `LOG_MAX_RECORDS`, roda em cascata `app.log → app_1.log → … → app_10.log`.

## Estilos de log

O ficheiro documenta 9 estilos (banner app/secção/função, tag `[api]`, separator, box, timing). Exemplo condensado:

```python
logger.info("-" * 49)
logger.info(f"{' Processar PDFs ':-^49}")
logger.info("-" * 49)
logger.info("[pdf] A processar documento %d", 123)
logger.debug(f"{' init_database() ':~^49}")
logger.debug("-" * 49)
```

Vê o bloco `LIVRO DE ESTILO DE LOGS` em `logging_template.py` para spec completa.

## Estrutura

```
.
├── .gitignore
├── .github/
│   └── TEMPLATE_GUIDE.md   # guia "Use this template"
├── logging_template.py     # módulo principal
├── requirements.txt
└── README.md
```

Adiciona os teus módulos base a partir daqui (ex: `config.py`, `utils/`, `src/`).

## Roadmap

- `v0.1.0-beta` — tábua rasa (este template)
- `v0.0.2-alpha` / `v0.0.1-alpha` — versões anteriores arquivadas (branch `prod`)

## Licença

MIT — vê `LICENSE` (a adicionar se necessário).
