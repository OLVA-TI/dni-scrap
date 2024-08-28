import cx_Oracle
from scraper import fetch_dni_from_api, insert_into_table_dni
from database import get_database_connection, pool

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
            data = fetch_dni_from_api(dni)
            if data:
                insert_into_table_dni(connection, data)
                responseData = {
                    'apellidoMaterno': data['apellido_materno'],
                    'apellidoPaterno': data['apellido_paterno'],
                    'digitoVerificador': data['digito_verificador'],
                    'dni': data['dni'],
                    'nombres': data['nombres']
                }
                response = {'data': responseData, 'message': 'Información de DNI obtenida de la API externa.', 'success': True}
            else:
                response = {'message': f'No se encontraron datos para el DNI especificado {dni}.', 'success': False}
        
        pool.release(connection)
    except cx_Oracle.Error as error:
        response = {'message': 'Error al consultar la base de datos: ' + str(error), 'success': False}


    return response
