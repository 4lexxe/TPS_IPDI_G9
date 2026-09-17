"""
Módulo de Procesamiento Digital de Imágenes - Aritmética de Píxeles
Asignatura: Procesamiento Digital de Imágenes (PDI)
Facultad de Ingeniería - UNJu

Integrantes:
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

Contenido y operaciones implementadas según el material de cátedra:
1. Transformaciones entre espacios de color RGB <-> YIQ.
2. Cuasi-suma en RGB (clampeada y promediada).
3. Cuasi-suma en YIQ (clampeada y promediada con interpolación convexa de cromaticidad).
4. Cuasi-resta en RGB (clampeada, promediada y valor absoluto).
5. Cuasi-resta en YIQ (clampeada y promediada).
6. Producto y cociente píxel a píxel entre dos imágenes.
7. Operaciones de selección condicional por luminancia: 'If-lighter' e 'If-darker'.
"""

import numpy as np

# ==============================================================================
# MATRICES DE TRANSFORMACIÓN Y CONSTANTES (Espacio YIQ - NTSC)
# ==============================================================================

# Matriz directa RGB -> YIQ (Diapositiva 41 de teoría)
# Y = 0.299*R + 0.587*G + 0.114*B
# I = 0.595716*R - 0.274453*G - 0.321263*B
# Q = 0.211456*R - 0.522591*G + 0.311135*B
MATRIZ_RGB_A_YIQ = np.array([
    [0.299000,  0.587000,  0.114000],
    [0.595716, -0.274453, -0.321263],
    [0.211456, -0.522591,  0.311135]
], dtype=np.float32)

# Matriz inversa YIQ -> RGB (Diapositiva 41 de teoría)
# R = 1.0*Y + 0.9663*I + 0.6210*Q
# G = 1.0*Y - 0.2721*I - 0.6474*Q
# B = 1.0*Y - 1.1070*I + 1.7046*Q
MATRIZ_YIQ_A_RGB = np.array([
    [1.0000,  0.9663,  0.6210],
    [1.0000, -0.2721, -0.6474],
    [1.0000, -1.1070,  1.7046]
], dtype=np.float32)

# Límites teóricos válidos de los canales YIQ
LIMITE_I_MIN, LIMITE_I_MAX = -0.5957, 0.5957
LIMITE_Q_MIN, LIMITE_Q_MAX = -0.5226, 0.5226


# ==============================================================================
# FUNCIONES AUXILIARES DE NORMALIZACIÓN Y CONVERSIÓN
# ==============================================================================

def normalizar_rgb(imagen):
    """
    Normaliza los valores de la imagen a rango flotante [0.0, 1.0].
    Acepta arrays en uint8 ([0, 255]) o punto flotante.
    """
    img_array = np.asarray(imagen, dtype=np.float32)
    if img_array.max() > 1.0:
        img_array = img_array / 255.0
    return np.clip(img_array, 0.0, 1.0)


def rgb_a_bytes(imagen_float):
    """
    Convierte una imagen en rango normalizado [0.0, 1.0] a formato uint8 [0, 255].
    """
    return (np.clip(imagen_float, 0.0, 1.0) * 255.0).round().astype(np.uint8)


def rgb_a_yiq(imagen_rgb_norm):
    """
    Convierte una imagen RGB normalizada [0.0, 1.0] al espacio YIQ.
    Retorna un array (H, W, 3) con componentes [Y, I, Q].
    """
    return np.tensordot(imagen_rgb_norm, MATRIZ_RGB_A_YIQ, axes=([-1], [1]))


def yiq_a_rgb(imagen_yiq):
    """
    Convierte una imagen en espacio YIQ al espacio RGB normalizado [0.0, 1.0].
    Aplica recorte (clipping) para asegurar el rango válido [0.0, 1.0].
    """
    rgb = np.tensordot(imagen_yiq, MATRIZ_YIQ_A_RGB, axes=([-1], [1]))
    return np.clip(rgb, 0.0, 1.0)


