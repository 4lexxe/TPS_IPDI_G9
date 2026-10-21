# TP 5 — Morfología Matemática y Filtros No Lineales

**Asignatura:** Procesamiento Digital de Imágenes (PDI)  
**Facultad de Ingeniería — Universidad Nacional de Jujuy (UNJu)**

**Integrantes:**
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

---

## Descripción

Aplicación interactiva para el procesamiento no lineal y morfológico de imágenes digitales en escala de grises. Implementa operadores morfológicos con elemento estructurante en cruz de 3×3, extracción de bordes, filtros de realce, filtros no lineales estadísticos (mediana y Mean Shift), y segmentación con esqueletización topológica.

La interfaz de usuario sigue el estándar visual **Dark Studio HUD**, coherente con los trabajos prácticos anteriores del grupo.

---

## Objetivos del Trabajo Práctico

1. Cargar imágenes de diversos formatos y convertirlas automáticamente a escala de grises monocanal mediante ponderación NTSC ($Y = 0.299R + 0.587G + 0.114B$).
2. Definir y aplicar el elemento estructurante en **cruz de 3×3**:
   $$\begin{bmatrix} 0 & 1 & 0 \\ 1 & 1 & 1 \\ 0 & 1 & 0 \end{bmatrix}$$
3. Implementar operaciones morfológicas fundamentales en escala de grises:
   - **Erosión** (filtro de mínimo local sobre la vecindad de la cruz).
   - **Dilatación** (filtro de máximo local sobre la vecindad de la cruz).
   - **Apertura** ($\text{Dilatación}(\text{Erosión}(I))$).
   - **Cierre** ($\text{Erosión}(\text{Dilatación}(I))$).
4. Implementar detectores de bordes y realce morfológico:
   - **Borde Exterior:** $\text{Dilatación}(I) - I$.
   - **Borde Interior:** $I - \text{Erosión}(I)$.
   - **Gradiente Morfológico:** $\text{Dilatación}(I) - \text{Erosión}(I)$.
   - **Top-Hat Blanco:** $I - \text{Apertura}(I)$.
5. Implementar filtros espaciales no lineales:
   - **Filtro de Mediana 3×3**: sustitución de cada píxel por el valor mediano de la ventana completa 3×3 para remoción de ruido impulsivo (sal y pimienta).
   - **Mean Shift**: suavizado adaptativo preservando discontinuidades y bordes mediante clustering iterativo en espacio $(x, y)$ e intensidad de gris.
6. Implementar morfología binaria y segmentación:
   - **Binarización por Umbral**: corte configurable $[0, 255]$.
   - **Esqueletización Binaria**: adelgazamiento topológico iterativo mediante erosiones y aperturas sucesivas hasta el eje medial.
7. Permitir el **encadenamiento de operaciones** (usar la imagen procesada como nueva entrada) para pipelines complejos.

---

## Estructura de Archivos

```text
TP5/
├── main.py       # Interfaz gráfica Dark Studio HUD
├── utils.py      # Motor de operaciones morfológicas y algoritmos
├── tp5_pdi.py    # Punto de entrada alternativo
└── README.md     # Documentación técnica y manual de uso
```

---

## Detalle Teórico de las Operaciones

### 1. Elemento Estructurante en Cruz 3×3
El elemento estructurante define la vecindad activa de 5 píxeles alrededor de cada punto central $(r, c)$:
- Arriba: $(r-1, c)$
- Izquierda: $(r, c-1)$
- Centro: $(r, c)$
- Derecha: $(r, c+1)$
- Abajo: $(r+1, c)$

Los bordes de la imagen se extienden mediante repetición de los píxeles perimetrales (`mode="edge"`).

### 2. Operadores Morfológicos Básicos

| Operación | Definición Matemática | Efecto Visual |
|-----------|------------------------|---------------|
| **Erosión** | $\min_{(i,j) \in B} \{ I(x+i, y+j) \}$ | Contrae regiones claras y dilata cavidades oscuras. |
| **Dilatación** | $\max_{(i,j) \in B} \{ I(x+i, y+j) \}$ | Expande regiones claras y rellena huecos oscuros. |
| **Apertura** | $(I \ominus B) \oplus B$ | Suprime picos brillantes de menor tamaño que la cruz. |
| **Cierre** | $(I \oplus B) \ominus B$ | Rellena valles y orificios oscuros; une partes próximas. |

### 3. Detección de Bordes y Realce

| Operador | Fórmula | Propósito |
|----------|---------|-----------|
| **Borde Exterior** | $(I \oplus B) - I$ | Contorno exterior del objeto sobre fondo oscuro. |
| **Borde Interior** | $I - (I \ominus B)$ | Contorno interior del objeto. |
| **Gradiente Morfológico** | $(I \oplus B) - (I \ominus B)$ | Bordes balanceados e isotrópicos. |
| **Top-Hat Blanco** | $I - (I \circ B)$ | Resalta elementos finos y brillantes sobre fondos irregulares. |

### 4. Filtros No Lineales

- **Mediana 3×3**: Reemplaza el píxel por el percentil 50 de la ventana 3×3. Elimina ruido impulsivo sin desenfocar los bordes rectos.
- **Mean Shift**: Procedimiento iterativo de ascenso de gradiente sobre una función de densidad conjunta espacio-intensidad:
  $$(x^{(k+1)}, y^{(k+1)}, I^{(k+1)}) = \frac{1}{|S|} \sum_{p \in S} (x_p, y_p, I_p)$$
  donde $S$ es el conjunto de píxeles cuya distancia espacial es $\le h_s$ y cuya diferencia de gris es $\le h_r$.

### 5. Esqueletización Binaria

Dado el conjunto binario $X_0 = \text{Binarizar}(I, \text{umbral})$, en cada paso $k$:
$$S_k = (X_k \ominus B) \setminus ((X_k \ominus B) \circ B)$$
$$\text{Esqueleto} = \bigcup_k S_k$$
hasta que $X_k = \emptyset$.

---

## Ejecución

Desde la raíz del repositorio:

```bash
# Ejecución estándar
python TP5/main.py

# O bien mediante el alias de módulo:
python TP5/tp5_pdi.py
```
