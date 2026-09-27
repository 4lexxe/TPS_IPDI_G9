# -*- coding: utf-8 -*-
"""
Módulo de Procesamiento Digital de Imágenes (PDI) - TP 3: Operaciones de Luminancia
Facultad de Ingeniería - Universidad Nacional de Jujuy (UNJu)

Integrantes:
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

Este módulo contiene las transformaciones lineales entre los espacios RGB y YIQ,
así como las funciones no lineales y transformaciones a trozos aplicadas sobre
la componente de Luminancia (Y).
"""

import numpy as np

# ==============================================================================
# MATRICES DE TRANSFORMACIÓN DE ESPACIO DE COLOR (RGB <-> YIQ)
# ==============================================================================

# Matriz de transformación directa RGB -> YIQ (NTSC estándar)
RGB_TO_YIQ = np.array([
    [0.299000,  0.587000,  0.114000],
    [0.595716, -0.274453, -0.321263],
    [0.211456, -0.522591,  0.311135]
], dtype=np.float32)

# Matriz de transformación inversa YIQ -> RGB (NTSC estándar)
YIQ_TO_RGB = np.array([
    [1.000000,  0.966300,  0.621000],
    [1.000000, -0.272100, -0.647400],
    [1.000000, -1.107000,  1.704600]
], dtype=np.float32)

# Límites canónicos para las componentes cromáticas en YIQ
LIMITE_I_MIN, LIMITE_I_MAX = -0.5957, 0.5957
LIMITE_Q_MIN, LIMITE_Q_MAX = -0.5226, 0.5226


# ==============================================================================
# CONVERSIÓN ENTRE ESPACIOS DE COLOR
# ==============================================================================

def rgb_to_yiq(image: np.ndarray) -> np.ndarray:
    """
    Convierte una imagen RGB normalizada [0.0, 1.0] al espacio YIQ.

    Parámetros:
        image: ndarray de tamaño (H, W, 3) con valores en [0.0, 1.0].

    Retorna:
        ndarray de tamaño (H, W, 3) en espacio YIQ:
        - Y: Luminancia en [0.0, 1.0]
        - I: En fase en [-0.5957, 0.5957]
        - Q: En cuadratura en [-0.5226, 0.5226]
    """
    img_f32 = np.asarray(image, dtype=np.float32)
    return img_f32 @ RGB_TO_YIQ.T


def yiq_to_rgb(image: np.ndarray) -> np.ndarray:
    """
    Convierte una imagen en espacio YIQ nuevamente al espacio RGB.
    Aplica clampeo estricto al rango [0.0, 1.0] para evitar artefactos numéricos.

    Parámetros:
        image: ndarray de tamaño (H, W, 3) en espacio YIQ.

    Retorna:
        ndarray de tamaño (H, W, 3) en espacio RGB clampeado en [0.0, 1.0].
    """
    img_f32 = np.asarray(image, dtype=np.float32)
    result = img_f32 @ YIQ_TO_RGB.T
    return np.clip(result, 0.0, 1.0)


# ==============================================================================
# OPERACIONES NO LINEALES SOBRE LUMINANCIA
# ==============================================================================

def square_root_luminance(yiq: np.ndarray) -> np.ndarray:
    """
    Aplica la función raíz cuadrada sobre la luminancia Y:
        Y' = sqrt(Y)

    La raíz cuadrada expande los valores bajos de luminancia (sombras y medios
    tonos oscuros), aumentando el brillo general y mejorando la visibilidad
    en áreas poco iluminadas. Las componentes I y Q permanecen inalteradas.

    Parámetros:
        yiq: ndarray de tamaño (H, W, 3) en espacio YIQ.

    Retorna:
        Copia del array YIQ con la luminancia transformada.
    """
    result = yiq.copy()
    y_clamped = np.clip(result[:, :, 0], 0.0, 1.0)
    result[:, :, 0] = np.sqrt(y_clamped)
    return result


def square_luminance(yiq: np.ndarray) -> np.ndarray:
    """
    Aplica la función cuadrática sobre la luminancia Y:
        Y' = Y^2

    El cuadrado comprime los valores de luminancia comprendidos entre 0 y 1,
    oscureciendo sombras y medios tonos y destacando los brillos más intensos.
    Las componentes I y Q permanecen inalteradas.

    Parámetros:
        yiq: ndarray de tamaño (H, W, 3) en espacio YIQ.

    Retorna:
        Copia del array YIQ con la luminancia transformada.
    """
    result = yiq.copy()
    y_clamped = np.clip(result[:, :, 0], 0.0, 1.0)
    result[:, :, 0] = np.square(y_clamped)
    return result


def piecewise_linear_luminance(yiq: np.ndarray, y_min: float, y_max: float) -> np.ndarray:
    """
    Aplica una transformación lineal a trozos sobre la luminancia Y:

        Y < y_min:
            Y' = 0.0

        y_min <= Y <= y_max:
            Y' = (Y - y_min) / (y_max - y_min)

        Y > y_max:
            Y' = 1.0

    Esta operación expande el rango dinámico del intervalo [y_min, y_max] al
    rango completo [0.0, 1.0], saturando a negro los valores menores a y_min
    y a blanco los valores superiores a y_max. Incrementa significativamente
    el contraste en la banda de interés seleccionada.

    Condición: 0.0 <= y_min < y_max <= 1.0

    Parámetros:
        yiq: ndarray de tamaño (H, W, 3) en espacio YIQ.
        y_min: umbral inferior de luminancia (float en [0.0, 1.0]).
        y_max: umbral superior de luminancia (float en [0.0, 1.0]).

    Retorna:
        Copia del array YIQ con la luminancia transformada.
    """
    if not (0.0 <= y_min < y_max <= 1.0):
        raise ValueError(f"Se debe cumplir 0.0 <= y_min < y_max <= 1.0 (recibido y_min={y_min}, y_max={y_max})")

    result = yiq.copy()
    y = result[:, :, 0]

    new_y = np.zeros_like(y, dtype=np.float32)

    # Valores mayores al umbral superior saturan a blanco (1.0)
    new_y[y > y_max] = 1.0

    # Rango intermedio: interpolación lineal al intervalo [0.0, 1.0]
    middle = (y >= y_min) & (y <= y_max)
    new_y[middle] = (y[middle] - y_min) / (y_max - y_min)

    # Valores menores a y_min quedan en 0.0 por inicialización de zeros_like

    result[:, :, 0] = np.clip(new_y, 0.0, 1.0)
    return result


# ==============================================================================
# FUNCIONES AUXILIARES DE ESTADÍSTICAS Y MÉTRICAS
# ==============================================================================

def calcular_estadisticas_luminancia(imagen_rgb_norm: np.ndarray) -> dict:
    """
    Calcula métricas estadísticas de la luminancia Y de una imagen RGB normalizada.

    Retorna diccionario con: min, max, mean, std, median.
    """
    yiq = rgb_to_yiq(imagen_rgb_norm)
    y = yiq[:, :, 0].ravel()
    return {
        "min": float(np.min(y)),
        "max": float(np.max(y)),
        "mean": float(np.mean(y)),
        "std": float(np.std(y)),
        "median": float(np.median(y))
    }
