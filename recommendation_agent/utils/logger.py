"""
==============================================================================
logger.py

Central logging utility

Usage:

from utils.logger import logger

logger.info("message")
logger.error("error")

==============================================================================

"""


import logging

from logging.handlers import RotatingFileHandler


from config import LOG_FILE, LOG_LEVEL





def create_logger():


    logger = logging.getLogger(
        "stock_research"
    )


    # Avoid duplicate logs when imported by many modules

    if logger.handlers:

        return logger



    logger.setLevel(

        getattr(

            logging,

            LOG_LEVEL.upper(),

            logging.INFO

        )

    )



    formatter = logging.Formatter(

        "%(asctime)s | %(levelname)s | %(message)s"

    )




    ##########################################################################
    # File Handler
    ##########################################################################

    file_handler = RotatingFileHandler(

        LOG_FILE,

        maxBytes=5 * 1024 * 1024,

        backupCount=3,

        encoding="utf-8"

    )


    file_handler.setFormatter(

        formatter

    )





    ##########################################################################
    # Console Handler
    ##########################################################################

    console_handler = logging.StreamHandler()


    console_handler.setFormatter(

        formatter

    )





    logger.addHandler(

        file_handler

    )


    logger.addHandler(

        console_handler

    )



    # Prevent root logger duplication

    logger.propagate = False



    return logger





logger = create_logger()




if __name__ == "__main__":


    logger.info(

        "Logger initialized"

    )


    logger.warning(

        "Sample warning"

    )


    logger.error(

        "Sample error"

    )