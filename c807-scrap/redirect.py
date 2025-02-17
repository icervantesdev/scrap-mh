import csv
import requests
from tqdm import tqdm

# Función para obtener la URL de redirección
def get_redirection_url(url_suffix):
    base_url = 'https://app.c807.com/guia.php/seguimiento/'
    url = base_url + url_suffix

    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except requests.RequestException as e:
        print(f"Error al obtener la redirección para {url_suffix}: {str(e)}")
        return None

# Archivo de entrada y salida
input_csv = 'collect.csv'
output_csv = 'redirections.csv'

# Abrir archivo de entrada
with open(input_csv, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Saltar encabezado si lo tiene
    urls = [row[0] for row in reader]

# Realizar las peticiones y guardar los resultados en el archivo de salida
with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Original_URL', 'Redirection_URL'])

    # Usar tqdm para agregar una barra de progreso
    for url_suffix in tqdm(urls, desc="Procesando URLs", ncols=100):
        redirection_url = get_redirection_url(url_suffix)
        if redirection_url:
            writer.writerow([url_suffix, redirection_url])
        else:
            writer.writerow([url_suffix, 'Error al obtener la redirección'])

print(f"Se han guardado las redirecciones en {output_csv}")
