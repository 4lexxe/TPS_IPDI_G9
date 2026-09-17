"""
PDI - Trabajo Práctico N° 2: Aritmética de Píxeles
Facultad de Ingeniería - Universidad Nacional de Jujuy (UNJu)

Integrantes:
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

Aplicación interactiva con interfaz gráfica en Tkinter para operaciones
aritméticas de píxeles entre dos imágenes (Cuasi-Suma, Cuasi-Resta, Producto,
Cociente, Comparación por Luminancia y análisis de histogramas).
"""

import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

import aritmetica_pixeles as pdi


# ==============================================================================
# CONFIGURACIÓN DE LA VENTANA PRINCIPAL
# ==============================================================================

ventana = tk.Tk()
ventana.title("PDI - TP2: Aritmética de Píxeles (UNJu)")
ventana.geometry("1280x720")
ventana.minsize(1100, 640)

# Variables globales para imágenes (matrices NumPy float32 normalizadas [0.0, 1.0])
img_a_orig = None
img_a = None
img_b = None
img_c = None


# ==============================================================================
# FUNCIONES DE VISUALIZACIÓN Y RENDERIZADO
# ==============================================================================

def mostrar_en_label(img_norm, label, max_ancho=310, max_alto=330):
    """
    Renderiza un array NumPy normalizado [0.0, 1.0] o uint8 en un widget Label
    manteniendo la relación de aspecto original de la imagen.
    """
    if img_norm is None:
        label.config(image="", text="Sin imagen cargada")
        label.foto = None
        return

    # Conversión a uint8
    if img_norm.dtype != np.uint8:
        img_uint8 = (np.clip(img_norm, 0.0, 1.0) * 255.0).round().astype(np.uint8)
    else:
        img_uint8 = img_norm

    pil_img = Image.fromarray(img_uint8)
    # Redimensionado proporcional para el visor
    pil_img.thumbnail((max_ancho, max_alto), Image.Resampling.LANCZOS)
    
    foto = ImageTk.PhotoImage(pil_img)
    label.foto = foto
    label.config(image=foto, text="")


def actualizar_vistas(op_nombre=None, ms=None):
    """
    Actualiza los 3 visores de imágenes y las etiquetas informativas asociadas.
    """
    # Visor Imagen A
    if img_a is not None:
        h, w = img_a.shape[:2]
        lbl_info_a.config(text=f"Resolución: {w}x{h} px")
        mostrar_en_label(img_a, lbl_a)
    else:
        lbl_info_a.config(text="Sin imagen cargada")
        lbl_a.config(image="", text="Abrí la Imagen A")

    # Visor Imagen B
    if img_b is not None:
        h, w = img_b.shape[:2]
        lbl_info_b.config(text=f"Resolución: {w}x{h} px")
        mostrar_en_label(img_b, lbl_b)
    else:
        lbl_info_b.config(text="Sin imagen cargada")
        lbl_b.config(image="", text="Abrí la Imagen B")

    # Visor Imagen C (Resultado)
    if img_c is not None:
        h, w = img_c.shape[:2]
        txt = f"Resolución: {w}x{h} px"
        if op_nombre:
            txt += f" | {op_nombre}"
        lbl_info_c.config(text=txt)
        mostrar_en_label(img_c, lbl_c)
        
        if op_nombre and ms is not None:
            lbl_estado.config(text=f"✓ Operación: {op_nombre} ejecutada con éxito en {ms:.2f} ms.")
    else:
        lbl_info_c.config(text="Esperando operación...")
        lbl_c.config(image="", text="El resultado aparecerá aquí")


# ==============================================================================
# GESTIÓN DE ARCHIVOS Y COMPATIBILIDAD DE RESOLUCIONES
# ==============================================================================

def cargar_imagen_archivo(titulo="Seleccionar imagen"):
    """Diálogo estándar para abrir imágenes compatibles con PIL."""
    ruta = filedialog.askopenfilename(
        title=titulo,
        filetypes=[
            ("Archivos de Imagen", "*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff"),
            ("Todos los archivos", "*.*")
        ]
    )
    if not ruta:
        return None
    try:
        pil_img = Image.open(ruta).convert("RGB")
        return np.array(pil_img, dtype=np.float32) / 255.0
    except Exception as e:
        messagebox.showerror("Error al cargar imagen", f"No se pudo abrir el archivo:\n{e}")
        return None


