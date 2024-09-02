import csv
import time
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def obtener_datos():
    fecha = fecha_entry.get()
    codigo_generacion = codigo_entry.get()
    
    if not fecha or not codigo_generacion:
        result_label.config(text="Por favor, ingrese la fecha y el código de generación.")
        return
    
    # Configuración del navegador
    url = "https://admin.factura.gob.sv/consultaPublica?ambiente=01"
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    try:
        # Esperar hasta que el campo de fecha esté presente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='fechaEmi']"))
        )

        # Rellenar la fecha
        fecha_input = driver.find_element(By.XPATH, "//input[@formcontrolname='fechaEmi']")
        fecha_input.send_keys(fecha)

        # Rellenar el código de generación
        codigo_input = driver.find_element(By.XPATH, "//input[@formcontrolname='codigoGeneracion']")
        codigo_input.send_keys(codigo_generacion)

        # Hacer clic en el botón "Realizar Búsqueda"
        buscar_button = driver.find_element(By.XPATH, "//button[contains(text(),'Realizar Búsqueda')]")
        buscar_button.click()

        # Esperar hasta que los resultados estén presentes
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Resultado de consulta')]"))
        )

        # Encuentra los elementos que contienen los resultados de la búsqueda
        result_rows = driver.find_elements(By.CLASS_NAME, 'form-group.row')

        # Define una lista para almacenar los campos y sus valores
        rows = []

        # Itera sobre cada elemento para extraer los datos
        for result_row in result_rows:
            label_elements = result_row.find_elements(By.TAG_NAME, 'label')
            if len(label_elements) == 2:  # Solo procesa los grupos que tienen dos etiquetas <label>
                campo = label_elements[0].text.strip(':')
                valor = label_elements[1].text
                rows.append([campo, valor])

        # Guarda los campos y sus valores en un archivo CSV con el nombre basado en el código de generación
        csv_file = f"{codigo_generacion}.csv"
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Campo', 'Valor'])  # Escribe el encabezado
            writer.writerows(rows)  # Escribe los datos

        result_label.config(text=f"Los datos se han guardado en {csv_file}")

    except Exception as e:
        result_label.config(text=f"Error: {str(e)}")
    
    finally:
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
root.title("Consulta Pública DTE")

# Crear y posicionar los elementos en la ventana
fecha_label = tk.Label(root, text="Fecha de Generación (MM/DD/YYYY):")
fecha_label.grid(row=0, column=0, padx=5, pady=5)

fecha_entry = tk.Entry(root, width=20)
fecha_entry.grid(row=0, column=1, padx=5, pady=5)

codigo_label = tk.Label(root, text="Código de Generación (UUID):")
codigo_label.grid(row=1, column=0, padx=5, pady=5)

codigo_entry = tk.Entry(root, width=40)
codigo_entry.grid(row=1, column=1, padx=5, pady=5)

obtener_button = tk.Button(root, text="Obtener Datos", command=obtener_datos)
obtener_button.grid(row=2, column=0, padx=5, pady=5)

result_label = tk.Label(root, text="", wraplength=400)
result_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

abrir_csv_button = tk.Button(root, text="Abrir CSV", command=abrir_csv)
abrir_csv_button.grid(row=4, column=0, padx=5, pady=5)

cancelar_button = tk.Button(root, text="Cancelar", command=root.quit)
cancelar_button.grid(row=4, column=2, padx=5, pady=5)

# Ejecutar el bucle de la interfaz gráfica
root.mainloop()
