"""
==============================================================================
h2_database.py

H2 Database Connection Utility

Creates and manages a single H2 database connection for the application.

Database Location:
<Project Root>/market_recommendation.mv.db

This implementation is portable and works on:

- Windows
- Linux
- Cloud VM
- Docker

==============================================================================

"""

import jaydebeapi

from config import (
    DATABASE_DRIVER,
    DATABASE_URL,
    DATABASE_USER,
    DATABASE_PASSWORD,
    H2_JAR,
    DATABASE_DEBUG
)

from utils.logger import logger


class H2Database:

    ##########################################################################
    # Constructor
    ##########################################################################

    def __init__(self):

        self.driver = DATABASE_DRIVER

        self.url = DATABASE_URL

        self.username = DATABASE_USER

        self.password = DATABASE_PASSWORD

        self.jar = str(H2_JAR)

        self.conn = None

    ##########################################################################
    # Connect
    ##########################################################################

    def connect(self):

        if self.conn is None:

            if DATABASE_DEBUG:

                logger.info("=" * 80)
                logger.info("Connecting to H2 Database")
                logger.info("Driver       : %s", self.driver)
                logger.info("Database URL : %s", self.url)
                logger.info("H2 Jar       : %s", self.jar)
                logger.info("=" * 80)

            self.conn = jaydebeapi.connect(

                self.driver,

                self.url,

                [

                    self.username,

                    self.password

                ],

                self.jar

            )

            cursor = self.conn.cursor()

            cursor.execute(

                "SELECT DATABASE_PATH()"

            )

            database_path = cursor.fetchone()[0]

            logger.info(

                "Connected to H2 Database : %s",

                database_path

            )

            cursor.close()

        return self.conn

    ##########################################################################
    # Close Connection
    ##########################################################################

    def close(self):

        try:

            if self.conn is not None:

                self.conn.close()

                logger.info(

                    "H2 database connection closed."

                )

        except Exception as ex:

            logger.warning(

                "Error closing H2 connection : %s",

                ex

            )

        finally:

            self.conn = None