import requests
import random


# Configuración
API_URL = "https://api.quantumnumbers.anu.edu.au"
API_KEY = "Xt5SPc3fXk1Y5txTHodB283HqUfWRcM2awOGLFLq"
request_length = 50  # Solicitar más números para asegurar que haya suficientes en el rango
desired_count = 5  # Cantidad de números que queremos obtener
max_value = 46
min_value = 1

# Solicitar números aleatorios
response = requests.get(
    f"{API_URL}?length={request_length}&type=uint8",
    headers={"x-api-key": API_KEY}
)

# Verifica si la respuesta fue exitosa
if response.status_code == 200:
    json_response = response.json()
    
    # Inspeccionar la respuesta para extraer los datos correctos
    if isinstance(json_response, dict) and "data" in json_response:
        all_numbers = json_response["data"]
    else:
        all_numbers = json_response  # Si es una lista directamente

    print(json_response)

    # Convertir a enteros y filtrar en el rango deseado
    filtered_numbers = [int(num) for num in all_numbers if min_value <= int(num) <= max_value]

    # Asegurarse de obtener exactamente 5 números
    if len(filtered_numbers) < desired_count:
        print("No se obtuvieron suficientes números en el rango. Intenta solicitar más.")
    else:
        selected_numbers = random.sample(filtered_numbers, desired_count)
        print(f"5 números seleccionados entre {min_value} y {max_value}: {selected_numbers}")
else:
    print(f"Error en la solicitud: {response.status_code} - {response.text}")