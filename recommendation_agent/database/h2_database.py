import jaydebeapi

from config import DATABASE_TYPE


class H2Database:

    def __init__(self):

        self.driver = "org.h2.Driver"

        self.url = "jdbc:h2:~/market_recommendation"

        self.jar = r"C:\Program Files (x86)\H2\bin\h2-2.4.240.jar"

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