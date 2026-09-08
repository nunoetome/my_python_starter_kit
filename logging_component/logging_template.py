"""logging_template.py — Sistema de logging configurável via config.yaml.

Disponibiliza logger reutilizável com níveis independentes para ficheiro e
consola, ultra debug mode (ficheiro/função/linha em DEBUG), prefixo
personalizado e rotação automática por tamanho e/ou número de registos.

Características:
    - Níveis configuráveis (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Formato ultra debug para mensagens DEBUG
    - Prefixo personalizado para logs agregados
    - Rotação automática (RotatingFileHandler) por tamanho e registos

Configuração:
    Parâmetros lidos de ``config/config.yaml`` secção ``logging`` via
    ``config.config.get_config("logging")``. Fallback para constantes
    locais se config ausente. Aceita ``dict`` explícito em
    ``setup_logging(config=...)``.

    Chaves suportadas: ``log_folder``, ``log_file``, ``log_prefix``,
    ``level``, ``level_file``/``file_level``, ``level_console``/
    ``console_level``, ``max_bytes``, ``max_records``, ``max_backup``,
    ``file_ultra_debug``, ``console_ultra_debug``.

Uso:
    from logging_component.logging_template import setup_logging, logger

    logger = setup_logging()
    logger.info("Aplicação iniciada")
    logger.debug("Detalhe com ultra debug")

    # com config explícita
    logger = setup_logging(config={"log_prefix": "[app]", "level": "DEBUG"})

Notas:
    - Instância global ``logger`` segue PEP 8 (minúsculas, não constante).
    - ``LOGGER`` mantido como alias para retrocompatibilidade.
    - Ficheiros com rotação ``app.log``, ``app_1.log`` ... ``app_N.log``.

Referência:
    https://github.com/nunoetome/my_python_starter_kit

Changelog:
    - 2026-09-04 | Nuno Tomé | 2.2 — Config via config.yaml, logger minúsculas
    - 2026-06-19 | Nuno Tomé | 2.1 — Livro de estilo de logs para AI e humanos
    - 2026-06-02 | Nuno Tomé | 2.0 — RotatingFileHandler, PEP 257, setup_logging()
    - 2025-01-22 | Nuno Tomé | 1.0 — UTF-8 na escrita dos ficheiros de log
"""

import logging
import os

try:
    from config.config import CONFIG_YAML as _CONFIG_YAML
    from config.config import get_config as _get_config
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    try:
        _root = _Path(__file__).resolve().parent.parent
        if str(_root) not in _sys.path:
            _sys.path.insert(0, str(_root))
        from config.config import CONFIG_YAML as _CONFIG_YAML
        from config.config import get_config as _get_config
    except ImportError:
        _CONFIG_YAML = {}
        _get_config = None


# --- Configuração de níveis ------------------------------------------------
# Descomente o nível pretendido. LOG_LEVEL_GLOBAL sobrepõe-se aos restantes.

LOG_LEVEL_GLOBAL = logging.INFO
LOG_LEVEL_FILE = logging.INFO
LOG_LEVEL_CONSOLE = logging.INFO

# --- Caminhos e prefixo ----------------------------------------------------
LOG_FOLDER = 'log_files'
LOG_OUTPUT_FILE = os.path.join(LOG_FOLDER, 'app.log')
LOG_OUTPUT_PREFIX = '<<app>>'

# --- Formatos --------------------------------------------------------------
LOG_FORMAT_FILE = (
    LOG_OUTPUT_PREFIX
    + ' %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOG_FORMAT_CONSOLE = LOG_OUTPUT_PREFIX + ' %(levelname)s - %(message)s'

# --- Ultra debug mode ------------------------------------------------------
# Quando ativo, as mensagens DEBUG incluem ficheiro, função e linha.
FILE_ULTRA_DEBUG = True
CONSOLE_ULTRA_DEBUG = True

LOG_FORMAT_FILE_ULTRA_DEBUG = (
    LOG_FORMAT_FILE + ' - [%(filename)s - %(funcName)s - %(lineno)d]'
)
LOG_FORMAT_CONSOLE_ULTRA_DEBUG = (
    LOG_FORMAT_CONSOLE + ' - [%(filename)s - %(funcName)s - %(lineno)d]'
)

# --- Rotação de logs -------------------------------------------------------
# 0 = desligado
LOG_MAX_BYTES = 10485760       # bytes
LOG_MAX_RECORDS = 5000     # número de registos
LOG_MAX_BACKUP = 10      # número máximo de ficheiros de arquivo
# ---------------------------------------------------------------------------


_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "NOTSET": logging.NOTSET,
}


