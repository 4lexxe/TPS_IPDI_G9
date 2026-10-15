# -*- coding: utf-8 -*-
"""
Módulo de Procesamiento Digital de Imágenes (PDI) - TP 4: Filtrado por Convolución
Facultad de Ingeniería - Universidad Nacional de Jujuy (UNJu)

Integrantes:
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

Contenido:
- Conversión RGB <-> YIQ (reutilizado de TP3).
- Motor de convolución 2D con extensión de borde por repetición de filas/columnas.
- Kernels de paso bajos: Plano (3x3, 5x5, 7x7), Bartlett (3x3, 5x5, 7x7),
  Gaussiano (5x5, 7x7).
- Detectores de bordes: Laplaciano v4, Laplaciano v8, Sobel (8 orientaciones).
- Filtros paso altos y paso banda.
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


def rgb_to_yiq(image: np.ndarray) -> np.ndarray:
    """
    Convierte una imagen RGB normalizada [0.0, 1.0] al espacio YIQ.

    Parametros:
        image: ndarray de tamano (H, W, 3) con valores en [0.0, 1.0].

    Retorna:
        ndarray de tamano (H, W, 3) en espacio YIQ.
    """
    img_f32 = np.asarray(image, dtype=np.float32)
    return img_f32 @ RGB_TO_YIQ.T


def yiq_to_rgb(image: np.ndarray) -> np.ndarray:
    """
    Convierte una imagen en espacio YIQ nuevamente al espacio RGB.

    Parametros:
        image: ndarray de tamano (H, W, 3) en espacio YIQ.

    Retorna:
        ndarray de tamano (H, W, 3) en espacio RGB clampeado en [0.0, 1.0].
    """
    img_f32 = np.asarray(image, dtype=np.float32)
    result = img_f32 @ YIQ_TO_RGB.T
    return np.clip(result, 0.0, 1.0)


# ==============================================================================
# MOTOR DE CONVOLUCION 2D CON EXTENSION DE BORDE POR REPETICION
# ==============================================================================

def _pad_repeat(image: np.ndarray, pad_h: int, pad_w: int) -> np.ndarray:
    """
    Extiende la imagen repitiendo las filas y columnas extremas del borde.
    Implementacion manual sin np.pad para cumplir el requisito del enunciado:
    'repetir artificialmente filas o columnas cuando estas hagan falta'.

    Parametros:
        image: ndarray 2D de tamano (H, W).
        pad_h: cantidad de filas a extender arriba y abajo.
        pad_w: cantidad de columnas a extender a la izquierda y la derecha.

    Retorna:
        ndarray 2D de tamano (H + 2*pad_h, W + 2*pad_w).
    """
    # Extension horizontal: repetir primera y ultima columna
    left_cols  = np.repeat(image[:, :1], pad_w, axis=1)
    right_cols = np.repeat(image[:, -1:], pad_w, axis=1)
    extended_h = np.concatenate([left_cols, image, right_cols], axis=1)

    # Extension vertical: repetir primera y ultima fila
    top_rows    = np.repeat(extended_h[:1, :], pad_h, axis=0)
    bottom_rows = np.repeat(extended_h[-1:, :], pad_h, axis=0)
    padded = np.concatenate([top_rows, extended_h, bottom_rows], axis=0)

    return padded


def apply_filter(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Aplica convolucion 2D sobre una imagen en escala de grises usando el kernel
    provisto. El manejo de bordes se realiza mediante repeticion de filas y
    columnas extremas (tecnica especificada en el enunciado del TP4).

    Usa np.lib.stride_tricks para eficiencia con imagenes grandes.

    Parametros:
        image:  ndarray 2D de tamano (H, W) con valores float en [0.0, 1.0].
        kernel: ndarray 2D cuadrado de tamano (k, k) con k impar.

    Retorna:
        ndarray 2D de tamano (H, W) con el resultado de la convolucion.
    """
    k   = kernel.shape[0]
    pad = k // 2

    padded = _pad_repeat(image.astype(np.float32), pad, pad)
    H, W   = image.shape

    # Voltear kernel para convolucion real (vs. correlacion cruzada)
    kernel_flip = kernel[::-1, ::-1].astype(np.float32)

    # Vista de ventanas deslizantes (H, W, k, k) sin copiar datos
    shape   = (H, W, k, k)
    strides = (
        padded.strides[0], padded.strides[1],
        padded.strides[0], padded.strides[1]
    )
    windows = np.lib.stride_tricks.as_strided(padded, shape=shape, strides=strides)

    output = np.einsum('hwij,ij->hw', windows, kernel_flip)
    return output.astype(np.float32)


# Alias historico mantenido por compatibilidad
convolution = apply_filter


# ==============================================================================
# KERNELS DE PASO BAJOS
# ==============================================================================

def flat_kernel(size: int) -> np.ndarray:
    """
    Kernel de promedio uniforme (Plano / Box filter) de tamano size x size.
    Todos los coeficientes son iguales y suman 1.

    Parametros:
        size: dimension del kernel (3, 5 o 7).

    Retorna:
        ndarray 2D de tamano (size, size) normalizado.
    """
    return np.ones((size, size), dtype=np.float32) / (size * size)


def _bartlett_1d(size: int) -> np.ndarray:
    """Genera el vector triangular (Bartlett) 1D de longitud `size`."""
    half = size // 2
    v    = np.arange(1, half + 2, dtype=np.float32)
    vec  = np.concatenate([v, v[-2::-1]])
    return vec / vec.sum()


def bartlett_kernel(size: int) -> np.ndarray:
    """
    Kernel de Bartlett (triangular separable) de tamano size x size.
    Se obtiene como producto exterior del vector Bartlett 1D consigo mismo.

    Parametros:
        size: dimension del kernel (3, 5 o 7).

    Retorna:
        ndarray 2D de tamano (size, size) normalizado a suma 1.
    """
    v = _bartlett_1d(size)
    k = np.outer(v, v)
    return (k / k.sum()).astype(np.float32)


