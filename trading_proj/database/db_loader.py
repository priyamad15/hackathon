from pathlib import Path

import pandas as pd

from database.h2_database import H2Database
from utils.logger import logger


class DatabaseLoader:

    def __init__(self):

        self.database = H2Database()
        self.connection = self.database.connect()
        self.cursor = self.connection.cursor()

    ##########################################################################
    # Infer SQL datatype
    ##########################################################################

    def get_sql_type(self, dtype):

        if pd.api.types.is_integer_dtype(dtype):
            return "BIGINT"

        elif pd.api.types.is_float_dtype(dtype):
            return "DOUBLE"

        elif pd.api.types.is_bool_dtype(dtype):
            return "BOOLEAN"

        else:
            return "VARCHAR(500)"

    ##########################################################################
    # Load CSV into H2
    ##########################################################################

    def load_csv(self, csv_file):

        csv_path = Path(csv_file)

        if not csv_path.exists():
            raise FileNotFoundError(f"{csv_file} not found.")

        logger.info("Loading CSV : %s", csv_path.name)

        table_name = csv_path.stem.upper()

        df = pd.read_csv(csv_path)

        columns = [
            f'"{column}" {self.get_sql_type(df[column].dtype)}'
            for column in df.columns
        ]

        create_sql = f"""
        CREATE TABLE {table_name}
        (
            {', '.join(columns)}
        )
        """

        placeholders = ",".join(["?"] * len(df.columns))

        insert_sql = f"""
        INSERT INTO {table_name}
        VALUES ({placeholders})
        """

        try:

            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

            self.cursor.execute(create_sql)

            for row in df.itertuples(index=False, name=None):
                self.cursor.execute(insert_sql, row)

            self.connection.commit()

            print("\n========== VERIFY DATABASE ==========")

            self.cursor.execute("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA='PUBLIC'
            """)

            tables = self.cursor.fetchall()

            print("Tables in database:")

            for table in tables:
                print(table[0])

            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")

            count = self.cursor.fetchone()[0]

            print(f"Rows in {table_name} : {count}")

            print("=====================================\n")

            logger.info(
                "%s loaded successfully (%s rows)",
                table_name,
                count
            )

        except Exception:

            self.connection.rollback()

            logger.exception(
                "Failed loading table %s",
                table_name
            )

            raise

    ##########################################################################
    # Close resources
    ##########################################################################

    def close(self):

        try:

            if self.cursor is not None:
                self.cursor.close()
                logger.info("Database cursor closed.")

        except Exception as ex:
            logger.warning("Error closing cursor: %s", ex)

        try:

            if self.database is not None:
                self.database.close()
                logger.info("Database connection closed.")

        except Exception as ex:
            logger.warning("Error closing connection: %s", ex)

        finally:

            self.cursor = None
            self.connection = None
            self.database = None