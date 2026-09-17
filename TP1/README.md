# Procesamiento Digital de Imágenes (PDI)
## Trabajo Práctico N° 1: Espacios Cromáticos y Manipulación en Espacio YIQ

Aplicación con interfaz gráfica interactiva para la manipulación en tiempo real de **Luminancia** ($a$) y **Saturación** ($b$) en el modelo de color NTSC YIQ, desarrollada para la cátedra de Procesamiento Digital de Imágenes de la Facultad de Ingeniería (UNJu).

---

### Integrantes
- **Alex Gabriel Calatayud**
- **Santiago Balceda**
- **Robinson Elias Cala**

---

## Fundamentos Teóricos y Algoritmo

El modelo NTSC YIQ separa la información de **Luminancia** ($Y$) de la información cromática (**Crominancia** $I$ y $Q$). El sistema visual humano posee una sensibilidad aproximada de $80\%$ a la luminancia ($Y$), $15\%$ al canal $I$ y $5\%$ al canal $Q$.

### 1. Transformación Lineal $RGB \to YIQ$ (Diapositiva 41)
Para valores normalizados de $R, G, B \in [0.0, 1.0]$:

$$
\begin{bmatrix}
Y \\
I \\
Q
\end{bmatrix}
=
\begin{bmatrix}
0.299 & 0.587 & 0.114 \\
0.595716 & -0.274453 & -0.321263 \\
0.211456 & -0.522591 & 0.311135
\end{bmatrix}
\begin{bmatrix}
R \\
G \\
B
\end{bmatrix}
$$

### 2. Transformación Inversa $YIQ \to RGB$ (Diapositiva 41)

$$
\begin{bmatrix}
R \\
G \\
B
\end{bmatrix}
=
\begin{bmatrix}
1.0 & 0.9663 & 0.6210 \\
1.0 & -0.2721 & -0.6474 \\
1.0 & -1.1070 & 1.7046
\end{bmatrix}
\begin{bmatrix}
Y \\
I \\
Q
\end{bmatrix}
$$

### 3. Workflow de Manipulación (Diapositiva 47)
1. **Normalización**: Convertir los valores $RGB$ de la imagen al rango $[0.0, 1.0]$.
2. **Transformación $RGB \to YIQ$**: Producto tensorial con la matriz directa de conversión.
3. **Modificación de Luminancia**: $Y' = a \cdot Y$.
4. **Modificación de Saturación**: $I' = b \cdot I$ y $Q' = b \cdot Q$.
5. **Chequeo de rango en $Y'$**: $0.0 \le Y' \le 1.0$ (evitando saturación y artefactos numéricos).
6. **Chequeo de rango en crominancias**:
   - $-0.5957 \le I' \le 0.5957$
   - $-0.5226 \le Q' \le 0.5226$
7. **Transformación $Y'I'Q' \to R'G'B'$**: Aplicación de la matriz inversa y acotación a $[0.0, 1.0]$.
8. **Conversión a bytes**: Multiplicación por $255.0$ y conversión al tipo `uint8`.

---

## Características de la Aplicación

- **Manipulación en Tiempo Real**: Sliders interactivos con visualización inmediata de los cambios.
- **Presets Directos de Diapositivas**:
  - **Escala de Grises / B&N** ($b = 0.0$): Elimina por completo la crominancia (Diapositiva 50).
  - **Baja Saturación** ($b = 0.5$): Reduce la intensidad de los colores (Diapositiva 50).
  - **Super Saturado** ($b = 1.5$): Realza vivamente los tonos (Diapositiva 51).
  - **Baja Luminancia** ($a = 0.5$): Atenúa el brillo general de la imagen (Diapositiva 48).
  - **Alta Luminancia** ($a = 1.3$): Aumenta el brillo hasta la saturación de luminancia (Diapositiva 49).
- **Descomposición de Canales Y, I, Q**: Selector para visualizar individualmente el canal $Y$ (escala de grises) y los canales de crominancia $I$ y $Q$ (Diapositiva 43).
- **Exportación / Guardado**: Permite guardar en disco la imagen procesada o el canal visualizado en formatos PNG, JPEG o BMP.
- **Barra de Estado**: Muestra resolución en píxeles y tiempo de ejecución por cuadro en milisegundos.

---

## Requisitos e Instalación

Requiere Python 3.8+ y las siguientes librerías:

```bash
pip install numpy pillow
```

*(La librería `tkinter` viene incluida por defecto en las distribuciones oficiales de Python para Windows).*

---

## Ejecución

Desde la carpeta `TP1`, ejecutar:

```bash
python main.py
```
