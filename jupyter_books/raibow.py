from tkinter import Tk, Label, Entry, Button, StringVar, IntVar, Checkbutton, OptionMenu
from PIL import Image, ImageDraw, ImageFont
import random
import string

# Función para generar una tarjeta de coordenadas
def generate_card():
    seed_text = seed_var.get()
    use_special_chars = special_chars_var.get()
    add_pin_rows = pin_rows_var.get()
    columns_mode = columns_var.get()
    rows_mode = rows_var.get()
    size_mode = size_var.get()
    color_mode = color_var.get()
    
    # Colores pastel y letras mayúsculas para etiquetas
    COLORS = ["#FFDDDD", "#FFF4CC", "#FFFFCC", "#CCFFCC", "#CCFFFF", "#CCCCFF", "#E6CCFF"]
    LETTERS = list(string.ascii_uppercase[:22])
    ROWS = 7
    COLS = 22

    def generate_random_characters():
        chars = string.ascii_letters + string.digits
        if use_special_chars:
            chars += "!@#$%^&*"
        return random.choice(chars)

    # Crear imagen
    width, height = 800, 400
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    draw.text((20, 30), seed_text, fill="black", font=font)

    cell_width = 30
    cell_height = 30
    x_offset = 60
    y_offset = 80

    for i, letter in enumerate(LETTERS):
        draw.text((x_offset + i * cell_width, y_offset - 30), letter, fill="black", font=font)

    for row in range(ROWS):
        for col in range(COLS):
            x = x_offset + col * cell_width
            y = y_offset + row * cell_height
            draw.rectangle([x, y, x + cell_width, y + cell_height], fill=COLORS[row])
            char = generate_random_characters()
            draw.text((x + 10, y + 5), char, fill="black", font=font)

        draw.text((x_offset - 30, y_offset + row * cell_height + 5), chr(65 + row), fill="black", font=font)

    image.save("tarjeta_rainbow.png")

# Configuración de la interfaz gráfica con tkinter
root = Tk()
root.title("Generador de Tarjetas Rainbow")

# Paso 1: La semilla
Label(root, text="Paso 1: La semilla").grid(row=0, column=0, columnspan=2, sticky="w")
seed_var = StringVar()
Entry(root, textvariable=seed_var, width=30).grid(row=1, column=0, columnspan=2, sticky="w")

# Paso 2: Etiquetas, tamaño y colores
Label(root, text="Paso 2: Etiquetas, tamaño y colores").grid(row=2, column=0, columnspan=2, sticky="w")

columns_var = StringVar(value="Letras Mayúsculas")
rows_var = StringVar(value="Letras Mayúsculas")
size_var = StringVar(value="ISO/IEC 7810:ID1 (tarjeta de crédito)")
color_var = StringVar(value="Arcoiris")

Label(root, text="Columnas:").grid(row=3, column=0, sticky="e")
OptionMenu(root, columns_var,
           "Letras Mayúsculas",
           "Dígitos decimales",
           "Números impares",
           "Números pares",
           "Vocales",
           "Consonantes",
           "Modo Pi",
           "Hexadecimal 1-byte",
           "Hexadecimal 2-bytes",
           "Mayúsculas con ñ",
           "Sin etiqueta de columnas").grid(row=3, column=1, sticky="w")

Label(root, text="Filas:").grid(row=4, column=0, sticky="e")
OptionMenu(root, rows_var,
           "Letras Mayúsculas",
           "Vocales",
           "Dígitos decimales",
           "Números impares",
           "Números pares",
           "Números romanos",
           "Contador binario",
           "permisos chmod de Unix",
           "Modo Pi",
           "Secuencia de Primos",
           "Secuencia de cuadrados",
           "Potencias de 2",
           "Secuencia de Fibonacci",
           "Los números de Lost",
           "Sin etiqueta de filas").grid(row=4, column=1, sticky="w")

Label(root, text="Tamaño:").grid(row=5, column=0, sticky="e")
OptionMenu(root, size_var,
           "ISO/IEC 7810:ID1 (tarjeta de crédito)",
           "ISO/IEC 7810:ID2 (A7, ID Alemania)",
           "ISO/IEC 7810:ID3 (Pasaporte/Visa)").grid(row=5, column=1, sticky="w")

Label(root, text="Colores:").grid(row=6, column=0, sticky="e")
OptionMenu(root, color_var,
           "Arcoiris",
           "Paleta al azar",
           "Paleta alternativa",
           "Barras grises y blancas",
           "Sin colores").grid(row=6, column=1, sticky="w")

# Paso 3: Detalles finales
Label(root, text="Paso 3: Detalles finales").grid(row=7, column=0, columnspan=2, sticky="w")
pin_rows_var = IntVar()
Checkbutton(root, text="Las 4 últimas filas numéricas (para PINs)", variable=pin_rows_var).grid(row=8, column=0, columnspan=2, sticky="w")

special_chars_var = IntVar()
Checkbutton(root, text="Usar también símbolos especiales", variable=special_chars_var).grid(row=9, column=0, columnspan=2, sticky="w")

# Botón para generar la tarjeta
Button(root, text="Generar", command=generate_card).grid(row=10, column=0, columnspan=2)

root.mainloop()
