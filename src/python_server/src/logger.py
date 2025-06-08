try:
    from loguru import logger  # type: ignore
except ModuleNotFoundError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("tetris")

__all__ = ["logger"]
