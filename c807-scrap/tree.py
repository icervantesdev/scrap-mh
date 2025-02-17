import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


# # SELECT ord.sku, bx.trackOrder, bx.type_id, bx.created_at, ord.order_state_id
# # FROM orders as ord
# # INNER JOIN boxfuls as bx ON ord.id = bx.type_id
# # WHERE bx.created_at like '%2024-08%'
# #  	and bx.courierName like '%c807%';

# Función para guardar datos en CSV
def save_to_csv(csv_filename, url, title, description, date):
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([url, title, description, date])

# Función para obtener el primer paso para una URL
def get_first_step(url):
    options = Options()
    options.add_argument("--headless")  # Ejecutar Chrome en modo headless
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        # Encontrar todos los elementos con clase 'step__content'
        step_elements = driver.find_elements(By.CLASS_NAME, 'step__content')

        if step_elements:
            # Obtener el primer elemento
            first_step = step_elements[0]

            # Obtener el título
            title_element = first_step.find_element(By.CLASS_NAME, 'step__title')
            title = title_element.text.strip()

            # Obtener la descripción si existe
            try:
                description_element = first_step.find_element(By.CLASS_NAME, 'step__description')
                description = description_element.text.strip()
            except:
                description = ''  # Si no se encuentra step__description, dejar en blanco

            # Obtener la fecha
            date_element = first_step.find_element(By.CLASS_NAME, 'step__content-date')
            date_str = date_element.text.strip()
            date = datetime.strptime(date_str, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')

            # Guardar en CSV
            save_to_csv('results.csv', url, title, description, date)
        else:
            print(f"No se encontraron pasos para la URL: {url}")

    except Exception as e:
        print(f"Error al procesar la URL {url}: {str(e)}")

    finally:
        driver.quit()

# Leer las URLs desde el archivo CSV
csv_filename = 'urls.csv'

# Leer las URLs y procesarlas con una barra de progreso
with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    urls = [row[0].strip() for row in reader]

# Usar tqdm para mostrar la barra de progreso
for url in tqdm(urls, desc="Procesando URLs", ncols=100):
    get_first_step(url)
