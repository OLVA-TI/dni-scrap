from flask import jsonify
import cx_Oracle
import os
from dotenv import load_dotenv
from scraper import scrape_dni_info

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_USERSCHEMA = os.getenv("DB_USERSCHEMA")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Crear el pool de conexiones
pool = cx_Oracle.SessionPool(
    user=DB_USERNAME,
    password=DB_PASSWORD,
    dsn=cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_DATABASE),
    min=2,
    max=15,
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

def get_dni_info(dni):
    try:
        connection = get_database_connection()
        if not connection:
            return {'message': 'No se pudo conectar a la base de datos.', 'success': False}
        
        cursor = connection.cursor()
        query = "SELECT apellidoMaterno, apellidoPaterno, digitoVerificador, dni, nombres FROM DATOS_DNI WHERE dni = :dni AND status = 1"
        cursor.execute(query, {'dni': dni})
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            data = {
                'apellidoMaterno': result[0],
                'apellidoPaterno': result[1],
                'digitoVerificador': result[2],
                'dni': result[3],
                'nombres': result[4]
            }
            response = {'data': data, 'message': 'Información de DNI obtenida de la base de datos.', 'success': True}
        else:
            scrape_result = scrape_dni_info(dni)
            if scrape_result['success']:
                cursor = connection.cursor()
                cursor.execute(query, {'dni': dni})
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    data = {
                        'apellidoMaterno': result[0],
                        'apellidoPaterno': result[1],
                        'digitoVerificador': result[2],
                        'dni': result[3],
                        'nombres': result[4]
                    }
                    response = {'data': data, 'message': 'Información de DNI obtenida después del scraping.', 'success': True}
                else:
                    response = {'message': f'No se encontraron datos para el DNI especificado después del scraping {dni}.', 'success': False}
            else:
                response = {'message': f'No se encontraron datos para el DNI especificado {dni}.', 'success': False}
        
        pool.release(connection)
    except cx_Oracle.Error as error:
        response = {'message': 'Error al consultar la base de datos: ' + str(error), 'success': False}

    return response
