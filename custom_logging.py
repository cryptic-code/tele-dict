import logging

def get_logger(module_name: str, file_name: str = 'misc.log', only_debug: bool = False) -> logging.Logger:
    """ Create an appropriate Logger instance for a module. """

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

    if not only_debug:
        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger