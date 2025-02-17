import os
import requests
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

# Configuración
API_KEY = "TU_API_KEY_DE_LASTFM"
MUSIC_FOLDER = "D:\music\Melodías del Ocaso Perdido"

def obtener_portada(artista, titulo):
    """
    Obtiene la URL de la portada del álbum desde la API de Last.fm.
    """
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getInfo",
        "api_key": "ac68033e05ad5b68459f1b701d7ddb3a",
        "artist": artista,
        "track": titulo,
        "format": "json"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "track" in data and "album" in data["track"]:
            album = data["track"]["album"]
            if "image" in album and len(album["image"]) > 0:
                return album["image"][-1]["#text"]  # URL de la imagen de mayor tamaño
    return None

def agregar_portada_a_mp3(mp3_path, portada_url):
    """
    Descarga y agrega la portada al archivo MP3.
    """
    response = requests.get(portada_url)
    if response.status_code == 200:
        audio = MP3(mp3_path, ID3=ID3)
        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',
                type=3,  # Portada frontal
                desc=u'Cover',
                data=response.content
            )
        )
        audio.save()

def procesar_carpeta(carpeta):
    """
    Recorre los archivos MP3 en la carpeta y actualiza sus portadas.
    """
    for root, dirs, files in os.walk(carpeta):
        for file in files:
            if file.endswith(".mp3"):
                mp3_path = os.path.join(root, file)
                try:
                    # Leer metadatos
                    audio = EasyID3(mp3_path)
                    artista = audio.get("artist", ["Desconocido"])[0]
                    titulo = audio.get("title", ["Desconocido"])[0]
                    
                    # Obtener portada
                    print(f"Procesando: {titulo} - {artista}")
                    portada_url = obtener_portada(artista, titulo)
                    if portada_url:
                        print(f"Descargando portada para: {titulo}")
                        agregar_portada_a_mp3(mp3_path, portada_url)
                    else:
                        print(f"No se encontró portada para: {titulo}")
                except Exception as e:
                    print(f"Error procesando {file}: {e}")

# Ejecutar el script
procesar_carpeta(MUSIC_FOLDER)
