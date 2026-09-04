import time
import sys
from logging_component.logging_template import setup_logging

APP_NAME = "My Python Starter Kit"
APP_VERSION = "0.1.0-beta"

logger = setup_logging()


def main():
    t_app = time.perf_counter()

    logger.info("=" * 49)
    logger.info(f"{f' {APP_NAME} v{APP_VERSION} a iniciar ':=^49}")
    logger.info("=" * 49)

    try:
        logger.info("-" * 49)
        logger.info(f"{' Exemplo Secção ':-^49}")
        logger.info("-" * 49)

        t_sec = time.perf_counter()
        logger.info("[app] A executar lógica principal...")
        logger.debug(f"{' main() ':~^49}")

        time.sleep(0.05)

        logger.info("[app] Lógica concluída")
        logger.info(f"Exemplo Secção concluído em %.2fs", time.perf_counter() - t_sec)

        logger.info("-" * 49)
        logger.info(f"{' Fim Exemplo Secção ':-^49}")
        logger.info("-" * 49)

    except Exception as exc:
        logger.error("[app] Erro não tratado: %s", exc, exc_info=True)
        raise
    finally:
        logger.info("Aplicação concluída em %.2fs", time.perf_counter() - t_app)
        logger.info("=" * 49)
        logger.info(f"{f' {APP_NAME} v{APP_VERSION} finalizado ':=^49}")
        logger.info("=" * 49)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("[app] Interrompido pelo utilizador")
        sys.exit(130)
    except Exception:
        sys.exit(1)
