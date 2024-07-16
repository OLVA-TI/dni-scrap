import os
import cx_Oracle
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time
from selenium.common.exceptions import NoSuchElementException

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Variables de entorno para la base de datos
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_USERSCHEMA = os.getenv("DB_USERSCHEMA")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Variables globales
browser_instance = None
browser_lock = threading.Lock()

def init_browser():
    global browser_instance
    if browser_instance is None:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        # options.add_argument('--start-maximized')  # Iniciar Chrome maximizado
        options.add_argument('--page-load-strategy=eager')

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
        }
        options.add_experimental_option("prefs", prefs)

        try:
            browser_instance = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        except Exception as e:
            print(f"Error initializing browser: {e}")
            browser_instance = None

def close_browser():
    global browser_instance
    if browser_instance:
        browser_instance.quit()
        browser_instance = None

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

def scrape_dni_info(dni):
    global browser_instance, browser_lock
    result = {}
    print(browser_instance)

    with browser_lock:
        if browser_instance is None:
            init_browser()
        
        if browser_instance is None:
            result['message'] = 'Browser initialization failed.'
            result['success'] = False
            return result

        def attempt_scrape():
            browser_instance.execute_script("window.open('');")
            browser_instance.switch_to.window(browser_instance.window_handles[-1])
            browser_instance.get('https://eldni.com/pe/buscar-datos-por-dni')

            dni_input = browser_instance.find_element(By.ID, 'dni')
            dni_input.send_keys(dni)
            dni_input.submit()

            nombres = browser_instance.find_element(By.ID, 'nombres').get_attribute('value')
            apellidop = browser_instance.find_element(By.ID, 'apellidop').get_attribute('value')
            apellidom = browser_instance.find_element(By.ID, 'apellidom').get_attribute('value')
            digito_verificador = get_verify_code(dni)

            return {
                'dni': dni,
                'apellido_paterno': apellidop,
                'apellido_materno': apellidom,
                'nombres': nombres,
                'digito_verificador': digito_verificador,
                'status': 1,
                'error': None
            }

        try:
            try:
                data = attempt_scrape()

                connection = connect_to_oracle()
                if connection:
                    insert_into_table(connection, data)
                    connection.close()
                    result['message'] = "Información de DNI obtenida y guardada en la base de datos."
                    result['success'] = True
                else:
                    result['message'] = "No se pudo conectar a la base de datos."
                    result['success'] = False

            except NoSuchElementException:
                try:
                    time.sleep(3) # Esperar un poco antes de reintentar
                    data = attempt_scrape()

                    connection = connect_to_oracle()
                    if connection:
                        insert_into_table(connection, data)
                        connection.close()
                        result['message'] = "Información de DNI obtenida y guardada en la base de datos."
                        result['success'] = True
                    else:
                        result['message'] = "No se pudo conectar a la base de datos."
                        result['success'] = False

                except NoSuchElementException as e:
                    data = {
                        'dni': dni,
                        'apellido_paterno': None,
                        'apellido_materno': None,
                        'nombres': None,
                        'digito_verificador': None,
                        'status': 0,
                        'error': str(e)
                    }
                    connection = connect_to_oracle()
                    if connection:
                        insert_into_table(connection, data)
                        connection.close()
                    result['message'] = "No se ha encontrado el DNI o Cloudflare bloqueó el acceso."
                    result['success'] = False
                finally:
                    browser_instance.close()
                    browser_instance.switch_to.window(browser_instance.window_handles[0])
                        

        except Exception as e:
            result['message'] = str(e)
            result['success'] = False
        finally:
            browser_instance.close()
            browser_instance.switch_to.window(browser_instance.window_handles[0])

    return result

def get_verify_code(dni):
    sum = 5
    hash = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    for i in range(2, 10):
        sum += (int(dni[i - 2]) * hash[i])
    int_num = int(sum / 11)
    digit = 11 - (sum - int_num * 11)
    return digit - 10 if digit > 9 else digit
