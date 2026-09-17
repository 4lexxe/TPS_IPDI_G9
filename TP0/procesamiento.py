import numpy as np

# Nota: En todas las funciones, el parámetro 'imagen' es un array de NumPy (0.0 a 1.0) xD


# Convierte la imagen a escala de grises :D
def escala_grises(imagen):
    # .mean saca el promedio de los canales de color
    gris = imagen.mean(axis=2)
    # np.stack junta varios arrays a lo largo de un nuevo eje
    return np.stack([gris, gris, gris], axis=2)


# Conserva solo un canal de color (0 = Rojo, 1 = Verde, 2 = Azul)
def solo_canal(imagen, canal):
    # np.zeros_like crea un array de ceros con la misma forma que la imagen
    resultado = np.zeros_like(imagen)
    resultado[:, :, canal] = imagen[:, :, canal]
    return resultado


# Invierte todos los colores de la imagen (efecto negativo)
def invertir_colores(imagen):
    return 1.0 - imagen


# Calcula el histograma de frecuencias (0 a 255) para cada canal RGB
def calcular_histograma(imagen):
    # np.clip acota valores entre 0 y 1, .astype cambia el tipo a entero
    img_uint8 = (np.clip(imagen, 0, 1) * 255).astype(np.uint8)
    # np.histogram calcula la cantidad de píxeles para cada intensidad (0-255)
    hist_r, _ = np.histogram(img_uint8[:, :, 0], bins=256, range=(0, 256))
    hist_g, _ = np.histogram(img_uint8[:, :, 1], bins=256, range=(0, 256))
    hist_b, _ = np.histogram(img_uint8[:, :, 2], bins=256, range=(0, 256))
    return hist_r, hist_g, hist_b
