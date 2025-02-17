from pytube import Playlist
import yt_dlp
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, APIC
import re
import requests

# Configuración de la API de Last.fm
API_KEY = "ac68033e05ad5b68459f1b701d7ddb3a"

# Funciones auxiliares
def sanitize_filename(name):
    """Sanitiza nombres de archivo para evitar caracteres no permitidos."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def obtener_portada(artista, titulo):
    """Obtiene la URL de la portada del álbum desde la API de Last.fm."""
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getInfo",
        "api_key": API_KEY,
        "artist": artista,
        "track": titulo,
        "format": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "track" in data and "album" in data["track"]:
                album = data["track"]["album"]
                if "image" in album and len(album["image"]) > 0:
                    return album["image"][-1]["#text"]  # URL de mayor tamaño
    except Exception as e:
        print(f"Error al obtener portada: {e}")
    return None

def agregar_portada_a_mp3(mp3_path, portada_url):
    """Descarga y agrega la portada al archivo MP3."""
    try:
        response = requests.get(portada_url, timeout=10)
        if response.status_code == 200:
            audio = MP3(mp3_path, ID3=ID3)
            if not audio.tags:
                audio.add_tags()
            audio.tags.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime='image/jpeg',
                    type=3,  # Portada frontal
                    desc='Cover',
                    data=response.content
                )
            )
            audio.save()
    except Exception as e:
        print(f"Error al agregar portada: {e}")

# Solicitar URL de la lista de reproducción
playlist_url = input("Por favor, ingresa la URL de la lista de reproducción: ")
playlist = Playlist(playlist_url)

# Crear carpeta para guardar los archivos descargados
playlist_folder = sanitize_filename(playlist.title or "Lista_de_reproduccion")
if not os.path.exists(playlist_folder):
    os.makedirs(playlist_folder)

# Confirmar la descarga
definir_confirmacion = input("\n¿Quieres descargar todos los audios en formato MP3 con metadatos? (s/n): ")
if definir_confirmacion.lower() != 's':
    print("Descarga cancelada.")
    exit()

# Configuración de `yt-dlp`
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f'{playlist_folder}/%(title)s.%(ext)s',
    'postprocessors': [
        {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
    ],
    'windowsfilenames': True,  # Evitar problemas con nombres de archivo en Windows
}

# Descargar cada video y agregar metadatos
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for video_url in playlist.video_urls:
        try:
            info = ydl.extract_info(video_url, download=True)  # Extrae y descarga
            safe_title = sanitize_filename(info['title'])
            mp3_file = os.path.join(playlist_folder, f"{safe_title}.mp3")

            if os.path.exists(mp3_file):
                try:
                    audio = MP3(mp3_file, ID3=ID3)
                    if not audio.tags:
                        audio.add_tags()
                    audio.tags.add(TIT2(encoding=3, text=info.get('title', 'Título desconocido')))
                    audio.tags.add(TPE1(encoding=3, text=info.get('uploader', 'Artista desconocido')))
                    audio.tags.add(TALB(encoding=3, text=playlist.title or "Álbum desconocido"))
                    audio.tags.add(TYER(encoding=3, text=info.get('upload_date', '')[:4]))

                    # Buscar portada
                    portada_url = obtener_portada(info.get('uploader', ''), info.get('title', ''))
                    if portada_url:
                        agregar_portada_a_mp3(mp3_file, portada_url)
                        print(f"Portada agregada: {info['title']}")

                    audio.save()
                    print(f"Metadatos añadidos: {info['title']}")
                except Exception as e:
                    print(f"Error al procesar {safe_title}: {e}")
            else:
                print(f"Archivo MP3 no encontrado: {safe_title}")
        except Exception as e:
            print(f"Error al descargar {video_url}: {e}")

print("\nDescarga y etiquetado completados.")