def verificar_o_adaptar_resolucion():
    """
    Verifica si las imágenes A y B tienen idéntica resolución.
    Si difieren, consulta al usuario si desea redimensionar B al tamaño de A.
    Retorna True si las dimensiones coinciden (o fueron adaptadas), False en caso contrario.
    """
    global img_b
    if img_a is None or img_b is None:
        return True

    if img_a.shape == img_b.shape:
        return True

    h_a, w_a = img_a.shape[:2]
    h_b, w_b = img_b.shape[:2]

    respuesta = messagebox.askyesno(
        "Diferencia de resolución",
        f"La Imagen A es de {w_a}x{h_a} px y la Imagen B es de {w_b}x{h_b} px.\n\n"
        "Las operaciones aritméticas entre imágenes requieren idéntica resolución.\n\n"
        f"¿Desea redimensionar automáticamente la Imagen B a {w_a}x{h_a} px?"
    )

    if respuesta:
        img_b_uint8 = (np.clip(img_b, 0.0, 1.0) * 255.0).astype(np.uint8)
        pil_b = Image.fromarray(img_b_uint8).resize((w_a, h_a), Image.Resampling.LANCZOS)
        img_b = np.array(pil_b, dtype=np.float32) / 255.0
        actualizar_vistas()
        lbl_estado.config(text=f"Imagen B redimensionada a {w_a}x{h_a} px para coincidir con A.")
        return True

    return False


def abrir_imagen_a():
    """Abre y asigna la Imagen A."""
    global img_a_orig, img_a, img_c
    img = cargar_imagen_archivo("Abrir Imagen A")
    if img is not None:
        img_a_orig = img.copy()
        img_a = img.copy()
        # Si no había resultado, inicializarlo con A
        if img_c is None:
            img_c = img.copy()
        verificar_o_adaptar_resolucion()
        actualizar_vistas()
        lbl_estado.config(text="Imagen A cargada correctamente.")


def abrir_imagen_b():
    """Abre y asigna la Imagen B."""
    global img_b
    img = cargar_imagen_archivo("Abrir Imagen B")
    if img is not None:
        img_b = img.copy()
        verificar_o_adaptar_resolucion()
        actualizar_vistas()
        lbl_estado.config(text="Imagen B cargada correctamente.")


def guardar_resultado():
    """Guarda la Imagen C (Resultado) en disco."""
    if img_c is None:
        messagebox.showwarning("Atención", "No hay ninguna imagen resultado para guardar.")
        return

    ruta = filedialog.asksaveasfilename(
        title="Guardar imagen resultado",
        defaultextension=".png",
        filetypes=[
            ("PNG (.png)", "*.png"),
            ("JPEG (.jpg)", "*.jpg"),
            ("BMP (.bmp)", "*.bmp")
        ]
    )
    if not ruta:
        return

    try:
        img_uint8 = (np.clip(img_c, 0.0, 1.0) * 255.0).round().astype(np.uint8)
        Image.fromarray(img_uint8).save(ruta)
        lbl_estado.config(text=f"Imagen guardada exitosamente en: {ruta}")
    except Exception as e:
        messagebox.showerror("Error al guardar", f"No se pudo guardar la imagen:\n{e}")


def usar_resultado_como_a():
    """Pasa el resultado C como la nueva Imagen A (retroalimentación / pipeline)."""
    global img_a
    if img_c is None:
        messagebox.showwarning("Atención", "No hay imagen resultado para usar como entrada.")
        return
    img_a = img_c.copy()
    verificar_o_adaptar_resolucion()
    actualizar_vistas()
    lbl_estado.config(text="La imagen Resultado (C) se asignó como nueva Imagen A.")


def intercambiar_a_y_b():
    """Intercambia los roles de Imagen A e Imagen B."""
    global img_a, img_b
    if img_a is None or img_b is None:
        messagebox.showwarning("Atención", "Se requieren ambas imágenes cargadas para intercambiarlas.")
        return
    img_a, img_b = img_b.copy(), img_a.copy()
    actualizar_vistas()
    lbl_estado.config(text="Se intercambiaron Imagen A ⇄ Imagen B.")


def restaurar_original_a():
    """Restaura la Imagen A a su estado original al abrirla."""
    global img_a
    if img_a_orig is None:
        return
    img_a = img_a_orig.copy()
    verificar_o_adaptar_resolucion()
    actualizar_vistas()
    lbl_estado.config(text="Imagen A restaurada a su copia original.")


