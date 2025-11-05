#!/usr/bin/env python3
"""
Script optimizado para descargar audio/video de YouTube con metadata mejorada.
Características:
- Descarga de playlists o videos individuales
- Soporte para audio (MP3) y video (MP4)
- Metadata mejorada con parsing inteligente de títulos
- Portadas desde Last.fm con fallback a thumbnails de YouTube
- Barras de progreso
- Calidad configurable
- Logging detallado
"""

from pytube import Playlist, YouTube
import yt_dlp
import os
import re
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, APIC
from tqdm import tqdm

# Configuración
API_KEY = os.getenv("LASTFM_API_KEY", "ac68033e05ad5b68459f1b701d7ddb3a")
MAX_WORKERS = 3  # Descargas concurrentes

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yt_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MediaDownloader:
    """Clase para manejar la descarga y procesamiento de medios de YouTube."""

    def __init__(self, output_folder: str = "descargas"):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitiza nombres de archivo eliminando caracteres no permitidos."""
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        return name.strip()

    @staticmethod
    def parse_artist_title(title: str) -> Tuple[str, str]:
        """
        Extrae artista y título de un string.
        Formatos soportados:
        - "Artista - Título"
        - "Artista: Título"
        - "Artista | Título"
        """
        separators = [' - ', ': ', ' | ', ' – ']
        for sep in separators:
            if sep in title:
                parts = title.split(sep, 1)
                if len(parts) == 2:
                    artist = parts[0].strip()
                    song_title = parts[1].strip()
                    # Limpiar información extra entre paréntesis/corchetes al final
                    song_title = re.sub(r'\s*[\(\[](?:Official|Audio|Video|Lyric|HD|4K|Music Video).*?[\)\]]', '', song_title, flags=re.IGNORECASE)
                    return artist, song_title
        return "", title

    def get_lastfm_cover(self, artist: str, title: str) -> Optional[str]:
        """Obtiene la URL de la portada desde Last.fm."""
        if not artist or not title:
            return None

        url = "http://ws.audioscrobbler.com/2.0/"
        params = {
            "method": "track.getInfo",
            "api_key": API_KEY,
            "artist": artist,
            "track": title,
            "format": "json"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "track" in data and "album" in data["track"]:
                    album = data["track"]["album"]
                    if "image" in album and len(album["image"]) > 0:
                        # Obtener la imagen de mayor tamaño
                        cover_url = album["image"][-1]["#text"]
                        if cover_url:
                            logger.info(f"Portada encontrada en Last.fm para: {artist} - {title}")
                            return cover_url
        except Exception as e:
            logger.warning(f"Error al obtener portada de Last.fm: {e}")

        return None

    def get_youtube_thumbnail(self, video_info: Dict) -> Optional[str]:
        """Obtiene la mejor thumbnail disponible de YouTube."""
        try:
            if 'thumbnail' in video_info and video_info['thumbnail']:
                return video_info['thumbnail']
            elif 'thumbnails' in video_info and video_info['thumbnails']:
                # Obtener la de mayor resolución
                return video_info['thumbnails'][-1]['url']
        except Exception as e:
            logger.warning(f"Error al obtener thumbnail de YouTube: {e}")
        return None

    def download_image(self, url: str) -> Optional[bytes]:
        """Descarga una imagen desde una URL."""
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            logger.warning(f"Error al descargar imagen: {e}")
        return None

    def add_metadata_mp3(self, mp3_path: Path, info: Dict, playlist_title: Optional[str] = None):
        """Agrega metadata completa a un archivo MP3."""
        try:
            audio = MP3(mp3_path, ID3=ID3)
            if not audio.tags:
                audio.add_tags()

            # Parsear artista y título
            artist, title = self.parse_artist_title(info.get('title', 'Título desconocido'))
            if not artist:
                artist = info.get('uploader', 'Artista desconocido')

            # Agregar tags básicos
            audio.tags.add(TIT2(encoding=3, text=title))
            audio.tags.add(TPE1(encoding=3, text=artist))
            audio.tags.add(TALB(encoding=3, text=playlist_title or info.get('playlist', 'Álbum desconocido')))

            # Agregar año si está disponible
            upload_date = info.get('upload_date', '')
            if upload_date and len(upload_date) >= 4:
                audio.tags.add(TYER(encoding=3, text=upload_date[:4]))

            # Intentar agregar portada (Last.fm primero, YouTube thumbnail como fallback)
            cover_data = None
            cover_url = self.get_lastfm_cover(artist, title)

            if cover_url:
                cover_data = self.download_image(cover_url)
                logger.info(f"Usando portada de Last.fm")

            if not cover_data:
                thumbnail_url = self.get_youtube_thumbnail(info)
                if thumbnail_url:
                    cover_data = self.download_image(thumbnail_url)
                    logger.info(f"Usando thumbnail de YouTube como portada")

            if cover_data:
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,  # Portada frontal
                        desc='Cover',
                        data=cover_data
                    )
                )

            audio.save()
            logger.info(f"Metadata agregada exitosamente: {title}")

        except Exception as e:
            logger.error(f"Error al agregar metadata a {mp3_path}: {e}")

    def add_metadata_mp4(self, mp4_path: Path, info: Dict, playlist_title: Optional[str] = None):
        """Agrega metadata completa a un archivo MP4."""
        try:
            audio = MP4(mp4_path)

            # Parsear artista y título
            artist, title = self.parse_artist_title(info.get('title', 'Título desconocido'))
            if not artist:
                artist = info.get('uploader', 'Artista desconocido')

            # Agregar tags (formato MP4/M4A)
            audio['\xa9nam'] = [title]  # Título
            audio['\xa9ART'] = [artist]  # Artista
            audio['\xa9alb'] = [playlist_title or info.get('playlist', 'Álbum desconocido')]  # Álbum

            # Agregar año
            upload_date = info.get('upload_date', '')
            if upload_date and len(upload_date) >= 4:
                audio['\xa9day'] = [upload_date[:4]]

            # Intentar agregar portada
            cover_data = None
            cover_url = self.get_lastfm_cover(artist, title)

            if cover_url:
                cover_data = self.download_image(cover_url)

            if not cover_data:
                thumbnail_url = self.get_youtube_thumbnail(info)
                if thumbnail_url:
                    cover_data = self.download_image(thumbnail_url)

            if cover_data:
                audio['covr'] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]

            audio.save()
            logger.info(f"Metadata agregada exitosamente: {title}")

        except Exception as e:
            logger.error(f"Error al agregar metadata a {mp4_path}: {e}")

    def download_audio(self, url: str, playlist_title: Optional[str] = None, quality: str = '192') -> bool:
        """Descarga audio en formato MP3."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_folder / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'quiet': True,
            'no_warnings': True,
            'windowsfilenames': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                safe_title = self.sanitize_filename(info['title'])
                mp3_file = self.output_folder / f"{safe_title}.mp3"

                if mp3_file.exists():
                    self.add_metadata_mp3(mp3_file, info, playlist_title)
                    return True
                else:
                    logger.error(f"Archivo MP3 no encontrado: {mp3_file}")
                    return False

        except Exception as e:
            logger.error(f"Error al descargar audio {url}: {e}")
            return False

    def download_video(self, url: str, quality: str = 'best') -> bool:
        """Descarga video en formato MP4."""
        ydl_opts = {
            'format': f'{quality}[ext=mp4]/best[ext=mp4]/best',
            'outtmpl': str(self.output_folder / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'windowsfilenames': True,
            'merge_output_format': 'mp4',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                safe_title = self.sanitize_filename(info['title'])
                mp4_file = self.output_folder / f"{safe_title}.mp4"

                if mp4_file.exists():
                    self.add_metadata_mp4(mp4_file, info)
                    logger.info(f"Video descargado: {safe_title}")
                    return True
                else:
                    logger.error(f"Archivo MP4 no encontrado: {mp4_file}")
                    return False

        except Exception as e:
            logger.error(f"Error al descargar video {url}: {e}")
            return False

    def process_playlist(self, playlist_url: str, mode: str = 'audio', quality: str = '192', concurrent: bool = True):
        """Procesa una playlist completa."""
        try:
            playlist = Playlist(playlist_url)
            playlist_title = self.sanitize_filename(playlist.title or "Lista_de_reproduccion")

            # Crear subcarpeta para la playlist
            playlist_folder = self.output_folder / playlist_title
            playlist_folder.mkdir(exist_ok=True)
            self.output_folder = playlist_folder

            video_urls = list(playlist.video_urls)
            total_videos = len(video_urls)

            logger.info(f"Playlist: {playlist.title}")
            logger.info(f"Total de videos: {total_videos}")
            logger.info(f"Modo: {mode.upper()}")

            successful = 0
            failed = 0

            if concurrent and total_videos > 1:
                # Descarga concurrente
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    if mode == 'audio':
                        futures = {executor.submit(self.download_audio, url, playlist.title, quality): url
                                 for url in video_urls}
                    else:
                        futures = {executor.submit(self.download_video, url, quality): url
                                 for url in video_urls}

                    with tqdm(total=total_videos, desc="Descargando", unit="video") as pbar:
                        for future in as_completed(futures):
                            if future.result():
                                successful += 1
                            else:
                                failed += 1
                            pbar.update(1)
            else:
                # Descarga secuencial
                with tqdm(video_urls, desc="Descargando", unit="video") as pbar:
                    for url in pbar:
                        if mode == 'audio':
                            result = self.download_audio(url, playlist.title, quality)
                        else:
                            result = self.download_video(url, quality)

                        if result:
                            successful += 1
                        else:
                            failed += 1

            logger.info(f"\n{'='*50}")
            logger.info(f"Descarga completada!")
            logger.info(f"Exitosas: {successful}/{total_videos}")
            logger.info(f"Fallidas: {failed}/{total_videos}")
            logger.info(f"Guardado en: {playlist_folder}")
            logger.info(f"{'='*50}")

        except Exception as e:
            logger.error(f"Error al procesar playlist: {e}")

    def process_single_video(self, video_url: str, mode: str = 'audio', quality: str = '192'):
        """Procesa un video individual."""
        try:
            logger.info(f"Descargando video individual en modo: {mode.upper()}")

            if mode == 'audio':
                success = self.download_audio(video_url, quality=quality)
            else:
                success = self.download_video(video_url, quality=quality)

            if success:
                logger.info(f"✓ Descarga completada exitosamente")
            else:
                logger.error(f"✗ Error en la descarga")

        except Exception as e:
            logger.error(f"Error al procesar video: {e}")


def is_playlist(url: str) -> bool:
    """Determina si una URL es de una playlist."""
    return 'playlist' in url or 'list=' in url


def main():
    """Función principal con interfaz de usuario mejorada."""
    print("=" * 60)
    print("  YouTube Downloader - Audio/Video con Metadata Mejorada")
    print("=" * 60)

    # Solicitar URL
    url = input("\nIngresa la URL (video o playlist): ").strip()

    if not url:
        print("❌ URL no válida")
        return

    # Detectar tipo
    is_pl = is_playlist(url)
    url_type = "Playlist" if is_pl else "Video individual"
    print(f"\n📌 Detectado: {url_type}")

    # Seleccionar modo
    print("\n🎯 Selecciona el modo de descarga:")
    print("  1. Audio (MP3) - Solo audio con metadata")
    print("  2. Video (MP4) - Video completo con metadata")

    mode_choice = input("\nOpción [1/2] (default: 1): ").strip() or "1"
    mode = 'audio' if mode_choice == '1' else 'video'

    # Seleccionar calidad
    if mode == 'audio':
        print("\n🎵 Calidad de audio:")
        print("  1. 128 kbps (menor tamaño)")
        print("  2. 192 kbps (balance) [recomendado]")
        print("  3. 320 kbps (mejor calidad)")
        quality_choice = input("\nOpción [1/2/3] (default: 2): ").strip() or "2"
        quality_map = {'1': '128', '2': '192', '3': '320'}
        quality = quality_map.get(quality_choice, '192')
    else:
        print("\n🎬 Calidad de video:")
        print("  1. 720p (HD)")
        print("  2. 1080p (Full HD) [recomendado]")
        print("  3. Mejor disponible")
        quality_choice = input("\nOpción [1/2/3] (default: 2): ").strip() or "2"
        quality_map = {'1': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                       '2': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                       '3': 'best'}
        quality = quality_map.get(quality_choice, 'bestvideo[height<=1080]+bestaudio/best[height<=1080]')

    # Carpeta de salida
    output_folder = input("\n📁 Carpeta de destino (default: 'descargas'): ").strip() or "descargas"

    # Confirmación
    print(f"\n{'='*60}")
    print(f"  Tipo: {url_type}")
    print(f"  Modo: {mode.upper()}")
    print(f"  Calidad: {quality}")
    print(f"  Destino: {output_folder}/")
    print(f"{'='*60}")

    confirm = input("\n¿Continuar con la descarga? [S/n]: ").strip().lower()
    if confirm and confirm not in ['s', 'y', 'yes', 'si', 'sí']:
        print("❌ Descarga cancelada")
        return

    # Iniciar descarga
    downloader = MediaDownloader(output_folder)

    try:
        if is_pl:
            # Preguntar sobre descarga concurrente para playlists
            concurrent = True
            if mode == 'audio':
                concurrent_choice = input("\n⚡ ¿Usar descargas concurrentes (más rápido)? [S/n]: ").strip().lower()
                concurrent = not (concurrent_choice and concurrent_choice not in ['s', 'y', 'yes', 'si', 'sí'])

            downloader.process_playlist(url, mode=mode, quality=quality if mode == 'audio' else quality,
                                       concurrent=concurrent)
        else:
            downloader.process_single_video(url, mode=mode, quality=quality if mode == 'audio' else quality)
    except KeyboardInterrupt:
        print("\n\n⚠️  Descarga interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()
