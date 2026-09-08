import time
import sys
from config.config import get_config
from logging_component.logging_template import setup_logging

APP_NAME = "My Python Starter Kit"
APP_VERSION = "0.1.0-beta"

try:
    _log_cfg = get_config("logging")
except ValueError:
    _log_cfg = None
LOGGER = setup_logging(config=_log_cfg)


def main():
    t_app = time.perf_counter()

    LOGGER.info("=" * 49)
    LOGGER.info(f"{f' {APP_NAME} v{APP_VERSION} a iniciar ':=^49}")
    LOGGER.info("=" * 49)

    try:
        LOGGER.info("-" * 49)
        LOGGER.info(f"{' Exemplo Secção ':-^49}")
        LOGGER.info("-" * 49)

        t_sec = time.perf_counter()
        LOGGER.info("[app] A executar lógica principal...")
        LOGGER.debug(f"{' main() ':~^49}")

        time.sleep(0.05)

        LOGGER.info("[app] Lógica concluída")
        LOGGER.info(f"Exemplo Secção concluído em %.2fs", time.perf_counter() - t_sec)

        LOGGER.info("-" * 49)
        LOGGER.info(f"{' Fim Exemplo Secção ':-^49}")
        LOGGER.info("-" * 49)

    except Exception as exc:
        LOGGER.error("[app] Erro não tratado: %s", exc, exc_info=True)
        raise
    finally:
        LOGGER.info("Aplicação concluída em %.2fs", time.perf_counter() - t_app)
        LOGGER.info("=" * 49)
        LOGGER.info(f"{f' {APP_NAME} v{APP_VERSION} finalizado ':=^49}")
        LOGGER.info("=" * 49)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOGGER.warning("[app] Interrompido pelo utilizador")
        sys.exit(130)
    except Exception:
        sys.exit(1)
