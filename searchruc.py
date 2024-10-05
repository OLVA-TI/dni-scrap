import cx_Oracle
from scraper import fetch_ruc_from_api, insert_into_table_ruc
from database import get_database_connection, pool

def get_ruc_info(ruc, _source):
    try:
        connection = get_database_connection()
        if not connection:
            return {'message': 'No se pudo conectar a la base de datos.', 'success': False}
        
        cursor = connection.cursor()
        query = """
        SELECT RUC, RAZONSOCIAL, ESTADOCONTRIBUYENTE, CONDICIONDOMICILIO, UBIGEO
        FROM CONTRIBUYENTE
        WHERE RUC = :ruc
        """
        cursor.execute(query, {'ruc': ruc})
        result = cursor.fetchone()
        cursor.close()

        if result and result[2] == 'ACTIVO' and result[3] == 'HABIDO':
            # Verificar si ubigeo es None antes de trabajar con él
            ubigeo_sunat = result[4]
            ubigeo = [ubigeo_sunat[:2], ubigeo_sunat[:4], ubigeo_sunat] if ubigeo_sunat else []

            responseData = {
                'ruc': result[0],
                'nombre_o_razon_social': result[1],
                'estado': result[2],
                'condicion': result[3],
                'ubigeo_sunat': ubigeo_sunat or "",
                'ubigeo': ubigeo,
            }
            response = {'data': responseData, 'message': 'Información de RUC obtenida de la base de datos.', 'success': True}
        else:
            # Si no existe o el estado/condición no es el esperado, consultar la API
            data = fetch_ruc_from_api(ruc, _source)
            if data:
                insert_into_table_ruc(connection, data)
                ubigeo_sunat = data['ubigeo_sunat']
                ubigeo = [ubigeo_sunat[:2], ubigeo_sunat[:4], ubigeo_sunat] if ubigeo_sunat else []

                responseData = {
                    'ruc': data['ruc'],
                    'nombre_o_razon_social': data['nombre_o_razon_social'],
                    'estado': data['estado'],
                    'condicion': data['condicion'],
                    'ubigeo_sunat': ubigeo_sunat,
                    'ubigeo': ubigeo,
                }
                message = 'Información de RUC obtenida de la API externa.'
                if result:
                    message += ' Validación de condición y estado realizada.'
                response = {'data': responseData, 'message': message, 'success': True}
            else:
                response = {'message': f'No se encontraron datos para el RUC especificado {ruc}.', 'success': False}
        
        pool.release(connection)
    except cx_Oracle.Error as error:
        response = {'message': 'Error al consultar la base de datos: ' + str(error), 'success': False}

    return response
