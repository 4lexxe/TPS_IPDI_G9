#EJECUTAR python .\main.py

import tkinter as tk
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import procesamiento as pdi

# Ventana principal xD
ventana = tk.Tk()
ventana.title("PDI")
ventana.geometry("900x750")

# Variables globales para las imágenes y control de histograma
imagen_original, imagen_entrada, imagen_procesada = None, None, None
histograma_de = tk.StringVar(value="Entrada")


# Muestra una imagen NumPy en un Label de Tkinter
def mostrar(img, label):
    if img is None:
        return
    # Image.fromarray convierte el array NumPy a imagen PIL, .resize redimensiona y ImageTk.PhotoImage lo adapta a Tkinter
    foto = ImageTk.PhotoImage(Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((350, 300)))
    label.foto = foto
    # label.config actualiza la imagen y el texto del widget Label
    label.config(image=foto, text="")


# Actualiza la visualización de ambas imágenes y el histograma
def actualizar(*args):
    mostrar(imagen_entrada, lbl_izq)
    mostrar(imagen_procesada, lbl_der)
    
    img_target = imagen_entrada if histograma_de.get() == "Entrada" else imagen_procesada
    if img_target is not None:
        ax.clear()
        gris = img_target.mean(axis=2)
        intensidades = (np.clip(gris, 0, 1) * 255).astype(np.uint8)
        
        ax.hist(intensidades.reshape(-1), bins=32, range=(0, 256), color="gray", edgecolor="black")
        ax.set_title(f"Histograma - Imagen {histograma_de.get()}", fontsize=10)
        ax.set_xlabel("Valor de intensidad (0-255)", fontsize=9)
        ax.set_ylabel("Frecuencia", fontsize=9)
        ax.tick_params(labelsize=8)
        fig.tight_layout()
        canvas.draw()


# Abre y carga una imagen desde el disco
def abrir():
    global imagen_original, imagen_entrada, imagen_procesada
    ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")])
    if ruta:
        try:
            imagen_original = np.array(Image.open(ruta).convert("RGB")) / 255.0
            imagen_entrada, imagen_procesada = imagen_original.copy(), imagen_original.copy()
            actualizar()
        except Exception:
            pass


# Aplica una función de procesamiento a la imagen de entrada
def aplicar(fn, *args):
    global imagen_procesada
    if imagen_entrada is not None:
        imagen_procesada = fn(imagen_entrada, *args)
        actualizar()


# Pasa la imagen procesada al espacio de la izquierda (entrada)
def pasar():
    global imagen_entrada
    if imagen_procesada is not None:
        imagen_entrada = imagen_procesada.copy()
        actualizar()


# Restaura la imagen original subida al inicio
def restaurar():
    global imagen_entrada, imagen_procesada
    if imagen_original is not None:
        imagen_entrada, imagen_procesada = imagen_original.copy(), imagen_original.copy()
        actualizar()


# Guarda la imagen procesada en el disco
def guardar():
    if imagen_procesada is not None:
        # filedialog.asksaveasfilename abre el diálogo para elegir dónde guardar el archivo
        ruta = filedialog.asksaveasfilename(defaultextension=".png")
        if ruta:
            # Image.fromarray convierte los datos a formato de imagen y .save la escribe en disco
            Image.fromarray((np.clip(imagen_procesada, 0, 1) * 255).astype(np.uint8)).save(ruta)


# Botones superiores de la barra de control
top = tk.Frame(ventana)
top.pack(fill="x", pady=5)
tk.Button(top, text="Abrir", command=abrir).pack(side="left", padx=5)
tk.Button(top, text="Guardar", command=guardar).pack(side="left", padx=5)
tk.Button(top, text="Pasar a izquierda", command=pasar).pack(side="left", padx=5)
tk.Button(top, text="Restaurar", command=restaurar).pack(side="left", padx=5)

# Panel central para imágenes (izquierda/derecha) y botones de operaciones
mid = tk.Frame(ventana)
mid.pack(fill="both", expand=True)

lbl_izq = tk.Label(mid, text="Entrada", bg="#ddd")
lbl_izq.pack(side="left", fill="both", expand=True, padx=5)

lbl_der = tk.Label(mid, text="Procesada", bg="#ddd")
lbl_der.pack(side="right", fill="both", expand=True, padx=5)

ops = tk.Frame(mid)
ops.pack(side="right", fill="y", padx=5)
tk.Button(ops, text="Grises", command=lambda: aplicar(pdi.escala_grises)).pack(fill="x", pady=2)
tk.Button(ops, text="Rojo", command=lambda: aplicar(pdi.solo_canal, 0)).pack(fill="x", pady=2)
tk.Button(ops, text="Verde", command=lambda: aplicar(pdi.solo_canal, 1)).pack(fill="x", pady=2)
tk.Button(ops, text="Azul", command=lambda: aplicar(pdi.solo_canal, 2)).pack(fill="x", pady=2)
tk.Button(ops, text="Invertir", command=lambda: aplicar(pdi.invertir_colores)).pack(fill="x", pady=2)

tk.Label(ops, text="Histograma de:").pack(fill="x", pady=(15, 2))
menu_hist = tk.OptionMenu(ops, histograma_de, "Entrada", "Procesada", command=lambda _: actualizar())
menu_hist.pack(fill="x", pady=2)

# Panel de histograma en la parte inferior
# Figure crea el lienzo contenedor del gráfico
fig = Figure(figsize=(5, 3.2), dpi=80)
# add_subplot crea los ejes donde se dibujarán los datos dentro de la figura
ax = fig.add_subplot(111)
# FigureCanvasTkAgg conecta la figura de matplotlib con la interfaz de Tkinter
canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)

if __name__ == "__main__":
    ventana.mainloop()
