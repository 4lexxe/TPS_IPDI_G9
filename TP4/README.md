# TP 4 — Procesamiento por Convolucion

**Asignatura:** Procesamiento Digital de Imagenes (PDI)  
**Facultad de Ingenieria — Universidad Nacional de Jujuy (UNJu)**

**Integrantes:**
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

---

## Descripcion

Aplicacion interactiva para el filtrado espacial de imagenes mediante convolucion 2D sobre la componente de luminancia **Y** del espacio de color **YIQ (NTSC)**.

La interfaz HUD de estilo Dark Slate es consistente con los TPs anteriores del grupo.

---

## Objetivos

- Abrir y visualizar una imagen; convertirla al espacio YIQ y operar exclusivamente sobre la luminancia **Y**.
- Implementar el motor de convolucion 2D con extension de borde por **repeticion de filas/columnas** extremas (sin relleno de ceros).
- Aplicar los siguientes grupos de filtros:
  1. **Paso Bajos:** Plano y Bartlett 3x3, 5x5, 7x7; Gaussiano 5x5 y 7x7.
  2. **Detectores de Bordes:** Laplaciano v4 y v8; Sobel en las 8 orientaciones (N, NE, E, SE, S, SW, W, NW).
  3. **Paso Altos y Paso Banda:** Paso altos de frecuencia de corte 0.2 y 0.4; Paso banda 5x5 (DoG).

---

## Estructura

```text
TP4/
├── main.py       # Interfaz HUD Dark Slate + logica de pipeline
├── utils.py      # Motor de convolucion y todos los kernels
├── tp4_pdi.py    # Alias de ejecucion
└── README.md     # Este archivo
```

---

## Implementacion Tecnica

### Extension de Borde por Repeticion

Cuando el kernel necesita pixeles fuera de la imagen, se repiten artificialmente las filas o columnas extremas:

```
[A | A B C D | D]   <- columna A repetida a la izquierda, D a la derecha
```

Implementado en `utils._pad_repeat()` de forma manual mediante `np.repeat` y `np.concatenate` sin usar `np.pad`.

### Pipeline de Procesamiento

```
Imagen RGB [0,1]  -->  YIQ  -->  Extraer Y  -->  Convolucion  -->  Clip [0,1]  -->  Gris RGB
```

---

## Filtros Implementados

### Paso Bajos

| Filtro       | Tamano | Descripcion |
|-------------|--------|-------------|
| Plano       | 3/5/7  | Promedio uniforme (Box filter). Todos los coeficientes = 1/N^2 |
| Bartlett    | 3/5/7  | Filtro triangular separable. Producto exterior del vector [1 2...k...2 1] normalizado |
| Gaussiano   | 5/7    | Kernel Gaussiano analitico con sigma=(size-1)/6 |

### Detectores de Bordes

| Filtro          | Descripcion |
|----------------|-------------|
| Laplaciano v4  | Segunda derivada 4-conexa: [0 1 0 / 1 -4 1 / 0 1 0] |
| Laplaciano v8  | Segunda derivada 8-conexa: [1 1 1 / 1 -8 1 / 1 1 1] |
| Sobel x8       | Primera derivada en 8 orientaciones (N, NE, E, SE, S, SW, W, NW) |

Los detectores de bordes se visualizan con un sesgo de **+0.5** para centrar el cero en gris medio.

### Paso Altos

Implementado como: **HP = Impulso - Gaussiano_PasaBajos**

- fc = 0.2 → sigma grande → LP muy suave → HP agresivo
- fc = 0.4 → sigma moderado → HP mas suave

### Paso Banda

Implementado como diferencia de Gaussianos (**DoG**):  
**BP = G_narrow - G_wide**

---

## Ejecucion

```bash
# Desde la raiz del repositorio:
python TP4/main.py

# O mediante el alias:
python TP4/tp4_pdi.py
```

**Requisitos:**
```bash
pip install numpy pillow
```

*(tkinter se incluye con Python para Windows)*
