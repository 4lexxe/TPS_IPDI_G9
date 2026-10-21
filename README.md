# Procesamiento Digital de Imágenes (PDI)
## Trabajos Prácticos de Cátedra - Grupo 9
### Facultad de Ingeniería — Universidad Nacional de Jujuy (UNJu)

Repositorio centralizado con los desarrollos y trabajos prácticos de la asignatura **Procesamiento Digital de Imágenes (PDI)** correspondientes al **Grupo 9**.

---

### Integrantes
- **Alex Gabriel Calatayud**
- **Santiago Balceda**
- **Robinson Elias Cala**

---

## Estructura del Repositorio

```text
TPS_IPDI_G9/
├── TP0/                      # Trabajo Práctico N° 0: Introducción a PDI y Tkinter
│   ├── main.py               # Interfaz gráfica principal
│   ├── procesamiento.py      # Operaciones básicas (grises, canales, negativo, histograma)
│   ├── image.png             # Captura de pantalla de la interfaz
│   └── README.md             # Documentación específica de TP0
│
├── TP1/                      # Trabajo Práctico N° 1: Espacios Cromáticos y Modelo YIQ
│   ├── main.py               # Interfaz gráfica interactiva con sliders y presets
│   ├── procesamiento_yiq.py  # Conversión RGB <-> YIQ, alteración a (luz) y b (saturación)
│   └── README.md             # Documentación teórica y fórmulas del TP1
│
├── TP2/                      # Trabajo Práctico N° 2: Aritmética de Píxeles
│   ├── main.py               # Interfaz gráfica de triple visor y panel de operaciones
│   ├── aritmetica_pixeles.py # Cuasi-suma, cuasi-resta, producto, cociente, if-lighter/darker
│   └── README.md             # Documentación detallada de TP2 con fórmulas teóricas
│
├── TP3/                      # Trabajo Práctico N° 3: Operaciones de Luminancia
│   ├── main.py               # Interfaz HUD moderna en espacio YIQ con curva interactiva
│   ├── utils.py              # Conversión RGB <-> YIQ, filtros no lineales y tramos
│   ├── tp3_pdi.py            # Alias de ejecución
│   └── README.md             # Documentación matemática y manual de usuario
│
├── TP4/                      # Trabajo Práctico N° 4: Procesamiento por Convolución
│   ├── main.py               # Interfaz HUD Dark Slate + pipeline de convolución
│   ├── utils.py              # Motor de convolución 2D y todos los kernels
│   ├── tp4_pdi.py            # Alias de ejecución
│   └── README.md             # Documentación y manual de usuario de TP4
│
├── TP5/                      # Trabajo Práctico N° 5: Morfología Matemática y Filtros No Lineales
│   ├── main.py               # Interfaz HUD Dark Studio + control de pipeline
│   ├── utils.py              # Operadores morfológicos, mediana, mean shift, esqueletización
│   ├── tp5_pdi.py            # Alias de ejecución
│   └── README.md             # Documentación matemática y manual de usuario
│
├── .gitignore                # Archivos y temporales excluidos
└── README.md                 # Índice general de los Trabajos Prácticos
```

---

## Resumen de Trabajos Prácticos

### [TP0: Introducción a PDI y Manejo de Canales](TP0/README.md)
- Carga y visualización de imágenes con Tkinter y Pillow.
- Conversión a escala de grises mediante promedio de canales RGB.
- Visualización de canales aislados (Rojo, Verde, Azul).
- Inversión cromática (negativo).
- Cálculo y graficación de histograma de frecuencias por canal con Matplotlib.

### [TP1: Espacio de Color NTSC YIQ y Manipulación Cromática](TP1/README.md)
- Transformaciones directas e inversas entre matrices normalizadas $RGB \leftrightarrow YIQ$.
- Manipulación en tiempo real de **Luminancia** ($a$) y **Saturación** ($b$).
- Presets teóricos de diapositivas (B&N, Desaturado, Super Saturado, Baja Luz, Alta Luz).
- Descomposición visual de canales $Y$ (Luminancia), $I$ y $Q$ (Crominancias).

