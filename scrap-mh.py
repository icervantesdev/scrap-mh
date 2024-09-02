import pandas as pd
import time
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry  # Importa el DateEntry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def obtener_datos(fecha, codigo_generacion):
    url = "https://admin.factura.gob.sv/consultaPublica?ambiente=01"
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("detach", True)
    
    # Usa el chromedriver del PATH del sistema
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Abriendo la URL...")
        driver.get(url)

        print("Esperando que los campos de entrada estén disponibles...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='fechaEmi']"))
        )

        fecha_input = driver.find_element(By.XPATH, "//input[@formcontrolname='fechaEmi']")
        fecha_input.send_keys(fecha)
        print(f"Fecha de generación ingresada: {fecha}")

        codigo_input = driver.find_element(By.XPATH, "//input[@formcontrolname='codigoGeneracion']")
        codigo_input.send_keys(codigo_generacion)
        print(f"Código de generación ingresado: {codigo_generacion}")

        buscar_button = driver.find_element(By.XPATH, "//button[contains(text(),'Realizar Búsqueda')]")
        buscar_button.click()
        print("Botón de búsqueda presionado.")

        time.sleep(10)  # Esperar 10 segundos

        print("Esperando que los resultados se carguen...")
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='card-body']"))
        )

        print("Resultados de la búsqueda encontrados.")

        # Encuentra los elementos que contienen los resultados de la búsqueda
        result_rows = driver.find_elements(By.XPATH, "//div[@class='form-group row']")
        
        if not result_rows:
            print("No se encontraron datos en la búsqueda.")
            messagebox.showinfo("Información", "No se encontraron datos en la búsqueda.")
            return

        data = []

        for result_row in result_rows:
            try:
                label_elements = result_row.find_elements(By.TAG_NAME, 'label')
                if len(label_elements) == 2:
                    campo = label_elements[0].text.strip(':')
                    valor = label_elements[1].text
                    data.append([campo, valor])
                    print(f"Campo: {campo} - Valor: {valor}")
                else:
                    print("No se encontraron dos etiquetas <label> en la fila.")
            except Exception as e:
                print(f"Error al procesar una fila de resultados: {str(e)}")

        # Convertir los datos a un DataFrame de pandas
        df = pd.DataFrame(data, columns=['Campo', 'Valor'])

        # Guardar el DataFrame en un archivo de Excel (sobrescribe si existe)
        excel_file = f"{codigo_generacion}.xlsx"
        df.to_excel(excel_file, index=False, engine='openpyxl')

        print(f"Los datos se han guardado en {excel_file}")
        messagebox.showinfo("Éxito", f"Los datos se han guardado en {excel_file}")

    except Exception as e:
        print(f"Error general: {str(e)}")
        messagebox.showerror("Error", f"Error general: {str(e)}")
    
    finally:
        driver.quit()
        print("Navegador cerrado.")

def obtener_datos_gui():
    fecha = entry_fecha.get_date()  # Obtiene la fecha del DateEntry
    codigo_generacion = entry_codigo.get()
    if not fecha or not codigo_generacion:
        messagebox.showwarning("Advertencia", "Por favor, ingrese ambos campos.")
        return
    obtener_datos(fecha.strftime("%m/%d/%Y"), codigo_generacion)  # Formatea la fecha

# Crear la ventana principal
root = tk.Tk()
root.title("Obtener Datos")
root.geometry("575x200")  # Aumenta el tamaño de la ventana
root.resizable(False, False)

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
label_fecha = ttk.Label(main_frame, text="Fecha de generación (MM/DD/YYYY):")
label_fecha.grid(row=0, column=0, padx=5, pady=10, sticky="w")

entry_fecha = DateEntry(main_frame, width=37, background='darkblue', foreground='white', borderwidth=2, date_pattern='mm/dd/yyyy')
entry_fecha.grid(row=0, column=1, padx=5, pady=10)

label_codigo = ttk.Label(main_frame, text="Código de generación (UUID):")
label_codigo.grid(row=1, column=0, padx=5, pady=10, sticky="w")

entry_codigo = ttk.Entry(main_frame, width=37)
entry_codigo.grid(row=1, column=1, padx=5, pady=10)

btn_obtener = ttk.Button(main_frame, text="Obtener", command=obtener_datos_gui)
btn_obtener.grid(row=2, column=0, columnspan=2, pady=10)

btn_cerrar = ttk.Button(main_frame, text="Cerrar", command=root.quit)
btn_cerrar.grid(row=3, column=0, columnspan=2, pady=5)

# Ejecutar la aplicación
root.mainloop()
