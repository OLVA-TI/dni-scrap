import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_USERSCHEMA = os.getenv("DB_USERSCHEMA")
DB_PASSWORD = os.getenv("DB_PASSWORD")

pool = cx_Oracle.SessionPool(
            user=DB_USERNAME,
            password=DB_PASSWORD,
            dsn=cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_DATABASE),
            min=2,
            max=10,
            increment=2,
            encoding="UTF-8"
        )

def get_database_connection():
    try:
        connection = pool.acquire()
        return connection
    except cx_Oracle.Error as error:
        print('Error al conectar a Oracle:', error)
        return None