def verificar_dimensiones(img_a, img_b):
    """
    Verifica que dos imágenes posean exactamente las mismas dimensiones (H, W, C).
    """
    if img_a.shape != img_b.shape:
        raise ValueError(
            f"Las imágenes deben tener idéntica resolución. "
            f"Imagen A: {img_a.shape[:2]}, Imagen B: {img_b.shape[:2]}"
        )


# ==============================================================================
# 1. CUASI-SUMA EN RGB (Diapositivas 6-10)
# ==============================================================================

def suma_rgb_clampeada(img_a, img_b):
    """
    Cuasi-suma clampeada en el espacio de color RGB.
    C[i, j] = min(A[i, j] + B[i, j], 1.0)
    
    Suma independientemente cada primario y satura a 1.0 (o 255).
    Puede provocar deriva cromática (color shift) al saturarse un primario
    antes que los otros.
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)
    return np.clip(a + b, 0.0, 1.0)


def suma_rgb_promediada(img_a, img_b):
    """
    Cuasi-suma promediada en el espacio de color RGB.
    C[i, j] = (A[i, j] + B[i, j]) / 2.0
    
    Evita discontinuidades y saturaciones independientes de color,
    pero genera una imagen generalmente más oscura al promediar intensidades.
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)
    return (a + b) / 2.0


# ==============================================================================
# 2. CUASI-SUMA EN YIQ (Diapositivas 11-14)
# ==============================================================================

def suma_yiq_clampeada(img_a, img_b):
    """
    Cuasi-suma clampeada en el espacio de color YIQ.
    
    - Luminancia: YC = min(YA + YB, 1.0)
    - Cromaticidad (interpolación convexa ponderada por luminancias):
      IC = (YA * IA + YB * IB) / (YA + YB)
      QC = (YA * QA + YB * QB) / (YA + YB)
    
    Desacopla la luminancia de la crominancia para evitar la deriva cromática.
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)

    yiq_a = rgb_a_yiq(a)
    yiq_b = rgb_a_yiq(b)

    ya, ia, qa = yiq_a[..., 0], yiq_a[..., 1], yiq_a[..., 2]
    yb, ib, qb = yiq_b[..., 0], yiq_b[..., 1], yiq_b[..., 2]

    # Luminancia clampeada
    yc = np.clip(ya + yb, 0.0, 1.0)

    # Cromaticidad: interpolación convexa
    suma_y = ya + yb
    # Evitar división por cero en píxeles negros
    denominador = np.where(suma_y == 0.0, 1.0, suma_y)

    ic = np.where(suma_y == 0.0, 0.0, (ya * ia + yb * ib) / denominador)
    qc = np.where(suma_y == 0.0, 0.0, (ya * qa + yb * qb) / denominador)

    ic = np.clip(ic, LIMITE_I_MIN, LIMITE_I_MAX)
    qc = np.clip(qc, LIMITE_Q_MIN, LIMITE_Q_MAX)

    yiq_c = np.stack([yc, ic, qc], axis=-1)
    return yiq_a_rgb(yiq_c)


def suma_yiq_promediada(img_a, img_b):
    """
    Cuasi-suma promediada en el espacio de color YIQ.
    
    - Luminancia: YC = (YA + YB) / 2.0
    - Cromaticidad: interpolación convexa ponderada por las luminancias relativas.
    
    Nota teórica (Diapositiva 14): Por linealidad de la transformación y el promedio,
    el resultado cromático global coincide con la suma RGB promediada.
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)

    yiq_a = rgb_a_yiq(a)
    yiq_b = rgb_a_yiq(b)

    ya, ia, qa = yiq_a[..., 0], yiq_a[..., 1], yiq_a[..., 2]
    yb, ib, qb = yiq_b[..., 0], yiq_b[..., 1], yiq_b[..., 2]

    # Luminancia promediada
    yc = (ya + yb) / 2.0

    suma_y = ya + yb
    denominador = np.where(suma_y == 0.0, 1.0, suma_y)

    ic = np.where(suma_y == 0.0, 0.0, (ya * ia + yb * ib) / denominador)
    qc = np.where(suma_y == 0.0, 0.0, (ya * qa + yb * qb) / denominador)

    ic = np.clip(ic, LIMITE_I_MIN, LIMITE_I_MAX)
    qc = np.clip(qc, LIMITE_Q_MIN, LIMITE_Q_MAX)

    yiq_c = np.stack([yc, ic, qc], axis=-1)
    return yiq_a_rgb(yiq_c)


