# YouTube Downloader - Script Optimizado

Script avanzado para descargar audio y video de YouTube con metadata mejorada y múltiples opciones de configuración.

## Características Principales

### Funcionalidades
- Descarga de **playlists completas** o **videos individuales**
- Soporte para **audio (MP3)** y **video (MP4)**
- **Metadata mejorada** con parsing inteligente de títulos
- **Portadas de álbum** desde Last.fm con fallback a thumbnails de YouTube
- **Barras de progreso** en tiempo real
- **Calidad configurable** para audio y video
- **Descargas concurrentes** para mayor velocidad
- **Logging detallado** con archivo de registro
- **Manejo robusto de errores**

### Optimizaciones

#### 1. **Arquitectura Modular**
- Código organizado en clases y funciones reutilizables
- Clase `MediaDownloader` para manejo centralizado de descargas
- Separación de responsabilidades (descarga, metadata, interfaz)

#### 2. **Metadata Inteligente**
- **Parsing automático de títulos**: Detecta formatos como "Artista - Canción"
- **Limpieza automática**: Elimina etiquetas como [Official Video], (Audio), etc.
- **Múltiples fuentes**:
  - Last.fm API para portadas de álbum de alta calidad
  - YouTube thumbnails como fallback
  - Metadata del video (uploader, fecha, etc.)

#### 3. **Descarga de Videos**
- Soporte completo para descarga de videos en MP4
- Múltiples opciones de calidad (720p, 1080p, mejor disponible)
- Metadata agregada a videos MP4

#### 4. **Rendimiento**
- **Descargas concurrentes**: Hasta 3 descargas simultáneas
- **Barras de progreso**: Feedback visual con `tqdm`
- **Logging eficiente**: Registro en archivo + consola

#### 5. **Experiencia de Usuario**
- Interfaz interactiva mejorada
- Detección automática de playlists vs videos individuales
- Opciones de calidad configurables
- Confirmaciones y feedback claro

## Instalación

### Requisitos del Sistema

**Requerido:**
- Python 3.7+
- `ffmpeg` - Para conversión de audio/video

**Instalar ffmpeg:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS (con Homebrew)
brew install ffmpeg

# Windows (con Chocolatey)
choco install ffmpeg
```

### Dependencias de Python
```bash
pip install -r requirements.txt
```

Las dependencias principales son:
- `pytube` - Para parsear información de playlists
- `yt-dlp` - Para descargar videos/audio
- `mutagen` - Para agregar metadata
- `requests` - Para obtener portadas
- `tqdm` - Para barras de progreso

### Configuración Opcional

Puedes configurar tu propia API key de Last.fm como variable de entorno:
```bash
export LASTFM_API_KEY="tu_api_key_aqui"
```

## Uso

### Ejecución Básica
```bash
python yt.py
```

### Flujo de Uso

1. **Ingresar URL**
   - Playlist de YouTube
   - Video individual de YouTube

2. **Seleccionar Modo**
   - `1`: Audio (MP3) - Solo audio con metadata
   - `2`: Video (MP4) - Video completo con metadata

3. **Seleccionar Calidad**

   **Para Audio:**
   - `1`: 128 kbps (menor tamaño)
   - `2`: 192 kbps (balance) [recomendado]
   - `3`: 320 kbps (mejor calidad)

   **Para Video:**
   - `1`: 720p (HD)
   - `2`: 1080p (Full HD) [recomendado]
   - `3`: Mejor disponible

4. **Carpeta de Destino**
   - Por defecto: `descargas/`
   - Personalizable

5. **Descargas Concurrentes** (solo para playlists de audio)
   - Opción para descargar múltiples archivos simultáneamente

### Ejemplos de Uso

#### Descargar Playlist de Audio
```
URL: https://www.youtube.com/playlist?list=PLxxxxxxxx
Modo: 1 (Audio)
Calidad: 2 (192 kbps)
Carpeta: mis_canciones
Concurrente: S
```

#### Descargar Video Individual
```
URL: https://www.youtube.com/watch?v=xxxxxxx
Modo: 2 (Video)
Calidad: 2 (1080p)
Carpeta: videos
```

#### Descargar Audio de Alta Calidad
```
URL: https://www.youtube.com/watch?v=xxxxxxx
Modo: 1 (Audio)
Calidad: 3 (320 kbps)
Carpeta: musica_hq
```

## Metadata Agregada

### Para Archivos MP3
- **Título**: Parseado inteligentemente del título del video
- **Artista**: Extraído del título o del uploader
- **Álbum**: Nombre de la playlist (o "Álbum desconocido")
- **Año**: Fecha de subida del video
- **Portada**:
  1. Intenta obtener desde Last.fm
  2. Usa thumbnail de YouTube como fallback

### Para Archivos MP4
- Similar a MP3 pero en formato compatible con MP4
- Portada embebida en el archivo de video

## Estructura de Archivos

```
descargas/
├── Nombre_de_Playlist/
│   ├── Artista - Canción 1.mp3
│   ├── Artista - Canción 2.mp3
│   └── ...
└── yt_downloader.log
```

## Logging

El script genera un archivo `yt_downloader.log` con información detallada:
- Descargas exitosas/fallidas
- Errores y advertencias
- Fuente de portadas (Last.fm o YouTube)
- Metadata procesada

## Características Técnicas

### Parsing Inteligente de Títulos
Detecta automáticamente estos formatos:
- `Artista - Título`
- `Artista: Título`
- `Artista | Título`
- `Artista – Título` (guión largo)

Y limpia etiquetas como:
- `[Official Video]`
- `(Audio)`
- `[Lyric Video]`
- `(HD)`
- `(4K)`
- `[Music Video]`

### Sistema de Portadas con Fallback
1. **Primera opción**: Last.fm API
   - Busca la portada oficial del álbum
   - Usa la imagen de mayor resolución disponible

2. **Segunda opción**: YouTube Thumbnail
   - Obtiene la thumbnail de mayor calidad del video
   - Siempre disponible como respaldo

### Descargas Concurrentes
- Usa `ThreadPoolExecutor` para múltiples descargas
- Por defecto: 3 workers simultáneos
- Configurable en la variable `MAX_WORKERS`

## Solución de Problemas

### Error: "Archivo MP3/MP4 no encontrado"
- Verifica que tienes `ffmpeg` instalado en tu sistema
- `ffmpeg` es requerido para convertir audio/video

### Error al obtener portadas
- Verifica tu conexión a internet
- La API de Last.fm tiene límites de requests
- El script usará automáticamente la thumbnail de YouTube

### Descargas lentas
- Activa las descargas concurrentes (solo para playlists)
- Verifica tu velocidad de internet
- Reduce la calidad si es necesario

### Errores con caracteres especiales
- El script sanitiza automáticamente los nombres de archivo
- Los caracteres no permitidos se reemplazan por `_`

## Mejoras Futuras Sugeridas

- [ ] Soporte para otros servicios (SoundCloud, etc.)
- [ ] Búsqueda de música por nombre (sin URL)
- [ ] Conversión a otros formatos (FLAC, AAC, etc.)
- [ ] Integración con Spotify para metadata mejorada
- [ ] GUI opcional
- [ ] Descarga de subtítulos
- [ ] Reanudación de descargas interrumpidas

## Notas

- Este script es solo para uso educativo y personal
- Respeta los derechos de autor y términos de servicio de YouTube
- No uses para distribución comercial de contenido con derechos de autor

## Licencia

Para uso personal y educativo.

---

**Versión**: 2.0 (Optimizada)
**Última actualización**: 2025-11-05
