# Procesamiento Digital de Imágenes (PDI)
## Trabajo Práctico N° 2: Aritmética de Píxeles

Aplicación con interfaz gráfica interactiva desarrollada para la cátedra de **Procesamiento Digital de Imágenes** de la **Facultad de Ingeniería (UNJu)**, basada en el diseño e identidad visual de los TP's 0 y 1.

Permite realizar operaciones aritméticas entre dos imágenes de igual resolución, explorando los efectos cromáticos tanto en el espacio **RGB** como en el espacio de luminancia y crominancia **YIQ (NTSC)**.

---

### Integrantes
- **Alex Gabriel Calatayud**
- **Santiago Balceda**
- **Robinson Elias Cala**

---

## Fundamentos Teóricos y Operaciones Implementadas

### 1. Cuasi-Suma en Espacio RGB (Diapositivas 6 a 10)
En una cuasi-suma, la luminancia o intensidad resultante es una función monótona no decreciente de la luminancia del segundo operando. Al sumar dos imágenes $A$ y $B$:

- **Suma RGB Clampeada (Anclaje)**:
  $$C[i, j] = \min(A[i, j] + B[i, j], 1.0)$$
  *Problema teórico*: Provoca **deriva cromática** (*color shift*) debido a que los canales $R, G, B$ saturan de manera independiente alterando el tono relativo.
- **Suma RGB Promediada**:
  $$C[i, j] = \frac{A[i, j] + B[i, j]}{2.0}$$
  *Efecto*: Evita la saturación y la deriva cromática, pero la imagen resultante es en general más oscura debido al promedio de niveles.

---

### 2. Cuasi-Suma en Espacio YIQ (Diapositivas 11 a 14)
Desacopla la luminancia ($Y$) de la crominancia ($I, Q$), evitando la deriva cromática:

- **Luminancia $Y_C$**:
  - *Clampeada*: $Y_C = \min(Y_A + Y_B, 1.0)$
  - *Promediada*: $Y_C = \frac{Y_A + Y_B}{2.0}$
- **Cromaticidad $I_C, Q_C$ (Interpolación Convexa)**:
  $$I_C = \frac{Y_A \cdot I_A + Y_B \cdot I_B}{Y_A + Y_B}$$
  $$Q_C = \frac{Y_A \cdot Q_A + Y_B \cdot Q_B}{Y_A + Y_B}$$
  La cromaticidad resultante yace dentro del segmento delimitado por los dos colores en el espacio cromático, ponderada según la luminancia relativa de cada píxel.
- *Propiedad*: La suma YIQ promediada conmuta respecto de transformaciones lineales, coincidiendo con la suma RGB promediada.

---

### 3. Cuasi-Resta en RGB y Valor Absoluto (Diapositiva 16)
La diferencia entre dos imágenes revela cambios, movimiento e iluminación:

- **Resta RGB Clampeada**:
  $$C[i, j] = \max(A[i, j] - B[i, j], 0.0)$$
- **Resta RGB Promediada**:
  $$C[i, j] = \frac{A[i, j] - B[i, j] + 1.0}{2.0}$$
  Mapea linealmente el intervalo $[-1.0, 1.0]$ al rango $[0.0, 1.0]$ (el gris medio $0.5$ representa diferencia nula).
- **Resta RGB Absoluta**:
  $$C[i, j] = |A[i, j] - B[i, j]|$$
  Destaca la magnitud neta de variación entre ambos cuadros.

---

### 4. Cuasi-Resta en Espacio YIQ (Diapositivas 16 y 17)
- **Resta YIQ Clampeada**:
  $$Y_C = \max(Y_A - Y_B, 0.0), \quad I_C = I_A - I_B, \quad Q_C = Q_A - Q_B$$
- **Resta YIQ Promediada**:
  $$Y_C = \frac{Y_A - Y_B + 1.0}{2.0}, \quad I_C = \frac{I_A - I_B}{2.0}, \quad Q_C = \frac{Q_A - Q_B}{2.0}$$

---

### 5. Producto y Cociente (Diapositiva 18)
- **Producto RGB**:
  $$C[i, j] = A[i, j] \cdot B[i, j]$$
  Utilizado para máscaras de atenuación y composición.
- **Cociente RGB**:
  $$C[i, j] = \min\left(\frac{A[i, j]}{B[i, j] + \epsilon}, 1.0\right) \quad \text{donde } \epsilon = \frac{1}{255}$$
  Permite compensar efectos de iluminación no uniforme.

---

### 6. Operaciones Condicionales por Luminancia (Diapositivas 15 y 17)
- **If-Lighter**: Retiene para cada coordenada el píxel íntegro que presente mayor luminancia ($Y_A > Y_B$).
  $$\text{Si } Y_A > Y_B \implies C[i, j] = A[i, j] \quad \text{sino } C[i, j] = B[i, j]$$
- **If-Darker**: Retiene el píxel correlativo de menor luminancia ($Y_A < Y_B$).
  $$\text{Si } Y_A < Y_B \implies C[i, j] = A[i, j] \quad \text{sino } C[i, j] = B[i, j]$$

---

## Características de la Interfaz Gráfica

- **Tres Visores Simultáneos**: Visualización en paralelo de la **Imagen A**, **Imagen B** y el **Resultado C** con indicador de resolución individual.
- **Detección y Adaptación de Resoluciones**: Si las imágenes cargadas poseen dimensiones diferentes, la aplicación ofrece redimensionar automáticamente la Imagen B para ajustarla a la Imagen A.
- **Top Bar con Acciones Rápidas**:
  - `📁 Abrir Imagen A` / `📁 Abrir Imagen B`: Carga de archivos PNG, JPG, BMP, etc.
  - `💾 Guardar C`: Exportación del resultado en PNG, JPG o BMP.
  - `⇄ Usar C como A`: Permite encadenar procesamientos sucesivos (pipeline).
  - `🔀 A ⇄ B`: Intercambia los operandos para observar asimetría en restas y cocientes.
  - `↺ Restaurar A`: Restablece la Imagen A a su estado inicial.
- **Panel de Operaciones Organizado por Categorías**: Botones directos con estilo coherente al TP1.
- **Medición de Rendimiento en Tiempo Real**: La barra de estado reporta el tiempo de ejecución en milisegundos de cada operación.
- **Histograma Integrado con Matplotlib**: Análisis de distribución de frecuencias para Imagen A, Imagen B o Resultado C.

---

## Requisitos e Instalación

Requiere Python 3.8+ y las librerías científicas estándar:

```bash
pip install numpy pillow matplotlib
```

*(La librería `tkinter` se encuentra incluida de fábrica en las distribuciones de Python para Windows).*

---

## Ejecución

Desde la carpeta del proyecto:

```bash
# Desde la raíz del repositorio
python TP2/main.py

# O ingresando al directorio TP2
cd TP2
python main.py
```
