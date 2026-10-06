import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def get_engine():
    load_dotenv()
    driver = os.environ["DB_DRIVER"]
    server = os.environ["DB_SERVER"]
    database = os.environ["DB_NAME"]
    odbc_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_string)}")


if __name__ == "__main__":
    with get_engine().connect() as connection:
        print(connection.execute(text("SELECT DB_NAME()")).scalar())