def _parse_level(value, default):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return _LEVEL_MAP.get(value.upper(), default)
    return default


def _resolve_logging_config(explicit=None):
    if isinstance(explicit, dict) and explicit:
        return explicit
    if _get_config is not None:
        try:
            cfg = _get_config("logging")
            if isinstance(cfg, dict) and cfg:
                return cfg
        except ValueError:
            pass
    if isinstance(_CONFIG_YAML, dict):
        cfg = _CONFIG_YAML.get("logging")
        if isinstance(cfg, dict):
            return cfg
    return {}


logger = logging.getLogger(__name__)
LOGGER = logger


class RotatingFileHandler(logging.Handler):
    """Handler com rotação automática por tamanho e/ou número de registos.

    A rotação ocorre quando o ficheiro atual atinge o limite de tamanho
    (LOG_MAX_BYTES) **ou** o limite de registos (LOG_MAX_RECORDS),
    conforme o que acontecer primeiro. Os ficheiros são renomeados em
    cascata (logrotate-style) até ao número máximo de arquivos definido
    em LOG_MAX_BACKUP.

     Arquivos gerados::

         app.log       ← ficheiro de escrita atual
         app_1.log     ← arquivo mais recente
         app_2.log     ← ...
         app_N.log     ← arquivo mais antigo (removido no próximo ciclo)
    """

    def __init__(self, filename, mode='a', encoding=None,
                 max_bytes=0, max_records=0, max_backup=0):
        super().__init__()
        self.filename = filename
        self.base_name, self.ext = os.path.splitext(filename)
        self.mode = mode
        self.encoding = encoding
        self.max_bytes = max_bytes
        self.max_records = max_records
        self.max_backup = max_backup
        self.record_count = 0
        self.terminator = '\n'
        self.stream = None
        self._open()

    def _open(self):
        dirname = os.path.dirname(self.filename)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        self.stream = open(self.filename, self.mode, encoding=self.encoding)
        self.record_count = 0

    def _archive_name(self, index):
        return f"{self.base_name}_{index}{self.ext}"

    def _should_rotate(self):
        if self.max_backup <= 0:
            return False
        if self.max_records > 0 and self.record_count >= self.max_records:
            return True
        if self.max_bytes > 0:
            try:
                if os.path.getsize(self.filename) >= self.max_bytes:
                    return True
            except OSError:
                pass
        return False

    def _rotate(self):
        self.stream.close()

        oldest = self._archive_name(self.max_backup)
        if os.path.exists(oldest):
            os.remove(oldest)

        for i in range(self.max_backup - 1, 0, -1):
            src = self._archive_name(i)
            dst = self._archive_name(i + 1)
            if os.path.exists(src):
                os.replace(src, dst)

        if os.path.exists(self.filename):
            os.replace(self.filename, self._archive_name(1))

        self._open()

    def emit(self, record):
        try:
            msg = self.format(record) + self.terminator
            self.stream.write(msg)
            self.record_count += 1
            self.flush()

            if self._should_rotate():
                self._rotate()
        except Exception:
            self.handleError(record)

    def flush(self):
        if self.stream and not self.stream.closed:
            self.stream.flush()

    def close(self):
        if self.stream and not self.stream.closed:
            self.stream.close()
        super().close()


