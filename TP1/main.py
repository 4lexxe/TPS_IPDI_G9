import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import procesamiento_yiq as pdi_yiq

# Ventana principal
ventana = tk.Tk()
ventana.title("PDI - TP1: Luminancia y Saturación (YIQ)")
ventana.geometry("1000x560")

# Variables globales
img_original = None
img_procesada = None


# Muestra una imagen NumPy en un widget Label
def mostrar(img, label):
    if img is None:
        return
    foto = ImageTk.PhotoImage(Image.fromarray(img).resize((380, 380)))
    label.foto = foto
    label.config(image=foto, text="")


# Ejecuta el procesamiento YIQ en tiempo real según los sliders
def procesar(*args):
    global img_procesada
    if img_original is None:
        return
    a = float(scale_a.get())
    b = float(scale_b.get())
    img_procesada, _ = pdi_yiq.manipular_luminancia_saturacion(img_original, a, b)
    lbl_titulo_proc.config(text=f"Imagen Procesada (a={a:.2f}, b={b:.2f})")
    mostrar(img_procesada, lbl_der)


# Muestra un canal individual (Y, I o Q) en el visor derecho
def ver_canal(nombre):
    global img_procesada
    if img_original is None:
        return
    canales = pdi_yiq.descomponer_canales_yiq(img_original)
    img_procesada = canales[nombre]
    lbl_titulo_proc.config(text=f"Visualizando Canal {nombre}")
    mostrar(img_procesada, lbl_der)


# Abre y carga una imagen desde el disco
def abrir():
    global img_original
    ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp")])
    if ruta:
        try:
            img_original = np.array(Image.open(ruta).convert("RGB"))
            mostrar(img_original, lbl_izq)
            procesar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")


# Guarda la imagen procesada en disco
def guardar():
    if img_procesada is not None:
        ruta = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
        if ruta:
            Image.fromarray(img_procesada).save(ruta)


# Aplica valores preestablecidos a los sliders
def preset(a, b):
    scale_a.set(a)
    scale_b.set(b)
    procesar()


# --- Barra Superior ---
top = tk.Frame(ventana, pady=6)
top.pack(fill="x")
tk.Button(top, text="📁 Abrir Imagen", bg="#007ACC", fg="white", font=("Arial", 9, "bold"), command=abrir).pack(side="left", padx=5)
tk.Button(top, text="💾 Guardar", bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), command=guardar).pack(side="left", padx=5)
tk.Button(top, text="↺ Restaurar (1.0, 1.0)", bg="#e53935", fg="white", command=lambda: preset(1.0, 1.0)).pack(side="left", padx=5)
tk.Label(top, text="Integrantes: Alex Gabriel Calatayud • Santiago Balceda • Robinson Elias Cala", fg="#555", font=("Arial", 9)).pack(side="right", padx=10)

# --- Panel Central ---
mid = tk.Frame(ventana)
mid.pack(fill="both", expand=True, padx=10, pady=5)

# Panel Izquierdo: Original
p_izq = tk.Frame(mid)
p_izq.pack(side="left", fill="both", expand=True, padx=5)
tk.Label(p_izq, text="Imagen Original", font=("Arial", 10, "bold")).pack(pady=2)
lbl_izq = tk.Label(p_izq, text="Sin imagen cargada", bg="#e8e8e8", relief="groove")
lbl_izq.pack(fill="both", expand=True)

# Panel Central: Procesada / Canal
p_der = tk.Frame(mid)
p_der.pack(side="left", fill="both", expand=True, padx=5)
lbl_titulo_proc = tk.Label(p_der, text="Imagen Procesada", font=("Arial", 10, "bold"))
lbl_titulo_proc.pack(pady=2)
lbl_der = tk.Label(p_der, text="Sin imagen procesada", bg="#e8e8e8", relief="groove")
lbl_der.pack(fill="both", expand=True)

# Panel Derecho: Controles y Presets
ctrl = tk.Frame(mid, width=200, padx=8)
ctrl.pack(side="right", fill="y")

tk.Label(ctrl, text="Luminancia (a):", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))
scale_a = tk.Scale(ctrl, from_=0.0, to=2.0, resolution=0.05, orient="horizontal", command=procesar)
scale_a.set(1.0)
scale_a.pack(fill="x", pady=(0, 5))

tk.Label(ctrl, text="Saturación (b):", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 0))
scale_b = tk.Scale(ctrl, from_=0.0, to=2.0, resolution=0.05, orient="horizontal", command=procesar)
scale_b.set(1.0)
scale_b.pack(fill="x", pady=(0, 10))

tk.Label(ctrl, text="Presets Teóricos:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5, 2))
tk.Button(ctrl, text="B&N (b = 0.0)", command=lambda: preset(1.0, 0.0)).pack(fill="x", pady=2)
tk.Button(ctrl, text="Desaturar (b = 0.5)", command=lambda: preset(1.0, 0.5)).pack(fill="x", pady=2)
tk.Button(ctrl, text="Saturar (b = 1.5)", command=lambda: preset(1.0, 1.5)).pack(fill="x", pady=2)
tk.Button(ctrl, text="Baja Luz (a = 0.5)", command=lambda: preset(0.5, 1.0)).pack(fill="x", pady=2)
tk.Button(ctrl, text="Alta Luz (a = 1.3)", command=lambda: preset(1.3, 1.0)).pack(fill="x", pady=2)

tk.Label(ctrl, text="Canales YIQ:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 2))
tk.Button(ctrl, text="Canal Y (Luminancia)", command=lambda: ver_canal("Y")).pack(fill="x", pady=2)
tk.Button(ctrl, text="Canal I (Crominancia)", command=lambda: ver_canal("I")).pack(fill="x", pady=2)
tk.Button(ctrl, text="Canal Q (Crominancia)", command=lambda: ver_canal("Q")).pack(fill="x", pady=2)
tk.Button(ctrl, text="Imagen Procesada", bg="#e0e0e0", command=procesar).pack(fill="x", pady=(6, 2))

if __name__ == "__main__":
    ventana.mainloop()
