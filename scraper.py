import os
import requests
import cx_Oracle
from dotenv import load_dotenv

load_dotenv(override=True)
API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")

def insert_into_table_dni(connection, data):
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

def insert_into_table_ruc(connection, data):
    try:
        cursor = connection.cursor()

        variables = {
            'ruc': data['ruc'],
            'nombre_o_razon_social': data['nombre_o_razon_social'],
            'estado': data['estado'],
            'condicion': data['condicion'],
            'ubigeo': data['ubigeo_sunat'],
        }
        
        merge_sql = """
        MERGE INTO CONTRIBUYENTE c
        USING (
            SELECT :ruc AS ruc, 
                :nombre_o_razon_social AS razonsocial, 
                :estado AS estadocontribuyente, 
                :condicion AS condiciondomicilio,
                :ubigeo AS ubigeo
            FROM dual
        ) src
        ON (c.ruc = src.ruc)
        WHEN MATCHED THEN
            UPDATE SET 
                c.razonsocial = src.razonsocial,
                c.estadocontribuyente = src.estadocontribuyente,
                c.condiciondomicilio = src.condiciondomicilio,
                c.ubigeo = src.ubigeo
        WHEN NOT MATCHED THEN
            INSERT (ruc, razonsocial, estadocontribuyente, condiciondomicilio, ubigeo)
            VALUES (src.ruc, src.razonsocial, src.estadocontribuyente, src.condiciondomicilio, src.ubigeo)
        """

        cursor.execute(merge_sql, variables)

        connection.commit()
        cursor.close()
        print("Datos insertados o actualizados correctamente en la tabla CONTRIBUYENTE.")
    except cx_Oracle.Error as error:
        print('Error al insertar datos en la tabla CONTRIBUYENTE:', error)

def fetch_dni_from_api(dni):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }

    response = requests.post(f'{API_URL}/dni?dni={dni}', json={}, headers=headers)

    print(response,f'{API_URL}/dni?dni={dni}')
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

def fetch_ruc_from_api(ruc):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }

    response = requests.post(f'{API_URL}/ruc?ruc={ruc}', json={}, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            data = result['data']
            return {
                'ruc': data['ruc'],
                'nombre_o_razon_social': data['nombre_o_razon_social'],
                'estado': data['estado'],
                'condicion': data['condicion'],
                'direccion': data['direccion'],
                'ubigeo_sunat': data['ubigeo_sunat'],
                'ubigeo': data['ubigeo_sunat'],
                'es_agente_de_retencion': data.get('es_agente_de_retencion', 'NO'),
                'es_buen_contribuyente': data.get('es_buen_contribuyente', 'NO'),
                'departamento': data.get('departamento'),
                'provincia': data.get('provincia'),
                'distrito': data.get('distrito')
            }
    return None