def gaussian_kernel(size: int, sigma: float = None) -> np.ndarray:
    """
    Kernel Gaussiano de tamano size x size generado analiticamente.
    Si sigma no se especifica, se usa sigma = (size-1)/6 para contener
    +/-3 sigma dentro del kernel.

    Parametros:
        size:  dimension del kernel (5 o 7).
        sigma: desviacion estandar de la Gaussiana (opcional).

    Retorna:
        ndarray 2D de tamano (size, size) normalizado a suma 1.
    """
    if sigma is None:
        sigma = (size - 1) / 6.0

    center = size // 2
    xs = np.arange(size) - center
    ys = np.arange(size) - center
    xx, yy = np.meshgrid(xs, ys)
    g = np.exp(-(xx ** 2 + yy ** 2) / (2.0 * sigma ** 2))
    return (g / g.sum()).astype(np.float32)


# ==============================================================================
# KERNELS DE DETECCION DE BORDES
# ==============================================================================

def laplacian_kernel_v4() -> np.ndarray:
    """
    Kernel Laplaciano de 4 vecinos (conectividad-4).

    Mascara:
        [ 0  1  0 ]
        [ 1 -4  1 ]
        [ 0  1  0 ]
    """
    return np.array([
        [ 0,  1,  0],
        [ 1, -4,  1],
        [ 0,  1,  0]
    ], dtype=np.float32)


def laplacian_kernel_v8() -> np.ndarray:
    """
    Kernel Laplaciano de 8 vecinos (conectividad-8).

    Mascara:
        [ 1  1  1 ]
        [ 1 -8  1 ]
        [ 1  1  1 ]
    """
    return np.array([
        [ 1,  1,  1],
        [ 1, -8,  1],
        [ 1,  1,  1]
    ], dtype=np.float32)


# Kernels de Sobel para las 8 orientaciones cardinales e intercardinalales.
_SOBEL_KERNELS = {
    "E": np.array([
        [-1,  0,  1],
        [-2,  0,  2],
        [-1,  0,  1]
    ], dtype=np.float32),

    "W": np.array([
        [ 1,  0, -1],
        [ 2,  0, -2],
        [ 1,  0, -1]
    ], dtype=np.float32),

    "S": np.array([
        [-1, -2, -1],
        [ 0,  0,  0],
        [ 1,  2,  1]
    ], dtype=np.float32),

    "N": np.array([
        [ 1,  2,  1],
        [ 0,  0,  0],
        [-1, -2, -1]
    ], dtype=np.float32),

    "NE": np.array([
        [ 0,  1,  2],
        [-1,  0,  1],
        [-2, -1,  0]
    ], dtype=np.float32),

    "NW": np.array([
        [ 2,  1,  0],
        [ 1,  0, -1],
        [ 0, -1, -2]
    ], dtype=np.float32),

    "SE": np.array([
        [-2, -1,  0],
        [-1,  0,  1],
        [ 0,  1,  2]
    ], dtype=np.float32),

    "SW": np.array([
        [ 0, -1, -2],
        [ 1,  0, -1],
        [ 2,  1,  0]
    ], dtype=np.float32),
}


def sobel_kernel(direction: str) -> np.ndarray:
    """
    Retorna el kernel de Sobel para la orientacion especificada.

    Parametros:
        direction: una de las 8 orientaciones ('N', 'NE', 'E', 'SE',
                   'S', 'SW', 'W', 'NW').

    Retorna:
        ndarray 2D de tamano (3, 3).

    Lanza:
        ValueError si la direccion no es valida.
    """
    if direction not in _SOBEL_KERNELS:
        raise ValueError(
            f"Direccion Sobel invalida: '{direction}'. "
            f"Opciones validas: {list(_SOBEL_KERNELS.keys())}"
        )
    return _SOBEL_KERNELS[direction].copy()


# ==============================================================================
# FILTROS PASO ALTOS Y PASO BANDA
# ==============================================================================

def high_pass_kernel(cutoff: float, size: int = 7) -> np.ndarray:
    """
    Genera un filtro paso altos en el dominio espacial de tamano size x size
    a partir de un Gaussiano paso bajos: HP = impulso - LP.

    A menor cutoff -> mayor sigma -> LP mas suave -> HP mas agresivo.

    Parametros:
        cutoff: frecuencia de corte normalizada (0.2 o 0.4 segun el enunciado).
        size:   tamano del kernel (impar). Por defecto 7.

    Retorna:
        ndarray 2D de tamano (size, size).
    """
    # sigma crece cuando cutoff baja (mayor suavizado en LP -> mas agresivo HP)
    sigma = (1.0 - cutoff) * size / 6.0 + 0.5
    lp = gaussian_kernel(size, sigma=sigma)

    # Impulso centrado
    impulse = np.zeros((size, size), dtype=np.float32)
    impulse[size // 2, size // 2] = 1.0

    return (impulse - lp).astype(np.float32)


def band_pass_kernel(size: int = 5) -> np.ndarray:
    """
    Filtro paso banda de tamano size x size implementado como diferencia de
    Gaussianos (DoG): BP = G_narrow - G_wide.

    Parametros:
        size: tamano del kernel (impar). Por defecto 5.

    Retorna:
        ndarray 2D de tamano (size, size).
    """
    sigma_narrow = size / 10.0
    sigma_wide   = size / 4.0
    g_narrow = gaussian_kernel(size, sigma=sigma_narrow)
    g_wide   = gaussian_kernel(size, sigma=sigma_wide)
    return (g_narrow - g_wide).astype(np.float32)
