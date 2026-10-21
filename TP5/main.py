# -*- coding: utf-8 -*-
"""PDI - TP5: Morfología Matemática y Filtros No Lineales (UNJu Grupo 9)."""
import os, sys, time, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np

try: from TP5 import utils as pdi
except ImportError: import utils as pdi

BG, CARD, CANVAS, TXT, MUTED, ACCENT = "#0f172a", "#1e293b", "#090d16", "#f8fafc", "#94a3b8", "#38bdf8"
BTN_BG, BTN_ACTIVE = "#334155", "#475569"

class AppMorfologia:
    def __init__(self, root):
        self.root = root
        self.root.title("PDI · TP5: Morfología Matemática & Filtros No Lineales")
        self.root.geometry("1280x750")
        self.root.minsize(1050, 620)
        self.root.configure(bg=BG)

        self.img_orig = self.img_in = self.img_out = None
        self.op = tk.StringVar(value="Erosión 3x3")
        self.umbral = tk.IntVar(value=127)
        self.hs = tk.IntVar(value=3)
        self.hr = tk.IntVar(value=25)

        self._init_ui()

    def _init_ui(self):
        # Header + Toolbar
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=14, pady=(10, 6))
        tk.Label(top, text="PDI · TP5: Morfología & Filtros No Lineales", font=("Segoe UI", 12, "bold"), fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(top, text="Grupo 9 · Cruz 3×3", font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(side="right")

        tb = tk.Frame(self.root, bg=CARD, bd=1, relief="solid", highlightbackground="#334155")
        tb.pack(fill="x", padx=14, pady=(0, 8))
        for txt, cmd, pri in [("📂 Abrir Imagen", self.abrir, True), ("↺ Restaurar", self.restaurar, False),
                             ("⇄ Usar Entrada", self.encadenar, False), ("💾 Guardar", self.guardar, False)]:
            b = tk.Button(tb, text=txt, command=cmd, font=("Segoe UI", 9, "bold" if pri else "normal"),
                          bg="#2563eb" if pri else BTN_BG, fg=TXT, activebackground="#1d4ed8" if pri else BTN_ACTIVE,
                          activeforeground=TXT, relief="flat", padx=10, pady=5, bd=0, cursor="hand2")
            b.pack(side="left", padx=5, pady=5)

        # Centro: Entrada, Controles, Salida
        mid = tk.Frame(self.root, bg=BG)
        mid.pack(fill="both", expand=True, padx=14)

        self.lbl_in = self._panel_img(mid, "IMAGEN DE ENTRADA")
        self._panel_ctrls(mid)
        self.lbl_out = self._panel_img(mid, "IMAGEN PROCESADA")

        # Barra de estado
        self.status = tk.Label(self.root, text="Listo. Abrí una imagen para comenzar.", font=("Segoe UI", 9), fg=MUTED, bg=CARD, anchor="w", padx=10, pady=4)
        self.status.pack(side="bottom", fill="x", padx=14, pady=(6, 8))
        self._sync_params()

    def _panel_img(self, parent, title):
        card = tk.Frame(parent, bg=CARD, bd=1, relief="solid", highlightbackground="#334155")
        card.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg=TXT, bg=CARD).pack(pady=6)
        lbl = tk.Label(card, text="Sin imagen", font=("Segoe UI", 10), fg=MUTED, bg=CANVAS)
        lbl.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        return lbl

    def _panel_ctrls(self, parent):
        ctrl = tk.Frame(parent, bg=CARD, width=280, bd=1, relief="solid", highlightbackground="#334155", padx=10, pady=10)
        ctrl.pack(side="left", fill="y", padx=4)
        ctrl.pack_propagate(False)

        tk.Label(ctrl, text="OPERACIÓN", font=("Segoe UI", 9, "bold"), fg=ACCENT, bg=CARD).pack(anchor="w")
        cb = ttk.Combobox(ctrl, textvariable=self.op, values=list(pdi.OPERACIONES.keys()), state="readonly")
        cb.pack(fill="x", pady=(4, 10))
        cb.bind("<<ComboboxSelected>>", self._sync_params)

        # Marco umbral
        self.f_umb = tk.Frame(ctrl, bg=CARD)
        tk.Label(self.f_umb, text="Umbral (0–255):", font=("Segoe UI", 8), fg=MUTED, bg=CARD).pack(anchor="w")
        tk.Scale(self.f_umb, from_=0, to=255, orient="horizontal", variable=self.umbral, bg=CARD, fg=TXT, highlightthickness=0, troughcolor=BTN_BG).pack(fill="x")

        # Marco Mean Shift
        self.f_ms = tk.Frame(ctrl, bg=CARD)
        for t, v, mx in [("Radio espacial (hs):", self.hs, 10), ("Rango gris (hr):", self.hr, 100)]:
            tk.Label(self.f_ms, text=t, font=("Segoe UI", 8), fg=MUTED, bg=CARD).pack(anchor="w")
            ttk.Spinbox(self.f_ms, from_=1, to=mx, textvariable=v, width=6).pack(anchor="w", pady=(0, 4))

        # Mini Cruz
        tk.Label(ctrl, text="Elemento Cruz 3×3:", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=CARD).pack(anchor="w", pady=(8, 2))
        grid = tk.Frame(ctrl, bg=CANVAS)
        grid.pack(anchor="w", pady=(0, 10))
        for r in range(3):
            row = tk.Frame(grid, bg=CANVAS)
            row.pack()
            for c in range(3):
                on = pdi.ELEMENTO_ESTRUCTURANTE[r, c] == 1
                tk.Label(row, text="1" if on else "0", font=("Consolas", 8, "bold"), bg="#0284c7" if on else BTN_BG, fg=TXT if on else MUTED, width=2).pack(side="left", padx=1, pady=1)

        tk.Button(ctrl, text="⚡ APLICAR", command=self.aplicar, bg="#2563eb", fg=TXT, activebackground="#1d4ed8",
                  activeforeground=TXT, font=("Segoe UI", 10, "bold"), relief="flat", pady=7, cursor="hand2").pack(fill="x", pady=6)

    def _sync_params(self, _=None):
        self.f_umb.pack_forget()
        self.f_ms.pack_forget()
        o = self.op.get()
        if o in ("Binarización por umbral", "Esqueletización binaria"): self.f_umb.pack(fill="x", pady=4)
        elif o == "Mean Shift": self.f_ms.pack(fill="x", pady=4)

    def abrir(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tif *.webp")])
        if not path: return
        try:
            with Image.open(path) as im: self.img_orig = pdi.convertir_escala_grises(im)
            self.img_in, self.img_out = self.img_orig.copy(), None
            self._draw(self.lbl_in, self.img_in)
            self.lbl_out.config(image="", text="Esperando operación...")
            self.status.config(text=f"Imagen cargada: {os.path.basename(path)} ({self.img_in.shape[1]}x{self.img_in.shape[0]} px)")
        except Exception as e: messagebox.showerror("Error", str(e))

    def aplicar(self):
        if self.img_in is None: return messagebox.showwarning("Aviso", "Primero abrí una imagen.")
        o = self.op.get()
        try:
            t0 = time.perf_counter()
            if o == "Binarización por umbral": res = pdi.binarizar_umbral(self.img_in, self.umbral.get())
            elif o == "Esqueletización binaria": res = pdi.esqueletizacion(self.img_in, self.umbral.get())
            elif o == "Mean Shift": res = pdi.mean_shift(self.img_in, self.hs.get(), self.hr.get())
            else: res = pdi.OPERACIONES[o](self.img_in)
            dt = (time.perf_counter() - t0) * 1000
            self.img_out = res
            self._draw(self.lbl_out, self.img_out)
            self.status.config(text=f"{o} aplicada en {dt:.1f} ms.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def encadenar(self):
        if self.img_out is None: return messagebox.showwarning("Aviso", "No hay resultado para encadenar.")
        self.img_in = self.img_out.copy()
        self._draw(self.lbl_in, self.img_in)
        self.status.config(text="Resultado fijado como nueva entrada.")

    def restaurar(self):
        if self.img_orig is None: return
        self.img_in, self.img_out = self.img_orig.copy(), None
        self._draw(self.lbl_in, self.img_in)
        self.lbl_out.config(image="", text="Esperando operación...")
        self.status.config(text="Imagen original restaurada.")

    def guardar(self):
        if self.img_out is None: return messagebox.showwarning("Aviso", "No hay imagen para guardar.")
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("BMP", "*.bmp")])
        if path: Image.fromarray(self.img_out).save(path); self.status.config(text=f"Guardado en {path}")

    def _draw(self, lbl, arr):
        im = Image.fromarray(arr).convert("L")
        im.thumbnail((480, 480), Image.Resampling.LANCZOS)
        foto = ImageTk.PhotoImage(im)
        lbl.config(image=foto, text="")
        lbl.foto = foto

def main():
    root = tk.Tk()
    AppMorfologia(root)
    root.mainloop()

if __name__ == "__main__": main()
