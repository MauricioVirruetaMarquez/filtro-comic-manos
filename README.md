# Filtro comic controlado con las manos

Programa en Python que abre la camara web, detecta ambas manos y muestra un
filtro solo dentro del marco formado por el indice y el pulgar de cada mano.
Cuando separas o acercas los dedos, el area filtrada cambia de tamano y forma
en tiempo real.

El programa funciona completamente en tu computadora: no envia imagenes ni video
a internet.

## Que hace

- Abre la camara web con OpenCV.
- Detecta hasta dos manos con MediaPipe.
- Activa el filtro cuando ambas manos tienen extendidos solo el indice y el
  pulgar.
- Usa las cuatro yemas de los dedos como esquinas de un marco.
- Aplica el filtro elegido solo dentro de ese marco.
- Permite cambiar entre filtros mientras la camara esta abierta.

## Filtros incluidos

- `1` Comic B/N: blanco y negro con tonos reducidos y bordes marcados.
- `2` Retro Noir: blanco y negro con alto contraste y grano suave.
- `3` Golden Hour: color calido, dorado y con luz suave.
- `4` LaLa Glow: brillo rosado tipo filtro vintage de retrato.

Los filtros Retro Noir, Golden Hour y LaLa Glow estan inspirados en los nombres
y la idea visual del proyecto VintageLiveCam, pero la implementacion de este
repositorio fue escrita desde cero.

## Dependencias

Este proyecto usa Python 3.12. Se recomienda esa version porque MediaPipe suele
tardar mas en dar soporte estable a versiones muy nuevas de Python.

Dependencias principales:

- `opencv-python`: abre la camara, lee los fotogramas, dibuja texto y formas en
  pantalla, y aplica operaciones de imagen como desenfoque, umbral adaptativo,
  mezcla de imagenes y conversiones de color.
- `mediapipe`: detecta los puntos de referencia de las manos. El programa usa
  esos puntos para saber donde estan el indice, el pulgar y los dedos recogidos.
- `numpy`: permite trabajar con la imagen como matriz numerica. Se usa para
  calcular angulos de los dedos, crear mascaras, modificar colores y generar
  grano en el filtro Retro Noir.

Las versiones se declaran en `requirements.txt`:

```txt
opencv-python>=4.8,<5
mediapipe==0.10.21
numpy>=1.24,<2
```

## Instalacion en Windows

Instala Python 3.12 si no lo tienes:

```powershell
winget install -e --id Python.Python.3.12
```

Luego crea el entorno virtual e instala las dependencias:

```powershell
cd "C:\Users\sebas\OneDrive\Documentos\ChatGPT\programas nuevos\filtro_comic_manos"
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
```

## Como abrirlo

La forma mas facil en Windows es hacer doble clic en:

```bat
abrir_filtro.bat
```

Tambien puedes abrirlo desde la terminal:

```powershell
.\.venv312\Scripts\python.exe filtro_comic.py
```

Si Windows tiene varias camaras, puedes probar otra con:

```powershell
.\.venv312\Scripts\python.exe filtro_comic.py --camara 1
```

## Controles

- Extiende indice y pulgar en las dos manos para activar el filtro.
- Recoge medio, anular y menique para evitar activaciones accidentales.
- Mueve las cuatro yemas para cambiar el tamano y la forma del marco.
- Pulsa `1`, `2`, `3` o `4` para cambiar de filtro.
- Pulsa `Q` o `Esc` para cerrar.

## Estructura del proyecto

```text
filtro_comic_manos/
  abrir_filtro.bat
  filtro_comic.py
  README.md
  requirements.txt
  .gitignore
```

No se suben a GitHub los entornos virtuales `.venv/` o `.venv312/`, ni los
archivos generados dentro de `__pycache__/`.

## Referencias

- [VintageLiveCam](https://github.com/Devanshi-navi/VintageLiveCam): referencia
  visual para los estilos vintage llamados LaLa Glow, Retro Noir y Golden Hour.
- [OpenCV](https://opencv.org/): libreria usada para captura de camara,
  procesamiento de imagen y dibujo sobre fotogramas.
- [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker):
  tecnologia usada como referencia para deteccion de manos y puntos de dedos.
- [NumPy](https://numpy.org/): libreria usada para calculos numericos sobre
  imagenes y puntos de las manos.