# ==============================================================================
# EJECUCIÓN CENTRALIZADA DE OPERACIONES ARITMÉTICAS
# ==============================================================================

def ejecutar_operacion(nombre, funcion, requiere_b=True):
    """
    Ejecuta una operación aritmética de PDI midiendo su tiempo de cálculo
    y gestionando validaciones de entrada.
    """
    global img_c
    if img_a is None:
        messagebox.showwarning("Atención", "Primero debe abrir la Imagen A.")
        return

    if requiere_b:
        if img_b is None:
            messagebox.showwarning("Atención", f"La operación '{nombre}' requiere abrir también la Imagen B.")
            return
        if not verificar_o_adaptar_resolucion():
            return

    try:
        t0 = time.perf_counter()
        if requiere_b:
            resultado = funcion(img_a, img_b)
        else:
            resultado = funcion(img_a)
        t_ms = (time.perf_counter() - t0) * 1000.0

        img_c = resultado
        actualizar_vistas(op_nombre=nombre, ms=t_ms)
    except Exception as e:
        messagebox.showerror("Error en operación", f"Ocurrió un error al ejecutar '{nombre}':\n{e}")


# ==============================================================================
# HERRAMIENTA: VISUALIZACIÓN DE HISTOGRAMA
# ==============================================================================