### [TP2: Aritmética de Píxeles entre Imágenes](TP2/README.md)
- **Cuasi-Suma**:
  - En RGB: Clampeada (anclaje) y Promediada.
  - En YIQ: Clampeada y Promediada (con interpolación convexa ponderada por luminancias).
- **Cuasi-Resta**:
  - En RGB: Clampeada, Promediada y Valor Absoluto ($|A - B|$).
  - En YIQ: Clampeada y Promediada.
- **Producto y Cociente**: Multiplicación normalizada y cociente con factor de protección $\epsilon$.
- **Operaciones Condicionales de Luminancia**: *If-Lighter* e *If-Darker*.
- Soporte para triple visor simultáneo (Imagen A, Imagen B y Resultado C), adaptación automática de resolución y medición de tiempos de cómputo en milisegundos.

### [TP3: Operaciones de Luminancia en Espacio YIQ](TP3/README.md)
- **Filtro Raíz Cuadrada**: $Y' = \sqrt{Y}$ para aclarado no lineal y realce de sombras.
- **Filtro Cuadrado**: $Y' = Y^2$ para compresión de sombras y realce de altas luces.
- **Transformación Lineal a Trozos**: Expansión dinámica en el intervalo $[Y_{min}, Y_{max}]$ con saturación en extremos.
- **HUD Dark Slate**: Visor dual responsivo, representación visual interactiva de la curva $T(Y)$ en tiempo real, sliders vinculados, presets rápidos y análisis de histogramas de luminancia de 32 bins con Matplotlib.

### [TP4: Procesamiento por Convolución](TP4/README.md)
- **Paso Bajos**: Plano (Box) 3×3, 5×5, 7×7; Bartlett triangular 3×3, 5×5, 7×7; Gaussiano 5×5 y 7×7.
- **Detectores de Bordes**: Laplaciano de 4 vecinos (v4) y 8 vecinos (v8); Sobel en las 8 orientaciones (N, NE, E, SE, S, SW, W, NW).
- **Paso Altos**: $HP = \delta - LP_{Gauss}$ con frecuencia de corte $f_c = 0{,}2$ y $f_c = 0{,}4$.
- **Paso Banda**: Diferencia de Gaussianos (DoG) 5×5.
- **Extensión de borde**: Repetición artificial de filas/columnas extremas (sin relleno de ceros).
- **HUD Dark Slate**: Visor dual, visualización interactiva del kernel con grilla de colores y coeficientes numéricos en tiempo real.

### [TP5: Morfología Matemática y Filtros No Lineales](TP5/README.md)
- **Elemento Estructurante en Cruz 3×3**: vecindad activa de 5 píxeles con extensión de borde perimetral.
- **Morfología Básica en Grises**: Erosión (mínimo local) y Dilatación (máximo local).
- **Filtros Morfológicos y Realce**: Apertura, Cierre y Top-Hat blanco.
- **Bordes Morfológicos**: Borde exterior, borde interior y gradiente morfológico.
- **Filtros No Lineales Espaciales**: Mediana 3×3 (filtro de ruido impulsivo) y Mean Shift adaptativo.
- **Segmentación y Morfología Binaria**: Binarización paramétrica y esqueletización topológica iterativa.
- **HUD Dark Studio**: Visor dual responsivo, visualizador matricial del elemento estructurante, encadenamiento secuencial de operaciones y control dinámico de parámetros.

---

## Requisitos e Instalación

Se requiere **Python 3.8+** y las siguientes dependencias:

```bash
pip install numpy pillow matplotlib
```

*(Nota: `tkinter` se encuentra preinstalado por defecto en las distribuciones oficiales de Python para Windows).*

---

## Ejecución de las Aplicaciones

Cada Trabajo Práctico puede ejecutarse de manera independiente:

```bash
# Ejecutar TP0
python TP0/main.py

# Ejecutar TP1
python TP1/main.py

# Ejecutar TP2
python TP2/main.py

# Ejecutar TP3
python TP3/main.py
# o también:
python TP3/tp3_pdi.py

# Ejecutar TP4
python TP4/main.py
# o también:
python TP4/tp4_pdi.py

# Ejecutar TP5
python TP5/main.py
# o también:
python TP5/tp5_pdi.py
```

