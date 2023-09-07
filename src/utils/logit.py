from functools import wraps

def mi_logger(funcion_original):
    import logging
    logging.basicConfig(filename=f"{format(funcion_original.__name__)}.log", level=logging.INFO)

    def funcion_envolvente(*args, **kwargs):
        logging.info(f"Ejecutado con args: {args}, y kwargs: {kwargs}")
        funcion_original(*args, **kwargs)
    return funcion_envolvente