def ini_logging(config=None):
    """[LEGACY] Configura e devolve o logger da aplicação.

    Mantida apenas para retrocompatibilidade. Para novos desenvolvimentos
    use :func:`setup_logging`.

    Args:
        config: dict opcional com chaves de ``config.yaml:logging``.
            Se None, tenta carregar via ``config.get_config("logging")``
            e cai para constantes deste módulo.
    """
    cfg = _resolve_logging_config(config)
    log_folder = cfg.get("log_folder", LOG_FOLDER)
    log_file = cfg.get("log_file", os.path.basename(LOG_OUTPUT_FILE))
    log_prefix = cfg.get("log_prefix", LOG_OUTPUT_PREFIX)
    log_level_global = _parse_level(cfg.get("level", LOG_LEVEL_GLOBAL), LOG_LEVEL_GLOBAL)
    log_level_file = _parse_level(cfg.get("level_file", cfg.get("file_level", LOG_LEVEL_FILE)), LOG_LEVEL_FILE)
    log_level_console = _parse_level(cfg.get("level_console", cfg.get("console_level", LOG_LEVEL_CONSOLE)), LOG_LEVEL_CONSOLE)
    log_max_bytes = int(cfg.get("max_bytes", LOG_MAX_BYTES))
    log_max_records = int(cfg.get("max_records", LOG_MAX_RECORDS))
    log_max_backup = int(cfg.get("max_backup", LOG_MAX_BACKUP))
    file_ultra = bool(cfg.get("file_ultra_debug", FILE_ULTRA_DEBUG))
    console_ultra = bool(cfg.get("console_ultra_debug", CONSOLE_ULTRA_DEBUG))
    log_output_file = os.path.join(log_folder, log_file)
    log_format_file = log_prefix + ' %(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_format_console = log_prefix + ' %(levelname)s - %(message)s'
    log_format_file_ultra = log_format_file + ' - [%(filename)s - %(funcName)s - %(lineno)d]'
    log_format_console_ultra = log_format_console + ' - [%(filename)s - %(funcName)s - %(lineno)d]'

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(log_level_global)

    file_handler = RotatingFileHandler(
        log_output_file,
        mode="a",
        encoding="utf-8",
        max_bytes=log_max_bytes,
        max_records=log_max_records,
        max_backup=log_max_backup,
    )
    file_handler.setLevel(log_level_file)

    if file_ultra:
        class CustomDebugFormatteFile(logging.Formatter):
            def format(self, record):
                if record.levelno == logging.DEBUG:
                    self._style._fmt = log_format_file_ultra
                else:
                    self._style._fmt = log_format_file
                return super().format(record)
        file_handler.setFormatter(CustomDebugFormatteFile())
    else:
        file_handler.setFormatter(logging.Formatter(log_format_file))

    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_console)

    if console_ultra:
        class CustomDebugFormatter(logging.Formatter):
            def format(self, record):
                if record.levelno == logging.DEBUG:
                    self._style._fmt = log_format_console_ultra
                else:
                    self._style._fmt = log_format_console
                return super().format(record)
        console_handler.setFormatter(CustomDebugFormatter())
    else:
        console_handler.setFormatter(logging.Formatter(log_format_console))

    logger.addHandler(console_handler)

    return logger


def setup_logging(config=None):
    """Configura e devolve o logger da aplicação.

    Wrapper que chama :func:`ini_logging` para garantir
    retrocompatibilidade.
    """
    return ini_logging(config=config)


