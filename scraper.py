from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def scrape_dni_info(dni):
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

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    result = {}

    try:
        driver.get('https://eldni.com/pe/buscar-datos-por-dni')
        dni_input = driver.find_element(By.ID, 'dni')
        dni_input.send_keys(dni)
        dni_input.submit()
        driver.implicitly_wait(5)
        try:
            nombres = driver.find_element(By.ID, 'nombres').get_attribute('value')
            apellidop = driver.find_element(By.ID, 'apellidop').get_attribute('value')
            apellidom = driver.find_element(By.ID, 'apellidom').get_attribute('value')
            digito_verificador = get_verify_code(dni)

            result['message'] = "Información de dni obtenida!"
            result['success'] = True
            result['data'] = {
                'dni': dni,
                'apellidoPaterno': apellidop,
                'apellidoMaterno': apellidom,
                'nombres': nombres,
                'digitoVerificador': digito_verificador
            }
        except:
            result['message'] = "No se ha encontrado el DNI"
            result['success'] = False

    except Exception as e:
        result['message'] = str(e)
        result['success'] = False
    
    finally:
        driver.quit()

    return result


def get_verify_code(dni):
    sum = 5
    hash = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    for i in range(2, 10):
        sum += (int(dni[i - 2]) * hash[i])
    int_num = int(sum / 11)
    digit = 11 - (sum - int_num * 11)
    return digit - 10 if digit > 9 else digit