import os
import jaydebeapi

from config import DATABASE_TYPE


class H2Database:

    def __init__(self):

        self.driver = "org.h2.Driver"

        # H2 database location
        self.url = "jdbc:h2:~/market_recommendation"

        # Project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # H2 jar inside project's bin folder
        self.jar = os.path.join(project_root, "bin", "h2-2.4.240.jar")

        if not os.path.exists(self.jar):
            raise FileNotFoundError(f"H2 JAR not found: {self.jar}")

        self.username = "sa"

        self.password = ""

        self.conn = None

    def connect(self):

        if self.conn is None:

            self.conn = jaydebeapi.connect(
                self.driver,
                self.url,
                [self.username, self.password],
                self.jar
            )

        return self.conn

    def close(self):

        try:
            if self.conn is not None:
                self.conn.close()
                print("H2 connection closed.")
        finally:
            self.conn = None