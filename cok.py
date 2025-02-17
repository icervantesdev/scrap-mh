import json

# Ruta al archivo JSON con las cookies exportadas
json_cookies_path = input("Ingresa la ruta del archivo JSON con las cookies: ").strip()

# Ruta de salida para el archivo cookies.txt
txt_cookies_path = input("Ingresa la ruta para guardar el archivo cookies.txt: ").strip()

try:
    # Leer el archivo JSON
    with open(json_cookies_path, 'r', encoding='utf-8') as json_file:
        cookies = json.load(json_file)

    # Convertir a formato cookies.txt
    with open(txt_cookies_path, 'w', encoding='utf-8') as txt_file:
        for cookie in cookies:
            domain = cookie.get('domain', '')
            path = cookie.get('path', '/')
            secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
            expiry = cookie.get('expirationDate', '0')  # Algunos cookies pueden no tener expiración
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            txt_file.write(f"{domain}\tTRUE\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")

    print(f"Archivo cookies.txt creado en: {txt_cookies_path}")

except Exception as e:
    print(f"Error al convertir las cookies: {e}")
