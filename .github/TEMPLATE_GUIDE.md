# My Python Starter Kit — Guia do Template

> Como criar um projeto novo a partir deste template. Este ficheiro fica em `.github/` e não é renderizado como README principal.

[![Use this template](https://img.shields.io/badge/Use%20this%20template-green?style=for-the-badge)](https://github.com/nunoetome/my_python_starter_kit/generate)

## O que recebes

- `logging_template.py` — logger com rotação e 9 estilos
- `requirements.txt` — placeholder
- `.gitignore` — Python curado
- `README.md` — README do projeto (a personalizar)
- Este guia

## Criar um repo novo

### Opção A — GitHub UI (recomendado)

1. Clica **Use this template → Create a new repository**
2. Escolhe owner/nome (ex: `meu_projeto`), `Public/Private`, **não** marques `Include all branches`
3. `Create repository` → `git clone` o novo repo

### Opção B — CLI `gh`

```bash
gh repo create meu_projeto --template nunoetome/my_python_starter_kit --public --clone
cd meu_projeto
```

> Nota: o novo repo tem histórico com 1 commit (unrelated history), não dá para fazer PR de volta ao template.

## Checklist pós-geração

Corre isto no novo repo:

- [ ] Renomear no `logging_template.py`:
  - `LOG_OUTPUT_PREFIX = '<<app>>'` → `<<meu_projeto>>`
  - `LOG_OUTPUT_FILE = os.path.join(LOG_FOLDER, 'app.log')` → nome do teu app
  - `LOG_FOLDER` se quiseres outro path
- [ ] Editar `README.md`:
  - Título, one-liner, badges, quick start, tabela de config
  - Remover banner `> **A usar como template?**` se já não for template
- [ ] `requirements.txt` — adicionar deps (`requests==2.32.3`)
- [ ] `git remote -v` confirmar `origin` aponta para o novo repo
- [ ] `python -m venv .venv && pip install -r requirements.txt`
- [ ] Testar logger: `python -c "from logging_template import setup_logging; setup_logging().info('ok')"` → deve criar `log_files/app.log`
- [ ] (Opcional) Apagar este ficheiro `.github/TEMPLATE_GUIDE.md` quando já não precisares
- [ ] Adicionar `LICENSE`, `CONTRIBUTING.md` se necessário

## Tour da estrutura

```
.
├── logging_template.py     # Configura via variáveis LOG_*
├── requirements.txt
├── .gitignore
├── README.md               # Documentação do teu projeto
└── .github/
    └── TEMPLATE_GUIDE.md   # Este ficheiro
```

## Personalização do logger

Topo de `logging_template.py`:

- Níveis: `LOG_LEVEL_GLOBAL/FILE/CONSOLE` (`DEBUG/INFO/WARNING/ERROR/CRITICAL`)
- Formatos: `LOG_FORMAT_FILE/CONSOLE` e variantes `*_ULTRA_DEBUG`
- Rotação: `LOG_MAX_BYTES`, `LOG_MAX_RECORDS`, `LOG_MAX_BACKUP`
- `setup_logging()` é o entrypoint ( `ini_logging()` mantido por compatibilidade)

Estilos visuais (banner `=`, secção `-`, função `~`, tag `[db]`, separator, box, timing) estão documentados no bloco `LIVRO DE ESTILO` do ficheiro.

## Sincronizar com o template upstream (opcional)

```bash
git remote add template https://github.com/nunoetome/my_python_starter_kit.git
git fetch template
git merge template/release/v0.1.0-beta --allow-unrelated-histories
```

## Contribuir para o template

PRs ao template devem ir para `nunoetome/my_python_starter_kit` branch `release/v0.1.0-beta` ou `dev`, não para o teu projeto derivado.
