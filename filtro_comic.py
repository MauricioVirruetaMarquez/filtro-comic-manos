"""Filtro cómic en vivo controlado por índice y pulgar de ambas manos."""

from __future__ import annotations

import argparse
import math
import sys

import cv2
import mediapipe as mp
import numpy as np


PULGAR_TIP = 4
INDICE_TIP = 8
DEDOS_PLEGABLES = ((9, 10, 12), (13, 14, 16), (17, 18, 20))


def angulo(a, b, c) -> float:
    """Ángulo ABC en grados, usando también la profundidad estimada."""
    ba = np.array((a.x - b.x, a.y - b.y, a.z - b.z), dtype=np.float32)
    bc = np.array((c.x - b.x, c.y - b.y, c.z - b.z), dtype=np.float32)
    denominador = float(np.linalg.norm(ba) * np.linalg.norm(bc))
    if denominador < 1e-8:
        return 0.0
    coseno = float(np.clip(np.dot(ba, bc) / denominador, -1.0, 1.0))
    return math.degrees(math.acos(coseno))


def gesto_activo(mano) -> bool:
    """Comprueba índice/pulgar extendidos y los otros tres dedos recogidos."""
    puntos = mano.landmark
    indice_extendido = angulo(puntos[5], puntos[6], puntos[INDICE_TIP]) > 150
    pulgar_extendido = angulo(puntos[2], puntos[3], puntos[PULGAR_TIP]) > 145
    otros_recogidos = all(
        angulo(puntos[mcp], puntos[pip], puntos[tip]) < 140
        for mcp, pip, tip in DEDOS_PLEGABLES
    )
    return indice_extendido and pulgar_extendido and otros_recogidos


def pixel(punto, ancho: int, alto: int) -> tuple[int, int]:
    x = int(np.clip(punto.x * ancho, 0, ancho - 1))
    y = int(np.clip(punto.y * alto, 0, alto - 1))
    return x, y


