import csv
import re
import time
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def obtener_datos():
    url = url_entry.get()
    if not url:
        result_label.config(text="Por favor, ingrese una URL válida.")
        return
    
    # Abrir el navegador y cargar la página
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    time.sleep(10)  # Espera para resolver manualmente el captcha

    # Extraer el identificador de la URL utilizando expresiones regulares
    match = re.search(r'codGen=([a-zA-Z0-9-]+)', url)
    if match:
        identificador = match.group(1)
        csv_file = f"{identificador}.csv"  # Nombre del archivo CSV basado en el identificador
    else:
        result_label.config(text="No se pudo encontrar el identificador en la URL.")
        driver.quit()
        return

    # Encuentra todos los elementos con la clase 'form-group row'
    form_group_elements = driver.find_elements(By.CLASS_NAME, 'form-group.row')

    # Define una lista para almacenar los campos y sus valores
    rows = []

    # Itera sobre cada elemento de 'form-group row' para extraer el texto de las etiquetas <label>
    for form_group in form_group_elements:
        labels = form_group.find_elements(By.TAG_NAME, 'label')
        if len(labels) == 2:  # Solo procesa los grupos que tienen dos etiquetas <label>
            campo = labels[0].text.strip(':')
            valor = labels[1].text
            rows.append([campo, valor])

    # Guarda los campos y sus valores en un archivo CSV con el nombre basado en el identificador
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Campo', 'Valor'])  # Escribe el encabezado
        writer.writerows(rows)  # Escribe los datos

    result_label.config(text=f"Los datos se han guardado en {csv_file}")

    # Cierra el navegador después de terminar
    driver.quit()

def abrir_csv():
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filename:
        with open(filename, 'r') as file:
            # Aquí puedes realizar alguna operación con el archivo CSV si lo necesitas
            pass

# Crear la ventana principal
root = tk.Tk()
root.title("Obtener Datos de URL")

# Crear y posicionar los elementos en la ventana
url_label = tk.Label(root, text="URL:")
url_label.grid(row=0, column=0, padx=5, pady=5)

url_entry = tk.Entry(root, width=40)
url_entry.grid(row=0, column=1, padx=5, pady=5)

obtener_button = tk.Button(root, text="Obtener", command=obtener_datos)
obtener_button.grid(row=0, column=2, padx=5, pady=5)

result_label = tk.Label(root, text="", wraplength=400)
result_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

abrir_csv_button = tk.Button(root, text="Abrir CSV", command=abrir_csv)
abrir_csv_button.grid(row=2, column=0, padx=5, pady=5)

cancelar_button = tk.Button(root, text="Cancelar", command=root.quit)
cancelar_button.grid(row=2, column=2, padx=5, pady=5)

# Ejecutar el bucle de la interfaz gráfica
root.mainloop()
