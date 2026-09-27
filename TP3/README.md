# Procesamiento Digital de Imágenes (PDI)
## Trabajo Práctico N° 3: Operaciones de Luminancia en Espacio YIQ

Aplicación interactiva con interfaz gráfica moderna (**Dark Slate Studio HUD**) para el procesamiento y transformación no lineal de la **Luminancia** ($Y$) en el espacio de color NTSC YIQ, desarrollada para la cátedra de Procesamiento Digital de Imágenes de la Facultad de Ingeniería (Universidad Nacional de Jujuy - UNJu).

---

### Integrantes — Grupo 9
- **Alex Gabriel Calatayud**
- **Santiago Balceda**
- **Robinson Elias Cala**

---

## Objetivos del Trabajo Práctico
1. Carga, normalización y visualización de imágenes digitales en formato RGB.
2. Conversión bidireccional entre los modelos de color $RGB \leftrightarrow YIQ$.
3. Procesamiento selectivo de la componente de **Luminancia ($Y$)** manteniendo fijas las componentes de **Crominancia ($I, Q$)**.
4. Implementación y análisis de transformaciones no lineales:
   - **Filtro Raíz Cuadrada**: $Y' = \sqrt{Y}$ (aclarado de sombras y expansión no lineal de tonos oscuros).
   - **Filtro Cuadrático**: $Y' = Y^2$ (oscurecimiento de medios tonos y resalte de altas luces).
   - **Filtro Lineal a Trozos**: Expansión del contraste en un intervalo de luminancia $[Y_{min}, Y_{max}]$.
5. Análisis estadístico de distribución de luminancia mediante **Histogramas de 32 bins** en el intervalo canónico $[0.0, 1.0]$.
6. Diseño de una interfaz de usuario avanzada (HUD) con **curva de transferencia interactiva en tiempo real**.

---

## Fundamentos Teóricos y Algoritmo

### 1. Espacio de Color NTSC YIQ (Diapositiva 41)
El modelo NTSC separa la información acromática (Luminancia $Y$) de las componentes cromáticas ($I$ en fase y $Q$ en cuadratura).

Para valores normalizados de $R, G, B \in [0.0, 1.0]$:

#### Conversión Directa $RGB \to YIQ$:
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

#### Conversión Inversa $YIQ \to RGB$:
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

Tras la transformación inversa se aplica un recorte de seguridad (clampeo) al intervalo $[0.0, 1.0]$ para evitar desbordes cromáticos numéricos.

---

### 2. Operaciones sobre la Luminancia

En todas las operaciones, las señales de crominancia $I$ y $Q$ **se preservan sin alteraciones**, garantizando que el matiz y la pureza del color original no sufran desfasajes indeseados:

$$I' = I \quad , \quad Q' = Q$$

#### A) Raíz Cuadrada (Aclarado no lineal)
$$Y' = \sqrt{Y}$$
- **Efecto visual**: Al ser $\sqrt{Y} \ge Y$ para $Y \in [0.0, 1.0]$, la función posee una pendiente muy elevada cerca del origen ($Y \to 0$). Esto expande drásticamente las sombras y medios tonos oscuros, haciendo visibles detalles en zonas subexpuestas sin saturar bruscamente las altas luces.

#### B) Cuadrado (Oscurecimiento no lineal)
$$Y' = Y^2$$
- **Efecto visual**: Al ser $Y^2 \le Y$ para $Y \in [0.0, 1.0]$, comprime los valores bajos y medios hacia cero y mantiene únicamente los valores muy cercanos a $1.0$. Resulta ideal para acentuar el contraste de altas luces, reflejos y fuentes lumínicas.

#### C) Transformación Lineal a Trozos
La transformación por tramos definida por los umbrales $0.0 \le Y_{min} < Y_{max} \le 1.0$ actúa de acuerdo a la función a trozos:

$$
Y' = T(Y) = 
\begin{cases} 
0.0 & \text{si } Y < Y_{min} \\
\dfrac{Y - Y_{min}}{Y_{max} - Y_{min}} & \text{si } Y_{min} \le Y \le Y_{max} \\
1.0 & \text{si } Y > Y_{max}
\end{cases}
$$

- **Efecto visual**: Se enfoca el rango dinámico útil en la banda comprendida entre $Y_{min}$ e $Y_{max}$, expandiéndola linealmente para ocupar la totalidad del espectro $[0.0, 1.0]$. Toda luminancia por debajo de $Y_{min}$ satura a negro absoluto ($0.0$) y toda luminancia por encima de $Y_{max}$ satura a blanco absoluto ($1.0$).

---

## Características de la Interfaz Gráfica (HUD Moderno)

La aplicación incorpora un rediseño integral basado en un entorno de desarrollo **Dark Slate Studio**:

1. **Visor Dual Sincronizado**:
   - Tarjetas independientes para **Imagen de Entrada** y **Resultado Procesado**.
   - Redimensionado responsivo con algoritmo Lanczos de alta fidelidad.
   - Indicadores en tiempo real de resolución ($W \times H$) y luminancia media ($\bar{Y}$).

2. **Panel Inspector Tecnológico**:
   - **Selector de Filtro** con tarjeta de explicación matemática inmediata.
   - **Canvas de Curva de Transferencia en Vivo**: Representa gráficamente $T(Y)$ con ejes, grilla y líneas de umbral proyectadas dinámicamente al deslizar los controles.
   - **Doble Control Deslizante (Sliders) y Entradas Numéricas** para $Y_{min}$ e $Y_{max}$, con validación cruzada para evitar solapamientos.
   - **Presets Rápidos**:
     - *Estándar*: $[0.20, 0.80]$
     - *Alto Contraste*: $[0.35, 0.65]$
     - *Expandir Sombras*: $[0.05, 0.50]$
     - *Expandir Luces*: $[0.50, 0.95]$
   - **Modo Tiempo Real (Live Preview)**: Aplica los filtros instantáneamente durante el arrastre de los controles.

3. **Herramientas de Flujo y Pipeline**:
   - **⇄ Usar Resultado como Entrada**: Permite encadenar transformaciones sucesivas.
   - **↺ Restaurar Original**: Regresa la entrada al archivo inicial cargado.
   - **💾 Guardar Resultado**: Exportación directa a PNG, JPG o BMP con cuantización uint8 segura.

4. **Histograma de Luminancia (32 Bins)**:
   - Integración con Matplotlib bajo tema oscuro coordinado.
   - Modalidades: *Entrada*, *Resultado* o *Comparativo (Ambos en paralelo)*.
   - Superposición de líneas guía de media aritmética ($\mu$) y desviación estándar ($\sigma$).

---

## Estructura de Archivos del TP3

```text
TP3/
├── main.py        # Interfaz gráfica moderna (HUD) y controlador de eventos
├── utils.py       # Funciones matemáticas de PDI (RGB <-> YIQ, filtros y estadísticas)
├── tp3_pdi.py     # Script ejecutable alias / punto de entrada alternativo
└── README.md      # Documentación teórica, fórmulas y manual de uso
```

---

## Requisitos de Instalación

Se requiere **Python 3.8+** con las bibliotecas estándar de procesamiento científico:

```bash
pip install numpy pillow matplotlib
```

*(Nota: Tkinter se encuentra incluido por defecto en Python para Windows).*

---

## Ejecución del Programa

Para iniciar la aplicación desde la raíz del proyecto:

```bash
# Opción 1: Ejecutar script principal
python TP3/main.py

# Opción 2: Ejecutar mediante el alias del TP
python TP3/tp3_pdi.py
```