def efecto_comic_byn(imagen: np.ndarray) -> np.ndarray:
    """Crea tonos suaves con contornos negros, estilo viñeta."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    suave = cv2.bilateralFilter(gris, 9, 75, 75)
    tonos = (suave // 32) * 32
    bordes = cv2.adaptiveThreshold(
        suave,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        9,
        7,
    )
    comic = cv2.bitwise_and(tonos, bordes)
    return cv2.cvtColor(comic, cv2.COLOR_GRAY2BGR)


def efecto_retro_noir(imagen: np.ndarray) -> np.ndarray:
    """Blanco y negro de alto contraste con un grano suave de película."""
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    contraste = cv2.convertScaleAbs(gris, alpha=1.55, beta=-42)
    grano = np.random.normal(0, 7, contraste.shape).astype(np.int16)
    con_grano = np.clip(contraste.astype(np.int16) + grano, 0, 255).astype(np.uint8)
    return cv2.cvtColor(con_grano, cv2.COLOR_GRAY2BGR)


def efecto_golden_hour(imagen: np.ndarray) -> np.ndarray:
    """Añade calidez dorada, sombras suaves y una pequeña mejora de luz."""
    flotante = imagen.astype(np.float32)
    # OpenCV usa el orden BGR: bajamos azul y reforzamos rojo y verde.
    flotante[:, :, 0] *= 0.72
    flotante[:, :, 1] *= 1.07
    flotante[:, :, 2] *= 1.24
    calida = np.clip(flotante + np.array([0, 8, 16], dtype=np.float32), 0, 255).astype(np.uint8)
    return cv2.addWeighted(calida, 1.12, cv2.GaussianBlur(calida, (0, 0), 5), -0.12, 6)


def efecto_lala_glow(imagen: np.ndarray) -> np.ndarray:
    """Resplandor suave rosado inspirado en filtros vintage de retrato."""
    flotante = imagen.astype(np.float32)
    flotante[:, :, 0] *= 1.10
    flotante[:, :, 1] *= 0.91
    flotante[:, :, 2] *= 1.16
    rosada = np.clip(flotante + np.array([14, 0, 17], dtype=np.float32), 0, 255).astype(np.uint8)
    brillo = cv2.GaussianBlur(rosada, (0, 0), 13)
    return cv2.addWeighted(rosada, 0.78, brillo, 0.22, 8)


FILTROS = {
    "comic": ("COMIC B/N", efecto_comic_byn),
    "noir": ("RETRO NOIR", efecto_retro_noir),
    "golden": ("GOLDEN HOUR", efecto_golden_hour),
    "lala": ("LALA GLOW", efecto_lala_glow),
}


def aplicar_en_marco(
    fotograma: np.ndarray,
    izquierda,
    derecha,
    efecto,
) -> tuple[np.ndarray, np.ndarray]:
    """Aplica el efecto dentro de las cuatro yemas y devuelve marco ordenado."""
    alto, ancho = fotograma.shape[:2]
    marco = np.array(
        [
            pixel(izquierda.landmark[INDICE_TIP], ancho, alto),
            pixel(derecha.landmark[INDICE_TIP], ancho, alto),
            pixel(derecha.landmark[PULGAR_TIP], ancho, alto),
            pixel(izquierda.landmark[PULGAR_TIP], ancho, alto),
        ],
        dtype=np.int32,
    )

    # Evita mostrar ruido cuando las yemas están prácticamente juntas.
    if abs(cv2.contourArea(marco)) < 1_500:
        return fotograma, marco

    filtrado = efecto(fotograma)
    mascara = np.zeros((alto, ancho), dtype=np.uint8)
    cv2.fillConvexPoly(mascara, marco, 255)
    salida = fotograma.copy()
    salida[mascara == 255] = filtrado[mascara == 255]
    return salida, marco


def texto_con_fondo(
    imagen: np.ndarray,
    texto: str,
    posicion: tuple[int, int],
    color: tuple[int, int, int],
) -> None:
    fuente = cv2.FONT_HERSHEY_SIMPLEX
    escala = 0.65
    grosor = 2
    (ancho, alto), base = cv2.getTextSize(texto, fuente, escala, grosor)
    x, y = posicion
    cv2.rectangle(imagen, (x - 8, y - alto - 8), (x + ancho + 8, y + base + 8), (20, 20, 20), -1)
    cv2.putText(imagen, texto, (x, y), fuente, escala, color, grosor, cv2.LINE_AA)


def ejecutar(indice_camara: int) -> int:
    camara = cv2.VideoCapture(indice_camara, cv2.CAP_DSHOW)
    if not camara.isOpened():
        print(f"No se pudo abrir la cámara {indice_camara}.", file=sys.stderr)
        return 1

    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    manos_api = mp.solutions.hands
    dibujador = mp.solutions.drawing_utils
    filtro_actual = "comic"

    with manos_api.Hands(
        static_image_mode=False,
        max_num_hands=2,
        model_complexity=1,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.60,
    ) as detector:
        while True:
            correcto, fotograma = camara.read()
            if not correcto:
                print("Se perdió la imagen de la cámara.", file=sys.stderr)
                break

            # El espejo hace que el movimiento resulte natural para el usuario.
            fotograma = cv2.flip(fotograma, 1)
            rgb = cv2.cvtColor(fotograma, cv2.COLOR_BGR2RGB)
            resultado = detector.process(rgb)
            manos = resultado.multi_hand_landmarks or []
            activas = [mano for mano in manos if gesto_activo(mano)]
            nombre_filtro, efecto = FILTROS[filtro_actual]

            if len(activas) == 2:
                activas.sort(key=lambda mano: mano.landmark[0].x)
                fotograma, marco = aplicar_en_marco(fotograma, activas[0], activas[1], efecto)
                cv2.polylines(fotograma, [marco], True, (255, 255, 255), 3, cv2.LINE_AA)
                for x, y in marco:
                    cv2.circle(fotograma, (int(x), int(y)), 7, (0, 220, 255), -1, cv2.LINE_AA)
                texto_con_fondo(fotograma, f"FILTRO {nombre_filtro} ACTIVO", (20, 38), (0, 220, 255))
            else:
                texto_con_fondo(
                    fotograma,
                    "Muestra indice y pulgar con ambas manos",
                    (20, 38),
                    (255, 255, 255),
                )

            texto_con_fondo(
                fotograma,
                "1: Comic  2: Noir  3: Golden  4: Glow",
                (20, fotograma.shape[0] - 20),
                (220, 220, 220),
            )

            # Los puntos ayudan a entender qué está detectando el programa.
            for mano in manos:
                dibujador.draw_landmarks(
                    fotograma,
                    mano,
                    manos_api.HAND_CONNECTIONS,
                    dibujador.DrawingSpec(color=(70, 70, 70), thickness=1, circle_radius=2),
                    dibujador.DrawingSpec(color=(160, 160, 160), thickness=1),
                )

            cv2.imshow("Filtro comic con las manos", fotograma)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla in (27, ord("q"), ord("Q")):
                break
            if tecla == ord("1"):
                filtro_actual = "comic"
            elif tecla == ord("2"):
                filtro_actual = "noir"
            elif tecla == ord("3"):
                filtro_actual = "golden"
            elif tecla == ord("4"):
                filtro_actual = "lala"

    camara.release()
    cv2.destroyAllWindows()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camara", type=int, default=0, help="Índice de cámara (por defecto: 0)")
    args = parser.parse_args()
    return ejecutar(args.camara)


if __name__ == "__main__":
    raise SystemExit(main())