# =================================================================
# LIVRO DE ESTILO DE LOGS — Especificação para AI e Humanos
# =================================================================
#
# Este bloco define as convenções visuais para o CONTEÚDO textual
# das mensagens de log (não o formato do LogRecord — isso é feito
# pelos Formatters já configurados). O objetivo é garantir
# consistência visual em todas as aplicações que usam este template.
#
# Cada estilo é definido por um conjunto fixo de campos para que
# uma AI (ou humano) consiga aplicá-lo de forma determinística.
#
# -----------------------------------------------------------------
# REGRAS GLOBAIS (aplicam-se a todos os estilos)
# -----------------------------------------------------------------
#
#   R1. WIDTH padrão = 49 colunas. NUNCA exceder 79 colunas.
#   R2. Caracteres por nível hierárquico:
#       Aplicação → '='
#       Secção    → '-'
#       Função    → '~'   (discreto, para passos internos)
#       Separador → '-'   (pode ser '-' ou '.' conforme contexto)
#   R3. Banners (app / secção / função) são sempre 3 linhas:
#       linha 1: char * width
#       linha 2: título formatado (center para início, right para fim)
#       linha 3: char * width
#   R4. Tags de contexto usam o formato [tag] no INÍCIO da mensagem,
#       colado ao texto (sem espaço entre ] e o texto).
#       Tags em lowercase, sem underscores (ex: [pdf], [db], [api]).
#   R5. Rodapés (APP_END, SECTION_END) usam o MESMO carácter e
#       largura do banner de abertura correspondente. O texto
#       alinha à direita com o padrão " Fim <nome> " ou " <nome> finalizado ".
#   R6. Para todos os alinhamentos, usar f-strings com alignment
#       specs do Python (:<width, :^width, :>width) preenchidas
#       com o carácter do estilo.
#   R7. Nível de log: Banners e separadores usam INFO.
#       Tags herdam o nível do contexto onde são usadas.
#       Box usa o nível do conteúdo que está a emoldurar.
#   R8. Se o título for maior que width-4, truncar com "…" no final
#       para caber. Se for menor, centrar com espaços simétricos.
#
# -----------------------------------------------------------------
# STYLE 1: BANNER_APP_START
#   Usage:    Início da aplicação. Colocar imediatamente após a
#             configuração do logger (setup_logging / ini_logging).
#   Severity: INFO
#   Rule:     Título centrado "<nome> a iniciar". 3 linhas com '='.
#   Width:    49
#   Char:     =
#   Align:    center (linha do título)
#   Lines:    3
#
#   Output:
#     ===================================================
#     ============== AppX v1.0 a iniciar ===============
#     ===================================================
#
#   Code:
#     logger.info("=" * 49)
#     logger.info(f"{' AppX v1.0 a iniciar ':=^49}")
#     logger.info("=" * 49)
#
# -----------------------------------------------------------------
# STYLE 2: BANNER_APP_END
#   Usage:    Fecho da aplicação, última mensagem antes de terminar.
#   Severity: INFO
#   Rule:     Texto alinhado à direita. Mesmo char e width do
#             BANNER_APP_START. Padrão: " <nome> finalizado ".
#   Width:    49
#   Char:     =
#   Align:    right (linha do título)
#   Lines:    3
#
#   Output:
#     ===================================================
#     ============== AppX v1.0 finalizado ===============
#     ===================================================
#
#   Code:
#     logger.info("=" * 49)
#     logger.info(f"{' AppX v1.0 finalizado ':=^49}")
#     logger.info("=" * 49)
#
# -----------------------------------------------------------------
# STYLE 3: BANNER_SECTION_START
#   Usage:    Início de uma sub-secção lógica da aplicação
#             (ex: "Processar PDFs", "Exportar dados", "Validar formulários").
#   Severity: INFO
#   Rule:     Título centrado com '-'. Mais discreto que o banner principal.
#   Width:    49
#   Char:     -
#   Align:    center
#   Lines:    3
#
#   Output:
#     ---------------------------------------------------
#     ---------------- Processar PDFs ------------------
#     ---------------------------------------------------
#
#   Code:
#     logger.info("-" * 49)
#     logger.info(f"{' Processar PDFs ':-^49}")
#     logger.info("-" * 49)
#
# -----------------------------------------------------------------
# STYLE 4: BANNER_SECTION_END
#   Usage:    Fecho de uma sub-secção. Espelha o BANNER_SECTION_START.
#   Severity: INFO
#   Rule:     Texto alinhado à direita. Padrão: " Fim <nome> ".
#   Width:    49
#   Char:     -
#   Align:    right
#   Lines:    3
#
#   Output:
#     ---------------------------------------------------
#     ---------------- Fim Processar PDFs ---------------
#     ---------------------------------------------------
#
#   Code:
#     logger.info("-" * 49)
#     logger.info(f"{' Fim Processar PDFs ':-^49}")
#     logger.info("-" * 49)
#
# -----------------------------------------------------------------
# STYLE 5: BANNER_FUNCTION
#   Usage:    Início de uma função/método crítico cuja execução
#             se quer destacar no log (ex: init_db, parse_xml).
#             NÃO usar em todas as funções — só nas relevantes.
#   Severity: DEBUG
#   Rule:     Título centrado com '~'. Mais discreto e curto.
#             Formato: "~~~ nome_funcao() ~~~" ou "~~~ descrição ~~~".
#   Width:    49
#   Char:     ~
#   Align:    center
#   Lines:    1 (apenas a linha do título, sem barras superior/inferior)
#
#   Output:
#     ~~~~~~~~~~~~~~~~~ init_database() ~~~~~~~~~~~~~~~~~~
#
#   Code:
#     logger.debug(f"{' init_database() ':~^49}")
#
# -----------------------------------------------------------------
# STYLE 6: TAG
#   Usage:    Prefixar mensagens com o nome do componente, serviço
#             ou módulo que as gerou. Facilita filtragem e leitura
#             de logs agregados.
#   Severity: qualquer (herda o nível da mensagem)
#   Rule:     [tag] no início, colado à mensagem. Tag em lowercase,
#             sem underscores, sem espaços. Máximo 12 caracteres.
#   Width:    N/A
#   Char:     N/A
#   Align:    left
#
#   Output:
#     [pdf] A processar documento 123
#     [pdf] Documento 123 convertido com sucesso
#     [db] Ligação à base de dados estabelecida
#     [db] Query executada em 0.34s
#     [api] GET /users -> 200 OK
#     [api] POST /invoice -> 201 Created
#
#   Code:
#     logger.info("[pdf] A processar documento %d", doc_id)
#     logger.info("[pdf] Documento %d convertido com sucesso", doc_id)
#     logger.info("[db] Ligação à base de dados estabelecida")
#     logger.info("[db] Query executada em %.2fs", elapsed)
#     logger.info("[api] GET /users -> 200 OK")
#     logger.info("[api] POST /invoice -> 201 Created")
#
# -----------------------------------------------------------------
# STYLE 7: SEPARATOR
#   Usage:    Separar visualmente blocos de log dentro de uma secção
#             ou entre iterações de um loop relevante.
#   Severity: DEBUG
#   Rule:     Linha única com o carácter repetido width vezes.
#   Width:    49
#   Char:     -  (pode usar '.' para separadores ainda mais discretos)
#   Align:    N/A
#   Lines:    1
#
#   Output:
#     ---------------------------------------------------
#
#   Code:
#     logger.debug("-" * 49)
#
# -----------------------------------------------------------------
# STYLE 8: BOX
#   Usage:    Emoldurar informação estruturada como tabelas, resumos
#             de processamento, ou dados multi-linha que beneficiem
#             de destaque visual.
#   Severity: mesmo nível dos dados que contém (geralmente INFO)
#   Rule:     Linha de topo com título (se existir), linhas de
#             conteúdo prefixadas com "| ", linha de base.
#             Bordas usam '-' (horizontal) e '|' (vertical).
#   Width:    49 (conteúdo interno: width - 4 para margens)
#   Char:     - (horizontal), | (vertical)
#   Align:    left (conteúdo)
#   Lines:    N+2 (N linhas de conteúdo + topo + base)
#
#   Output:
#     ---------------------------------------------------
#     | Resumo do processamento                         |
#     |-------------------------------------------------|
#     | Documentos processados  : 150                   |
#     | Sucesso                 : 145                   |
#     | Erros                   : 5                     |
#     | Tempo total             : 12.4s                 |
#     ---------------------------------------------------
#
#   Code:
#     lines = [
#         "| Resumo do processamento                         |",
#         "|-------------------------------------------------|",
#         "| Documentos processados  : 150                   |",
#         "| Sucesso                 : 145                   |",
#         "| Erros                   : 5                     |",
#         "| Tempo total             : 12.4s                 |",
#     ]
#     for line in lines:
#         logger.info(line)
#     # Nota: as bordas superior e inferior podem ser geradas
#     # com SEPARATOR se o alinhamento com '|' não for crítico,
#     # ou construídas manualmente para corresponder à largura
#     # exacta das linhas de conteúdo (neste caso 51 caracteres).
#
# -----------------------------------------------------------------
# STYLE 9: TIMING
#   Usage:    Medir e registar o tempo de execução de operações a
#             3 níveis: APP, SECTION, FUNCTION.
#   Severity: INFO (app/secção), DEBUG (função/bloco)
#   Rule:     Usar time.perf_counter() para medir o tempo decorrido.
#             O valor é sempre apresentado em segundos com 2 casas
#             decimais (centésimas de segundo) — %.2fs.
#             NUNCA converter para ms, µs ou outras unidades.
#   Unit:     centésimas de segundo (X.XXs)
#   Align:    left
#
#   --- VARIANT A: TIMING_APP ---
#   Usage:    Tempo total de execução da aplicação. Colocar
#             imediatamente ANTES do BANNER_APP_END.
#
#   Output:
#     Aplicação concluída em 142.35s
#
#   Code:
#     t_app_start = time.perf_counter()
#     # ... toda a lógica da aplicação ...
#     logger.info("Aplicação concluída em %.2fs", time.perf_counter() - t_app_start)
#
#   --- VARIANT B: TIMING_SECTION ---
#   Usage:    Tempo de execução de uma sub-secção. Colocar
#             imediatamente ANTES do BANNER_SECTION_END.
#             Pode incluir contexto adicional entre parênteses.
#
#   Output:
#     Processar PDFs concluído em 12.40s (150 documentos)
#
#   Code:
#     t_sec = time.perf_counter()
#     # ... sub-processo ...
#     logger.info("Processar PDFs concluído em %.2fs (%d docs)", time.perf_counter() - t_sec, count)
#
#   --- VARIANT C: TIMING_FUNCTION ---
#   Usage:    Tempo de uma função específica ou bloco de código
#             dentro de uma função. Usar para funções/blocos
#             críticos cuja performance se quer monitorizar.
#             Pode ser combinado com TAG (STYLE 6) para identificar
#             o componente.
#
#   Output:
#     init_database() -> 0.34s
#     [pdf] render_page() -> 0.12s
#     [db] batch_insert() -> 1.05s
#
#   Code:
#     t = time.perf_counter()
#     result = init_database()
#     logger.debug("init_database() -> %.2fs", time.perf_counter() - t)
#     # combinado com TAG:
#     logger.debug("[pdf] render_page() -> %.2fs", time.perf_counter() - t)
#
# -----------------------------------------------------------------
# EXEMPLO COMPLETO DE APLICAÇÃO DOS ESTILOS
# -----------------------------------------------------------------
#
# O ficheiro de log resultante de uma aplicação que siga este guia
# terá o seguinte aspecto (assumindo o prefixo e formato base já
# configurados no logger):
#
#   <<app>> 2025-06-18 10:00:01 - __main__ - INFO - ===================================================
#   <<app>> 2025-06-18 10:00:01 - __main__ - INFO - ============== AppX v1.0 a iniciar ===============
#   <<app>> 2025-06-18 10:00:01 - __main__ - INFO - ===================================================
#   <<app>> 2025-06-18 10:00:02 - __main__ - INFO - ---------------------------------------------------
#   <<app>> 2025-06-18 10:00:02 - __main__ - INFO - ---------------- Processar PDFs ------------------
#   <<app>> 2025-06-18 10:00:02 - __main__ - INFO - ---------------------------------------------------
#   <<app>> 2025-06-18 10:00:03 - __main__ - DEBUG - ~~~~~~~~~~~~~~~~~ init_database() ~~~~~~~~~~~~~~~~~~
#   <<app>> 2025-06-18 10:00:03 - __main__ - INFO - [pdf] A processar documento 1
#   <<app>> 2025-06-18 10:00:04 - __main__ - INFO - [pdf] A processar documento 2
#   <<app>> 2025-06-18 10:00:04 - __main__ - DEBUG - ---------------------------------------------------
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - [pdf] Documento 1 convertido com sucesso
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - [pdf] Documento 2 convertido com sucesso
#   <<app>> 2025-06-18 10:00:05 - __main__ - DEBUG - [pdf] render_page() -> 0.12s
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - ---------------------------------------------------
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - | Resumo do processamento                         |
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - |-------------------------------------------------|
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - | Documentos processados  : 2                     |
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - | Sucesso                 : 2                     |
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - | Erros                   : 0                     |
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - ---------------------------------------------------
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - Processar PDFs concluído em 12.40s (2 documentos)
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - ---------------------------------------------------
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - ---------------- Fim Processar PDFs ---------------
#   <<app>> 2025-06-18 10:00:05 - __main__ - INFO - ---------------------------------------------------
#   <<app>> 2025-06-18 10:00:06 - __main__ - INFO - Aplicação concluída em 12.85s
#   <<app>> 2025-06-18 10:00:06 - __main__ - INFO - ===================================================
#   <<app>> 2025-06-18 10:00:06 - __main__ - INFO - ============== AppX v1.0 finalizado ===============
#   <<app>> 2025-06-18 10:00:06 - __main__ - INFO - ===================================================
#
# -----------------------------------------------------------------
# NOTAS PARA A AI
# -----------------------------------------------------------------
#
#   - Usar SEMPRE f-strings com alignment specs do Python
#     (:^width, :<width, :>width) para centrar/alinhar texto.
#   - NUNCA hardcodar espaços manualmente para alinhar — usar as
#     formatting specs que são determinísticas e não dependem de
#     contagem manual.
#   - Para o BOX, calcular a largura das bordas com base na linha
#     mais longa do conteúdo, garantindo pelo menos width-4 para
#     as margens internas.
#   - Tags devem ser curtas (<=12 chars) e descritivas do componente.
#     Evitar tags genéricas como [app] ou [main].
#   - Banners de função (STYLE 5) só devem ser usados em funções
#     realmente críticas (ex: init, parse, export, connect).
#     Não poluir o log com banners em funções triviais.
#   - Manter 1 linha em branco (logger.info("")) entre blocos
#     lógicos distintos para melhor legibilidade.
#   - Para medições de tempo (STYLE 9), usar SEMPRE
#     time.perf_counter() para maior precisão. Chamar uma VEZ no
#     início do bloco a medir e calcular elapsed no final.
#     NUNCA converter para ms/µs — ficar sempre em centésimas de
#     segundo com %.2fs.
# =================================================================

# Exemplo de uso
def main():
    import time
    log = setup_logging()
    t_app = time.perf_counter()
    log.info("=" * 49)
    log.info(f"{' logging_template a iniciar ':=^49}")
    log.info("=" * 49)
    log.info("-" * 49)
    log.info(f"{' Exemplo Seccao ':-^49}")
    log.info("-" * 49)
    log.info("[demo] Mensagem INFO com prefixo do config.yaml")
    log.debug("[demo] Mensagem DEBUG com ultra debug")
    log.debug(f"{' main() ':~^49}")
    time.sleep(0.05)
    log.info("Exemplo Seccao concluido em %.2fs", time.perf_counter() - t_app)
    log.info("-" * 49)
    log.info(f"{' Fim Exemplo Seccao ':-^49}")
    log.info("-" * 49)
    log.info("Aplicacao concluida em %.2fs", time.perf_counter() - t_app)
    log.info("=" * 49)
    log.info(f"{' logging_template finalizado ':=^49}")
    log.info("=" * 49)


if __name__ == "__main__":
    main()
