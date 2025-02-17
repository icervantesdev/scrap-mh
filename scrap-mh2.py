import json
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def obtener_datos(fecha, codigo_generacion):
    url = "https://admin.factura.gob.sv/consultaPublica?ambiente=01"
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo oculto
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)

        # Esperar a que los campos estén presentes y listos para la entrada
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='fechaEmi']"))
        )

        fecha_input = driver.find_element(By.XPATH, "//input[@formcontrolname='fechaEmi']")
        fecha_input.clear()
        fecha_input.send_keys(fecha)
        print(f"Fecha ingresada: {fecha}")  # Depuración

        codigo_input = driver.find_element(By.XPATH, "//input[@formcontrolname='codigoGeneracion']")
        codigo_input.clear()
        codigo_input.send_keys(codigo_generacion)
        print(f"Código de generación ingresado: {codigo_generacion}")  # Depuración

        buscar_button = driver.find_element(By.XPATH, "//button[contains(text(),'Realizar Búsqueda')]")
        buscar_button.click()

        time.sleep(5)  # Esperar un poco antes de verificar el resultado

        # Verificar si se abre la ventana de error (indicando que no es válida)
        try:
            error_message_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="swal2-content"]/div/p[1]/strong'))
            )
            error_message = error_message_element.text
            print(f"Mensaje de error detectado: {error_message}")
            return {"Estado del documento": "NO Transmitido", "Mensaje": error_message}  # Retornar el mensaje de error
        except:
            pass  # Continuar si no se abre la ventana de error

        # Si no se detecta la ventana de error, continuar con la extracción de datos
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='card-body']"))
        )

        result_rows = driver.find_elements(By.XPATH, "//div[@class='form-group row']")

        if not result_rows:
            print(f"No se encontraron resultados para la fecha {fecha} y el código {codigo_generacion}.")
            return {"Estado del documento": "NO Transmitido", "Mensaje": "No se encontraron datos."}

        data = {"Estado del documento": "Transmitido"}
        for result_row in result_rows:
            try:
                label_elements = result_row.find_elements(By.TAG_NAME, 'label')
                if len(label_elements) == 2:
                    campo = label_elements[0].text.strip(':')
                    valor = label_elements[1].text
                    data[campo] = valor
            except Exception as e:
                print(f"Error al procesar una fila de resultados: {str(e)}")

        return data  # Retorna el diccionario con los datos extraídos

    except Exception as e:
        print(f"Error general: {str(e)}")
        return {"Estado del documento": "NO Transmitido", "Mensaje": "Error en la extracción de datos."}  # Retorna un mensaje de error general
    
    finally:
        driver.quit()

def procesar_archivo_json(filepath):
    try:
        with open(filepath, 'r') as file:
            datos = json.load(file)
    except Exception as e:
        print(f"Error al leer el archivo JSON: {str(e)}")
        return
    
    resultados = []
    
    for item in datos:
        fecha = item['Fecha']
        codigo_generacion = item['CodigoGeneracion']
        print(f"Procesando fecha: {fecha}, código: {codigo_generacion}")  # Depuración
        resultado = obtener_datos(fecha, codigo_generacion)
        
        if resultado is not None:
            # Agregar código de generación y fecha al resultado
            resultado['Fecha'] = fecha
            resultado['CodigoGeneracion'] = codigo_generacion
            resultados.append(resultado)
        else:
            print(f"No se encontraron datos para {codigo_generacion} en la fecha {fecha}")
    
    if resultados:
        # Obtener la ruta del script actual
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, "resultado_final.json")
        
        # Guardar los resultados en un archivo JSON en la misma carpeta que el script
        with open(output_file, 'w') as file:
            json.dump(resultados, file, indent=4)
        print(f"Todos los datos se han guardado en {output_file}")
    else:
        print("No se generaron datos.")

def seleccionar_archivo():
    try:
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        return filepath
    except Exception as e:
        print(f"Error al seleccionar el archivo: {str(e)}")
        return None

def procesar_datos():
    try:
        if not archivo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un archivo JSON primero.")
            return
        procesar_archivo_json(archivo_seleccionado)
    except Exception as e:
        print(f"Error en el procesamiento de datos: {str(e)}")

# Crear la ventana principal
root = tk.Tk()
root.title("Obtener Datos desde JSON")
root.geometry("500x150")
root.resizable(False, False)

# Variable global para almacenar la ruta del archivo JSON seleccionado
archivo_seleccionado = None

def seleccionar_y_procesar():
    global archivo_seleccionado
    archivo_seleccionado = seleccionar_archivo()
    if archivo_seleccionado:
        label_archivo.config(text=archivo_seleccionado)
    else:
        label_archivo.config(text="Ninguno")

# Estilo de la ventana
style = ttk.Style()
style.configure("TFrame", background="#f2f2f2")
style.configure("TLabel", background="#f2f2f2", font=("Arial", 10))
style.configure("TButton", background="#007bff", foreground="white", font=("Arial", 10))
style.map("TButton", background=[("active", "#0056b3")])

# Crear un marco principal
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill="both", expand=True)

# Crear los widgets
label_instruccion = ttk.Label(main_frame, text="Archivo JSON seleccionado:")
label_instruccion.grid(row=0, column=0, padx=5, pady=10, sticky="w")

label_archivo = ttk.Label(main_frame, text="Ninguno", width=50)
label_archivo.grid(row=0, column=1, padx=5, pady=10, sticky="w")

btn_seleccionar = ttk.Button(main_frame, text="Seleccionar JSON", command=seleccionar_y_procesar)
btn_seleccionar.grid(row=1, column=0, columnspan=2, pady=10)

btn_procesar = ttk.Button(main_frame, text="Procesar", command=procesar_datos)
btn_procesar.grid(row=2, column=0, columnspan=2, pady=10)

btn_cerrar = ttk.Button(main_frame, text="Cerrar", command=root.quit)
btn_cerrar.grid(row=3, column=0, columnspan=2, pady=5)

# Ejecutar la aplicación
root.mainloop()