# ==============================================================================
# 3. CUASI-RESTA EN RGB (Diapositiva 16)
# ==============================================================================

def resta_rgb_clampeada(img_a, img_b):
    """
    Cuasi-resta clampeada en el espacio de color RGB.
    C[i, j] = max(A[i, j] - B[i, j], 0.0)
    
    Valores inferiores a 0 se anclan a 0 (negro).
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)
    return np.clip(a - b, 0.0, 1.0)


def resta_rgb_promediada(img_a, img_b):
    """
    Cuasi-resta promediada en el espacio de color RGB.
    C[i, j] = (A[i, j] - B[i, j] + 1.0) / 2.0
    
    Mapea el rango de diferencias [-1.0, 1.0] linealmente al rango visual [0.0, 1.0],
    donde el gris medio (0.5) representa diferencia nula.
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)
    return np.clip((a - b + 1.0) / 2.0, 0.0, 1.0)


def resta_rgb_absoluta(img_a, img_b):
    """
    Resta absoluta entre dos imágenes RGB.
    C[i, j] = |A[i, j] - B[i, j]|
    
    Resalta diferencias netas de intensidad sin importar cuál píxel era más luminoso.
    Es de gran utilidad para detección de movimiento y cambios.
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)
    return np.abs(a - b)


# ==============================================================================
# 4. CUASI-RESTA EN YIQ (Diapositivas 16-17)
# ==============================================================================

def resta_yiq_clampeada(img_a, img_b):
    """
    Cuasi-resta clampeada en el espacio de color YIQ.
    
    - Luminancia: YC = max(YA - YB, 0.0)
    - Crominancia: IC = IA - IB, QC = QA - QB (acotados a sus rangos válidos)
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)

    yiq_a = rgb_a_yiq(a)
    yiq_b = rgb_a_yiq(b)

    ya, ia, qa = yiq_a[..., 0], yiq_a[..., 1], yiq_a[..., 2]
    yb, ib, qb = yiq_b[..., 0], yiq_b[..., 1], yiq_b[..., 2]

    yc = np.clip(ya - yb, 0.0, 1.0)
    ic = np.clip(ia - ib, LIMITE_I_MIN, LIMITE_I_MAX)
    qc = np.clip(qa - qb, LIMITE_Q_MIN, LIMITE_Q_MAX)

    yiq_c = np.stack([yc, ic, qc], axis=-1)
    return yiq_a_rgb(yiq_c)


def resta_yiq_promediada(img_a, img_b):
    """
    Cuasi-resta promediada en el espacio de color YIQ.
    
    - Luminancia: YC = (YA - YB + 1.0) / 2.0
    - Crominancia: IC = (IA - IB) / 2.0, QC = (QA - QB) / 2.0
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)

    yiq_a = rgb_a_yiq(a)
    yiq_b = rgb_a_yiq(b)

    ya, ia, qa = yiq_a[..., 0], yiq_a[..., 1], yiq_a[..., 2]
    yb, ib, qb = yiq_b[..., 0], yiq_b[..., 1], yiq_b[..., 2]

    yc = np.clip((ya - yb + 1.0) / 2.0, 0.0, 1.0)
    ic = np.clip((ia - ib) / 2.0, LIMITE_I_MIN, LIMITE_I_MAX)
    qc = np.clip((qa - qb) / 2.0, LIMITE_Q_MIN, LIMITE_Q_MAX)

    yiq_c = np.stack([yc, ic, qc], axis=-1)
    return yiq_a_rgb(yiq_c)


# ==============================================================================
# 5. PRODUCTO Y COCIENTE (Diapositiva 18)
# ==============================================================================

def producto_rgb(img_a, img_b):
    """
    Producto píxel a píxel entre dos imágenes RGB.
    C[i, j] = A[i, j] * B[i, j]
    
    Al estar normalizadas en [0.0, 1.0], actúa como modulación de máscara o filtro.
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)
    return np.clip(a * b, 0.0, 1.0)


