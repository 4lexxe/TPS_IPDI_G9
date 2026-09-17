"""
Módulo de Procesamiento en Espacio de Color YIQ (NTSC)
Asignatura: Procesamiento Digital de Imágenes (PDI)
Facultad de Ingeniería - UNJu

Integrantes:
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

Este módulo implementa las transformaciones lineales entre el espacio RGB y el
espacio YIQ (luminancia y crominancia), así como la manipulación independiente
de luminancia (factor 'a') y saturación (factor 'b') siguiendo estrictamente el
workflow de la Diapositiva 47 de la cátedra.
"""

import numpy as np

# Matriz directa RGB -> YIQ (Diapositiva 41)
# Y = 0.299*R + 0.587*G + 0.114*B
# I = 0.595716*R - 0.274453*G - 0.321263*B
# Q = 0.211456*R - 0.522591*G + 0.311135*B
MATRIZ_RGB_A_YIQ = np.array([
    [0.299000,  0.587000,  0.114000],
    [0.595716, -0.274453, -0.321263],
    [0.211456, -0.522591,  0.311135]
], dtype=np.float32)

# Matriz inversa YIQ -> RGB (Diapositiva 41)
# R = 1.0*Y + 0.9663*I + 0.6210*Q
# G = 1.0*Y - 0.2721*I - 0.6474*Q
# B = 1.0*Y - 1.1070*I + 1.7046*Q
MATRIZ_YIQ_A_RGB = np.array([
    [1.0000,  0.9663,  0.6210],
    [1.0000, -0.2721, -0.6474],
    [1.0000, -1.1070,  1.7046]
], dtype=np.float32)

# Límites teóricos de los canales YIQ
LIMITE_I_MIN, LIMITE_I_MAX = -0.5957, 0.5957
LIMITE_Q_MIN, LIMITE_Q_MAX = -0.5226, 0.5226


def normalizar_rgb(imagen):
    """
    Normaliza los valores de la imagen a rango [0.0, 1.0].
    Acepta imágenes en uint8 ([0, 255]) o float.
    """
    img_array = np.asarray(imagen, dtype=np.float32)
    if img_array.max() > 1.0:
        img_array = img_array / 255.0
    return np.clip(img_array, 0.0, 1.0)


def rgb_a_yiq(imagen_rgb_norm):
    """
    Convierte una imagen RGB normalizada [0.0, 1.0] al espacio YIQ.
    Retorna un array (H, W, 3) con canales [Y, I, Q].
    """
    # Multiplicación matricial por el tensor de píxeles
    return np.tensordot(imagen_rgb_norm, MATRIZ_RGB_A_YIQ, axes=([-1], [1]))


def yiq_a_rgb(imagen_yiq):
    """
    Convierte una imagen en espacio YIQ al espacio RGB normalizado [0.0, 1.0].
    Aplica recorte (clipping) para asegurar el rango válido [0.0, 1.0].
    """
    rgb = np.tensordot(imagen_yiq, MATRIZ_YIQ_A_RGB, axes=([-1], [1]))
    return np.clip(rgb, 0.0, 1.0)


def manipular_luminancia_saturacion(imagen_rgb, a=1.0, b=1.0):
    """
    Aplica el algoritmo de manipulación independiente de luminancia (a)
    y saturación (b) según los 8 pasos especificados en la Diapositiva 47:

    1. Normalizar los valores de RGB del pixel ([0, 1]).
    2. RGB -> YIQ utilizando la matriz de transformación directa.
    3. Y' := a * Y (alteración de luminancia).
    4. I' := b * I ; Q' := b * Q (alteración de saturación).
    5. Chequear que 0.0 <= Y' <= 1.0 (evitar saturación y valores negativos).
    6. Chequear -0.5957 <= I' <= 0.5957 y -0.5226 <= Q' <= 0.5226.
    7. Y'I'Q' -> R'G'B' (conversión a RGB normalizado).
    8. Convertir R'G'B' a bytes (uint8 [0, 255]).

    Retorna:
    - rgb_bytes (np.ndarray uint8 [0, 255])
    - rgb_norm (np.ndarray float32 [0.0, 1.0])
    """
    # Paso 1: Normalización en [0, 1]
    rgb_norm = normalizar_rgb(imagen_rgb)

    # Paso 2: RGB -> YIQ
    yiq = rgb_a_yiq(rgb_norm)

    Y = yiq[..., 0]
    I = yiq[..., 1]
    Q = yiq[..., 2]

    # Paso 3: Alteración de luminancia
    Y_prima = a * Y

    # Paso 4: Alteración de saturación
    I_prima = b * I
    Q_prima = b * Q

    # Paso 5: Chequeo de rango para Y' (0.0 a 1.0)
    Y_prima = np.clip(Y_prima, 0.0, 1.0)

    # Paso 6: Chequeo de rango para I' y Q'
    I_prima = np.clip(I_prima, LIMITE_I_MIN, LIMITE_I_MAX)
    Q_prima = np.clip(Q_prima, LIMITE_Q_MIN, LIMITE_Q_MAX)

    # Paso 7: Reensamblaje y conversión Y'I'Q' -> R'G'B'
    yiq_prima = np.stack([Y_prima, I_prima, Q_prima], axis=-1)
    rgb_salida_norm = yiq_a_rgb(yiq_prima)

    # Paso 8: Conversión a bytes uint8 [0, 255]
    rgb_bytes = (rgb_salida_norm * 255.0).round().astype(np.uint8)

    return rgb_bytes, rgb_salida_norm


def descomponer_canales_yiq(imagen_rgb):
    """
    Descompone una imagen RGB en sus tres canales Y, I, Q
    y genera representaciones visualizables de cada uno:

    - Canal Y: Luminancia (imagen en escala de grises [0, 255]).
    - Canal I: Crominancia I mapeada linealmente a [0, 255] para visualización.
    - Canal Q: Crominancia Q mapeada linealmente a [0, 255] para visualización.

    Retorna un diccionario con arrays uint8 (H, W) o (H, W, 3).
    """
    rgb_norm = normalizar_rgb(imagen_rgb)
    yiq = rgb_a_yiq(rgb_norm)

    Y = yiq[..., 0]
    I = yiq[..., 1]
    Q = yiq[..., 2]

    # Mapeo a uint8 para visualización adecuada
    vis_Y = (np.clip(Y, 0.0, 1.0) * 255.0).astype(np.uint8)

    # I va de -0.5957 a +0.5957 -> normalizamos al rango 0 a 255 centrando el cero en 128
    vis_I = np.clip(((I - LIMITE_I_MIN) / (LIMITE_I_MAX - LIMITE_I_MIN)) * 255.0, 0, 255).astype(np.uint8)

    # Q va de -0.5226 a +0.5226 -> normalizamos al rango 0 a 255 centrando el cero en 128
    vis_Q = np.clip(((Q - LIMITE_Q_MIN) / (LIMITE_Q_MAX - LIMITE_Q_MIN)) * 255.0, 0, 255).astype(np.uint8)

    return {
        "Y": np.stack([vis_Y, vis_Y, vis_Y], axis=-1),
        "I": np.stack([vis_I, vis_I, vis_I], axis=-1),
        "Q": np.stack([vis_Q, vis_Q, vis_Q], axis=-1)
    }
