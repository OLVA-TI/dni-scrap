import os
import cx_Oracle
import requests
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno para la base de datos
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_USERSCHEMA = os.getenv("DB_USERSCHEMA")
DB_PASSWORD = os.getenv("DB_PASSWORD")

API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")


def connect_to_oracle():
    try:
        dsn = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_DATABASE)
        connection = cx_Oracle.connect(user=DB_USERNAME, password=DB_PASSWORD, dsn=dsn)
        return connection
    except cx_Oracle.Error as error:
        print('Error al conectar a Oracle:', error)
        return None

def insert_into_table(connection, data):
    try:
        cursor = connection.cursor()

        merge_sql = """
        MERGE INTO datos_dni dd
        USING (
            SELECT :dni AS dni, 
                :apellido_paterno AS apellidopaterno, 
                :apellido_materno AS apellidomaterno, 
                :nombres AS nombres, 
                :digito_verificador AS digitoverificador, 
                :status AS status, 
                :error AS error
            FROM dual
        ) src
        ON (dd.dni = src.dni)
        WHEN MATCHED THEN
            UPDATE SET 
                dd.apellidopaterno = src.apellidopaterno,
                dd.apellidomaterno = src.apellidomaterno,
                dd.nombres = src.nombres,
                dd.digitoverificador = src.digitoverificador,
                dd.status = src.status,
                dd.error = src.error
        WHEN NOT MATCHED THEN
            INSERT (dni, apellidopaterno, apellidomaterno, nombres, digitoverificador, status, error)
            VALUES (src.dni, src.apellidopaterno, src.apellidomaterno, src.nombres, src.digitoverificador, src.status, src.error)
        """

        cursor.execute(merge_sql, data)

        connection.commit()
        cursor.close()
        print("Datos insertados correctamente en la tabla.")
    except cx_Oracle.Error as error:
        print('Error al insertar datos en la tabla:', error)

def fetch_dni_from_api(dni):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    payload = {'dni': dni}

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            data = result['data']
            return {
                'dni': data['numero'],
                'apellido_paterno': data['apellido_paterno'],
                'apellido_materno': data['apellido_materno'],
                'nombres': data['nombres'],
                'digito_verificador': data['codigo_verificacion'],
                'status': 1,
                'error': None
            }
    return None