def cociente_rgb(img_a, img_b, epsilon=1.0 / 255.0):
    """
    Cociente píxel a píxel entre dos imágenes RGB.
    C[i, j] = A[i, j] / (B[i, j] + epsilon)
    
    Se suma un epsilon (1/255) al denominador para evitar división por cero.
    El resultado se recorta al intervalo válido [0.0, 1.0].
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)
    divisor = b + epsilon
    return np.clip(a / divisor, 0.0, 1.0)


# ==============================================================================
# 6. OPERACIONES CONDICIONALES POR LUMINANCIA (Diapositivas 15 y 17)
# ==============================================================================

def if_lighter(img_a, img_b):
    """
    Operación 'If-lighter':
    Para cada posición (i, j), conserva el píxel íntegro de la imagen que tenga
    mayor luminancia Y (en el espacio YIQ).
    
    if YA > YB then C[i, j] = A[i, j] else C[i, j] = B[i, j]
    (Diapositiva 15)
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)

    yiq_a = rgb_a_yiq(a)
    yiq_b = rgb_a_yiq(b)

    ya = yiq_a[..., 0]
    yb = yiq_b[..., 0]

    condicion = (ya > yb)[..., np.newaxis]
    return np.where(condicion, a, b)


def if_darker(img_a, img_b):
    """
    Operación 'If-darker':
    Para cada posición (i, j), conserva el píxel íntegro de la imagen que tenga
    menor luminancia Y (en el espacio YIQ).
    
    if YA < YB then C[i, j] = A[i, j] else C[i, j] = B[i, j]
    (Diapositiva 17)
    """
    a = normalizar_rgb(img_a)
    b = normalizar_rgb(img_b)
    verificar_dimensiones(a, b)

    yiq_a = rgb_a_yiq(a)
    yiq_b = rgb_a_yiq(b)

    ya = yiq_a[..., 0]
    yb = yiq_b[..., 0]

    condicion = (ya < yb)[..., np.newaxis]
    return np.where(condicion, a, b)


# ==============================================================================
# 7. UTILIDADES COMPLEMENTARIAS (TP0 Y TP1)
# ==============================================================================

def escala_de_grises(imagen):
    """Convierte la imagen a escala de grises promediando los 3 canales RGB."""
    img_norm = normalizar_rgb(imagen)
    gris = img_norm.mean(axis=2, keepdims=True)
    return np.repeat(gris, 3, axis=2)


def canal_individual(imagen, canal):
    """
    Conserva exclusivamente el canal indicado:
    canal: 0 -> Rojo (R), 1 -> Verde (G), 2 -> Azul (B).
    """
    img_norm = normalizar_rgb(imagen)
    res = np.zeros_like(img_norm)
    res[..., canal] = img_norm[..., canal]
    return res


def cambiar_luminancia_saturacion(imagen, a=1.0, b=1.0):
    """
    Modifica independientemente la luminancia (a) y saturación (b) en espacio YIQ.
    """
    img_norm = normalizar_rgb(imagen)
    yiq = rgb_a_yiq(img_norm)
    y = np.clip(yiq[..., 0] * a, 0.0, 1.0)
    i = np.clip(yiq[..., 1] * b, LIMITE_I_MIN, LIMITE_I_MAX)
    q = np.clip(yiq[..., 2] * b, LIMITE_Q_MIN, LIMITE_Q_MAX)
    return yiq_a_rgb(np.stack([y, i, q], axis=-1))