def mostrar_histograma():
    """
    Muestra el histograma de intensidad de la imagen seleccionada (A, B o C)
    utilizando Matplotlib.
    """
    seleccion = combo_hist.get()
    img_target = None
    nombre = ""

    if seleccion == "Imagen A":
        img_target, nombre = img_a, "Imagen A"
    elif seleccion == "Imagen B":
        img_target, nombre = img_b, "Imagen B"
    else:
        img_target, nombre = img_c, "Resultado C"

    if img_target is None:
        messagebox.showwarning("Atención", f"No hay imagen disponible para '{nombre}'.")
        return

    # Cálculo de luminancia / escala de grises
    gris = img_target.mean(axis=2)
    intensidades = (np.clip(gris, 0.0, 1.0) * 255.0).astype(np.uint8).ravel()

    plt.figure(figsize=(7, 4))
    plt.hist(intensidades, bins=64, range=(0, 256), color="#37474F", edgecolor="black", alpha=0.85)
    plt.title(f"Histograma de Intensidad - {nombre}", fontsize=12, fontweight="bold")
    plt.xlabel("Nivel de Intensidad (0 a 255)", fontsize=10)
    plt.ylabel("Frecuencia (Cantidad de píxeles)", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


# ==============================================================================
# CONSTRUCCIÓN DE LA INTERFAZ GRÁFICA (ESTILO TP1)
# ==============================================================================

# --- Barra Superior (Top Bar) ---
top = tk.Frame(ventana, pady=6, bg="#ffffff", relief="groove", bd=1)
top.pack(fill="x")

btn_font = ("Arial", 9, "bold")

tk.Button(top, text="📁 Abrir Imagen A", bg="#007ACC", fg="white", font=btn_font,
          activebackground="#005999", activeforeground="white", command=abrir_imagen_a).pack(side="left", padx=5)

tk.Button(top, text="📁 Abrir Imagen B", bg="#0288D1", fg="white", font=btn_font,
          activebackground="#01579B", activeforeground="white", command=abrir_imagen_b).pack(side="left", padx=5)

tk.Button(top, text="💾 Guardar C", bg="#4CAF50", fg="white", font=btn_font,
          activebackground="#388E3C", activeforeground="white", command=guardar_resultado).pack(side="left", padx=5)

tk.Button(top, text="⇄ Usar C como A", bg="#673AB7", fg="white", font=btn_font,
          activebackground="#512DA8", activeforeground="white", command=usar_resultado_como_a).pack(side="left", padx=5)

tk.Button(top, text="🔀 A ⇄ B", bg="#FF9800", fg="white", font=btn_font,
          activebackground="#F57C00", activeforeground="white", command=intercambiar_a_y_b).pack(side="left", padx=5)

tk.Button(top, text="↺ Restaurar A", bg="#e53935", fg="white", font=btn_font,
          activebackground="#c62828", activeforeground="white", command=restaurar_original_a).pack(side="left", padx=5)

tk.Label(top, text="Integrantes: Alex Gabriel Calatayud • Santiago Balceda • Robinson Elias Cala",
         fg="#555", bg="#ffffff", font=("Arial", 9)).pack(side="right", padx=12)


# --- Panel Central (Visualizadores + Controles) ---
mid = tk.Frame(ventana)
mid.pack(fill="both", expand=True, padx=8, pady=6)

# Área de Visualización (3 Paneles: Imagen A, Imagen B, Resultado C)
zona_visores = tk.Frame(mid)
zona_visores.pack(side="left", fill="both", expand=True)

# 1. Panel Imagen A
p_a = tk.Frame(zona_visores, relief="ridge", bd=1, padx=4, pady=4)
p_a.pack(side="left", fill="both", expand=True, padx=4)

tk.Label(p_a, text="Imagen A (Base)", font=("Arial", 10, "bold"), fg="#007ACC").pack(pady=(2, 0))
lbl_info_a = tk.Label(p_a, text="Sin imagen cargada", font=("Arial", 8), fg="#666")
lbl_info_a.pack(pady=(0, 4))
lbl_a = tk.Label(p_a, text="Abrí la Imagen A", bg="#f3f3f3", relief="groove")
lbl_a.pack(fill="both", expand=True)

# 2. Panel Imagen B
p_b = tk.Frame(zona_visores, relief="ridge", bd=1, padx=4, pady=4)
p_b.pack(side="left", fill="both", expand=True, padx=4)

tk.Label(p_b, text="Imagen B (Operando)", font=("Arial", 10, "bold"), fg="#0288D1").pack(pady=(2, 0))
lbl_info_b = tk.Label(p_b, text="Sin imagen cargada", font=("Arial", 8), fg="#666")
lbl_info_b.pack(pady=(0, 4))
lbl_b = tk.Label(p_b, text="Abrí la Imagen B", bg="#f3f3f3", relief="groove")
lbl_b.pack(fill="both", expand=True)

# 3. Panel Resultado C
p_c = tk.Frame(zona_visores, relief="ridge", bd=1, padx=4, pady=4)
p_c.pack(side="left", fill="both", expand=True, padx=4)

lbl_titulo_c = tk.Label(p_c, text="Resultado C", font=("Arial", 10, "bold"), fg="#2E7D32")
lbl_titulo_c.pack(pady=(2, 0))
lbl_info_c = tk.Label(p_c, text="Esperando operación...", font=("Arial", 8), fg="#666")
lbl_info_c.pack(pady=(0, 4))
lbl_c = tk.Label(p_c, text="El resultado aparecerá aquí", bg="#f3f3f3", relief="groove")
lbl_c.pack(fill="both", expand=True)


# --- Panel Derecho de Controles ---
panel_ctrl_contenedor = tk.Frame(mid, width=280, padx=6)
panel_ctrl_contenedor.pack(side="right", fill="y")

# Canvas con scrollbar para panel de controles garantizando que todo sea visible
canvas_ctrl = tk.Canvas(panel_ctrl_contenedor, width=270, highlightthickness=0)
scrollbar_ctrl = tk.Scrollbar(panel_ctrl_contenedor, orient="vertical", command=canvas_ctrl.yview)
ctrl = tk.Frame(canvas_ctrl, padx=2)

ctrl.bind("<Configure>", lambda e: canvas_ctrl.configure(scrollregion=canvas_ctrl.bbox("all")))
canvas_ctrl.create_window((0, 0), window=ctrl, anchor="nw")
canvas_ctrl.configure(yscrollcommand=scrollbar_ctrl.set)

canvas_ctrl.pack(side="left", fill="both", expand=True)
scrollbar_ctrl.pack(side="right", fill="y")


# --- Funciones auxiliares para poblar botones de control ---
def crear_encabezado(texto, color="#222"):
    lbl = tk.Label(ctrl, text=texto, font=("Arial", 9, "bold"), fg=color, anchor="w")
    lbl.pack(fill="x", pady=(10, 3))
    return lbl

def crear_boton_op(texto, op_nombre, funcion, requiere_b=True, color_btn="#ffffff", fg_btn="#111111"):
    btn = tk.Button(
        ctrl,
        text=texto,
        font=("Arial", 8),
        bg=color_btn,
        fg=fg_btn,
        anchor="w",
        padx=8,
        pady=2,
        relief="groove",
        command=lambda: ejecutar_operacion(op_nombre, funcion, requiere_b)
    )
    btn.pack(fill="x", pady=1)
    return btn


# --- Sección 1: Cuasi-Suma ---
crear_encabezado("➕ 1. Cuasi-Suma (RGB y YIQ)", "#007ACC")
crear_boton_op("Suma RGB Clampeada", "Suma RGB Clampeada", pdi.suma_rgb_clampeada)
crear_boton_op("Suma RGB Promediada", "Suma RGB Promediada", pdi.suma_rgb_promediada)
crear_boton_op("Suma YIQ Clampeada", "Suma YIQ Clampeada", pdi.suma_yiq_clampeada)
crear_boton_op("Suma YIQ Promediada", "Suma YIQ Promediada", pdi.suma_yiq_promediada)

# --- Sección 2: Cuasi-Resta ---
crear_encabezado("➖ 2. Cuasi-Resta (RGB y YIQ)", "#C2185B")
crear_boton_op("Resta RGB Clampeada", "Resta RGB Clampeada", pdi.resta_rgb_clampeada)
crear_boton_op("Resta RGB Promediada", "Resta RGB Promediada", pdi.resta_rgb_promediada)
crear_boton_op("Resta RGB Absoluta (|A - B|)", "Resta RGB Absoluta", pdi.resta_rgb_absoluta)
crear_boton_op("Resta YIQ Clampeada", "Resta YIQ Clampeada", pdi.resta_yiq_clampeada)
crear_boton_op("Resta YIQ Promediada", "Resta YIQ Promediada", pdi.resta_yiq_promediada)

# --- Sección 3: Producto y Cociente ---
crear_encabezado("✖ ➗ 3. Producto y Cociente", "#E65100")
crear_boton_op("Producto RGB (A · B)", "Producto RGB", pdi.producto_rgb)
crear_boton_op("Cociente RGB (A / B)", "Cociente RGB", pdi.cociente_rgb)

# --- Sección 4: Operaciones Condicionales (Luminancia) ---
crear_encabezado("💡 4. Operaciones Condicionales", "#2E7D32")
crear_boton_op("If-Lighter (Mayor Luminancia)", "If-Lighter", pdi.if_lighter)
crear_boton_op("If-Darker (Menor Luminancia)", "If-Darker", pdi.if_darker)

# --- Sección 5: Extras y Filtros de TP1 sobre Imagen A ---
crear_encabezado("🎨 5. Operaciones Auxiliares (Imagen A)", "#455A64")
crear_boton_op("Escala de Grises", "Escala de Grises A", pdi.escala_de_grises, requiere_b=False)
crear_boton_op("Solo Canal R (Rojo)", "Solo Canal R", lambda a: pdi.canal_individual(a, 0), requiere_b=False)
crear_boton_op("Solo Canal G (Verde)", "Solo Canal G", lambda a: pdi.canal_individual(a, 1), requiere_b=False)
crear_boton_op("Solo Canal B (Azul)", "Solo Canal B", lambda a: pdi.canal_individual(a, 2), requiere_b=False)

# --- Sección 6: Histograma ---
crear_encabezado("📊 6. Análisis de Histograma", "#37474F")
frame_hist = tk.Frame(ctrl)
frame_hist.pack(fill="x", pady=2)

combo_hist = ttk.Combobox(frame_hist, values=["Imagen A", "Imagen B", "Resultado C"], state="readonly", font=("Arial", 8), width=12)
combo_hist.set("Resultado C")
combo_hist.pack(side="left", padx=(0, 4))

btn_ver_hist = tk.Button(frame_hist, text="Ver Gráfico", font=("Arial", 8, "bold"), bg="#546E7A", fg="white",
                         command=mostrar_histograma)
btn_ver_hist.pack(side="left", fill="x", expand=True)


# --- Barra de Estado Inferior ---
lbl_estado = tk.Label(
    ventana,
    text="Listo. Cargue una Imagen A y una Imagen B para comenzar a operar.",
    anchor="w",
    bg="#ECEFF1",
    fg="#37474F",
    relief="sunken",
    padx=10,
    pady=5,
    font=("Arial", 9)
)
lbl_estado.pack(side="bottom", fill="x")


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    ventana.mainloop()
