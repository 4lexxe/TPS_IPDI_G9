# -*- coding: utf-8 -*-
"""
TP 4 - Procesamiento por Convolucion
Asignatura: Procesamiento Digital de Imagenes (PDI)
Facultad de Ingenieria - Universidad Nacional de Jujuy (UNJu)

Integrantes:
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

Objetivos:
- Abrir y visualizar una imagen en nivel de gris (luminancia Y del espacio YIQ).
- Aplicar filtros de paso bajos: Plano y Bartlett 3x3/5x5/7x7, Gaussiano 5x5/7x7.
- Aplicar detectores de bordes: Laplaciano v4/v8, Sobel 8 orientaciones.
- Aplicar filtros de paso altos (fc=0.2 y fc=0.4) y paso banda (5x5).
- Manejo de bordes por repeticion de filas/columnas extremas.
"""

import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from PIL import Image, ImageTk

# Importar el modulo de operaciones de PDI de TP4
try:
    from TP4 import utils as pdi
except ImportError:
    import utils as pdi


# ==============================================================================
# DESCRIPCION DE FILTROS (texto informativo para el panel HUD)
# ==============================================================================

FILTRO_INFO = {
    "Sin procesamiento": (
        "Sin filtro",
        "Copia directa. La luminancia Y no es alterada."
    ),
    "Plano 3x3": (
        "Paso Bajos — Plano 3x3",
        "Box filter 3x3. Promedio uniforme de 9 pixeles.\n"
        "Todos los coeficientes = 1/9. Suavizado leve."
    ),
    "Plano 5x5": (
        "Paso Bajos — Plano 5x5",
        "Box filter 5x5. Promedio uniforme de 25 pixeles.\n"
        "Coeficientes = 1/25. Suavizado moderado."
    ),
    "Plano 7x7": (
        "Paso Bajos — Plano 7x7",
        "Box filter 7x7. Promedio uniforme de 49 pixeles.\n"
        "Coeficientes = 1/49. Suavizado fuerte."
    ),
    "Bartlett 3x3": (
        "Paso Bajos — Bartlett 3x3",
        "Filtro triangular separable 3x3.\n"
        "Pesos: [1 2 1] (R) x [1 2 1] (C) / 16.\n"
        "Suavizado con menos artefactos que Plano."
    ),
    "Bartlett 5x5": (
        "Paso Bajos — Bartlett 5x5",
        "Filtro triangular separable 5x5.\n"
        "Pesos: [1 2 3 2 1] (R) x [1 2 3 2 1] (C) / 81.\n"
        "Suavizado moderado con transicion suave."
    ),
    "Bartlett 7x7": (
        "Paso Bajos — Bartlett 7x7",
        "Filtro triangular separable 7x7.\n"
        "Pesos: [1 2 3 4 3 2 1] (R) x ... / 256.\n"
        "Suavizado fuerte con ringing minimo."
    ),
    "Gaussiano 5x5": (
        "Paso Bajos — Gaussiano 5x5",
        "Kernel Gaussiano 5x5 con sigma=(5-1)/6~0.67.\n"
        "Suavizado isotropico optimo. Sin ringing."
    ),
    "Gaussiano 7x7": (
        "Paso Bajos — Gaussiano 7x7",
        "Kernel Gaussiano 7x7 con sigma=(7-1)/6=1.0.\n"
        "Suavizado isotropico fuerte. Respuesta plana."
    ),
    "Laplaciano v4": (
        "Deteccion de Bordes — Laplaciano v4",
        "Laplaciano 4-conexo: [0 1 0 / 1 -4 1 / 0 1 0].\n"
        "Detecta bordes en las 4 direcciones cardinales.\n"
        "Resultado se muestra con sesgo +0.5 para visualizar."
    ),
    "Laplaciano v8": (
        "Deteccion de Bordes — Laplaciano v8",
        "Laplaciano 8-conexo: [1 1 1 / 1 -8 1 / 1 1 1].\n"
        "Detecta bordes incluyendo diagonales.\n"
        "Resultado se muestra con sesgo +0.5 para visualizar."
    ),
    "Sobel E":  ("Sobel — Direccion Este",      "Gradiente horizontal, bordes verticales."),
    "Sobel NE": ("Sobel — Direccion Noreste",   "Gradiente diagonal NE-SW."),
    "Sobel N":  ("Sobel — Direccion Norte",     "Gradiente vertical, bordes horizontales."),
    "Sobel NW": ("Sobel — Direccion Noroeste",  "Gradiente diagonal NW-SE."),
    "Sobel W":  ("Sobel — Direccion Oeste",     "Gradiente horizontal inverso."),
    "Sobel SW": ("Sobel — Direccion Suroeste",  "Gradiente diagonal SW-NE."),
    "Sobel S":  ("Sobel — Direccion Sur",       "Gradiente vertical inverso."),
    "Sobel SE": ("Sobel — Direccion Sureste",   "Gradiente diagonal SE-NW."),
    "Pasaaltos 0.2": (
        "Paso Altos — fc = 0.2",
        "HP = Impulso - Gaussiano(sigma grande).\n"
        "Frecuencia de corte 0.2 de Nyquist.\n"
        "Realza bordes finos y detalles de alta frecuencia."
    ),
    "Pasaaltos 0.4": (
        "Paso Altos — fc = 0.4",
        "HP = Impulso - Gaussiano(sigma moderado).\n"
        "Frecuencia de corte 0.4 de Nyquist.\n"
        "Realce de bordes menos agresivo que fc=0.2."
    ),
    "Pasabanda 5x5": (
        "Paso Banda — DoG 5x5",
        "Diferencia de Gaussianos (DoG) 5x5.\n"
        "BP = G_narrow - G_wide.\n"
        "Detecta bordes de ancho intermedio (banda media)."
    ),
}


# ==============================================================================
# CLASE PRINCIPAL DE LA APLICACION (HUD MODERNO - ESTILO TP3)
# ==============================================================================

class AppPDI:
    """
    Aplicacion interactiva para filtrado por convolucion sobre la luminancia Y
    del espacio de color YIQ. Interfaz HUD de estilo Dark Slate, consistente
    con la estetica del TP3.
    """

    # Paleta de diseno Dark Slate / Studio (coherente con TP3)
    COLOR_BG           = "#0f172a"
    COLOR_CARD         = "#1e293b"
    COLOR_CARD_BORDER  = "#334155"
    COLOR_CANVAS       = "#090d16"
    COLOR_TEXT         = "#f8fafc"
    COLOR_TEXT_MUTED   = "#94a3b8"

    ACCENT_BLUE    = "#2563eb"
    ACCENT_SLATE   = "#475569"
    ACCENT_EMERALD = "#059669"
    ACCENT_PURPLE  = "#7c3aed"
    ACCENT_INDIGO  = "#4f46e5"
    ACCENT_CYAN    = "#06b6d4"
    ACCENT_AMBER   = "#d97706"
    ACCENT_ROSE    = "#e11d48"
    ACCENT_TEAL    = "#0d9488"

    def __init__(self, ventana: tk.Tk):
        self.ventana = ventana
        self.ventana.title("PDI - TP4: Procesamiento por Convolucion (UNJu)")
        self.ventana.geometry("1280x800")
        self.ventana.minsize(1100, 680)
        self.ventana.configure(bg=self.COLOR_BG)

        # Matrices de imagen normalizadas [0.0, 1.0]
        self.imagen_original  = None
        self.imagen_entrada   = None
        self.imagen_procesada = None

        # Variables de control
        self.operacion = tk.StringVar(value="Sin procesamiento")

        # Construir HUD
        self._configurar_ttk()
        self._crear_interfaz()

    # -----------------------------------------------------------------------
    # ESTILOS TTK
    # -----------------------------------------------------------------------

    def _configurar_ttk(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Dark.TCombobox",
            fieldbackground="#334155",
            background="#1e293b",
            foreground="#f8fafc",
            darkcolor="#1e293b",
            lightcolor="#334155",
            arrowcolor="#38bdf8",
            bordercolor="#475569"
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", "#334155")],
            foreground=[("readonly", "#f8fafc")]
        )

        style.configure("Vertical.TScrollbar",
                        troughcolor="#0f172a",
                        background="#334155",
                        arrowcolor="#94a3b8")

    # -----------------------------------------------------------------------
    # CONSTRUCCION DE LA INTERFAZ
    # -----------------------------------------------------------------------

    def _crear_interfaz(self):
        self._crear_header()
        self._crear_barra_herramientas()

        cuerpo = tk.Frame(self.ventana, bg=self.COLOR_BG)
        cuerpo.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        self._crear_zona_imagenes(cuerpo)
        self._crear_panel_controles(cuerpo)
        self._crear_barra_estado()

    def _crear_header(self):
        header = tk.Frame(self.ventana, bg=self.COLOR_BG)
        header.pack(fill="x", padx=16, pady=(10, 6))

        info = tk.Frame(header, bg=self.COLOR_BG)
        info.pack(side="left")

        titulo_box = tk.Frame(info, bg=self.COLOR_BG)
        titulo_box.pack(anchor="w")

        badge = tk.Label(
            titulo_box, text="PDI \u2022 GRUPO 9",
            font=("Segoe UI", 8, "bold"),
            bg="#1e3a8a", fg="#93c5fd",
            padx=7, pady=2, relief="flat"
        )
        badge.pack(side="left", padx=(0, 8))

        tk.Label(
            titulo_box,
            text="TP 4 \u2014 Procesamiento por Convolucion",
            font=("Segoe UI", 12, "bold"),
            bg=self.COLOR_BG, fg=self.COLOR_TEXT
        ).pack(side="left")

        tk.Label(
            info,
            text="Facultad de Ingenieria (UNJu) \u2022 Procesamiento Digital de Imagenes \u2022 Filtrado Espacial",
            font=("Segoe UI", 8),
            bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            header,
            text="Integrantes: Alex Gabriel Calatayud \u2022 Santiago Balceda \u2022 Robinson Elias Cala",
            font=("Segoe UI", 9),
            bg=self.COLOR_BG, fg=self.COLOR_TEXT_MUTED
        ).pack(side="right", pady=4)

    def _crear_barra_herramientas(self):
        barra = tk.Frame(
            self.ventana,
            bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_CARD_BORDER,
            highlightthickness=1
        )
        barra.pack(fill="x", padx=14, pady=(0, 10))

        cont = tk.Frame(barra, bg=self.COLOR_CARD)
        cont.pack(fill="x", padx=8, pady=6)

        self._boton(cont, "\U0001f4c1 Abrir Imagen",           self._abrir_imagen,              self.ACCENT_BLUE   ).pack(side="left", padx=4)
        self._boton(cont, "\u21ba Restaurar Original",          self._restaurar_original,         self.ACCENT_SLATE  ).pack(side="left", padx=4)
        self._boton(cont, "\u21c4 Usar Resultado como Entrada", self._pasar_resultado_a_entrada,  self.ACCENT_PURPLE ).pack(side="left", padx=4)
        self._boton(cont, "\U0001f4be Guardar Resultado",        self._guardar_resultado,          self.ACCENT_EMERALD).pack(side="left", padx=4)

        self.lbl_pipeline = tk.Label(
            cont,
            text="Pipeline: RGB \u2192 YIQ \u2192 Convolucion sobre Y \u2192 Resultado en gris",
            font=("Segoe UI", 8, "italic"),
            bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED
        )
        self.lbl_pipeline.pack(side="right", padx=10)

    def _crear_zona_imagenes(self, padre):
        zona = tk.Frame(padre, bg=self.COLOR_BG)
        zona.pack(side="left", fill="both", expand=True, padx=(0, 10))

        zona.columnconfigure(0, weight=1)
        zona.columnconfigure(1, weight=1)
        zona.rowconfigure(0, weight=1)

        # ---- Tarjeta ENTRADA ----
        card_e = tk.Frame(
            zona, bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1,
            padx=8, pady=8
        )
        card_e.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        hdr_e = tk.Frame(card_e, bg=self.COLOR_CARD)
        hdr_e.pack(fill="x", pady=(0, 6))

        tk.Label(hdr_e, text="IMAGEN DE ENTRADA",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.COLOR_CARD, fg="#60a5fa").pack(side="left")

        self.lbl_info_entrada = tk.Label(hdr_e, text="Sin imagen",
                                         font=("Segoe UI", 8),
                                         bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED)
        self.lbl_info_entrada.pack(side="right")

        fc_e = tk.Frame(card_e, bg=self.COLOR_CANVAS,
                        highlightbackground="#1e293b", highlightthickness=1)
        fc_e.pack(fill="both", expand=True)

        self.label_entrada = tk.Label(
            fc_e,
            text="Abri una imagen para comenzar\n(JPG, PNG, BMP, WEBP, TIFF)",
            font=("Segoe UI", 10),
            bg=self.COLOR_CANVAS, fg="#64748b"
        )
        self.label_entrada.pack(fill="both", expand=True)

        # ---- Tarjeta RESULTADO ----
        card_r = tk.Frame(
            zona, bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1,
            padx=8, pady=8
        )
        card_r.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        hdr_r = tk.Frame(card_r, bg=self.COLOR_CARD)
        hdr_r.pack(fill="x", pady=(0, 6))

        tk.Label(hdr_r, text="RESULTADO PROCESADO",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.COLOR_CARD, fg="#34d399").pack(side="left")

        self.lbl_info_resultado = tk.Label(hdr_r, text="Esperando operacion",
                                           font=("Segoe UI", 8),
                                           bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED)
        self.lbl_info_resultado.pack(side="right")

        fc_r = tk.Frame(card_r, bg=self.COLOR_CANVAS,
                        highlightbackground="#1e293b", highlightthickness=1)
        fc_r.pack(fill="both", expand=True)

        self.label_resultado = tk.Label(
            fc_r,
            text="El resultado aparecera aqui\ntras seleccionar y aplicar un filtro",
            font=("Segoe UI", 10),
            bg=self.COLOR_CANVAS, fg="#64748b"
        )
        self.label_resultado.pack(fill="both", expand=True)

        self.label_entrada.bind("<Configure>", self._al_redimensionar)

    def _crear_panel_controles(self, padre):
        cont = tk.Frame(
            padre, bg=self.COLOR_CARD, width=320,
            highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1
        )
        cont.pack(side="right", fill="y")
        cont.pack_propagate(False)

        canvas_hud = tk.Canvas(cont, bg=self.COLOR_CARD, highlightthickness=0)
        scroll     = ttk.Scrollbar(cont, orient="vertical", command=canvas_hud.yview,
                                   style="Vertical.TScrollbar")
        hud = tk.Frame(canvas_hud, bg=self.COLOR_CARD, padx=12, pady=10)
        hud.bind(
            "<Configure>",
            lambda e: canvas_hud.configure(scrollregion=canvas_hud.bbox("all"))
        )
        canvas_hud.create_window((0, 0), window=hud, anchor="nw", width=300)
        canvas_hud.configure(yscrollcommand=scroll.set)
        canvas_hud.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Rueda del raton para scroll
        def _scroll_rueda(e):
            canvas_hud.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas_hud.bind_all("<MouseWheel>", _scroll_rueda)

        # -- Seccion 1: Selector de filtro --
        self._encabezado(hud, "\u26a1 1. FILTRO DE CONVOLUCION")

        # Grupos de opciones agrupadas visualmente
        grupos = [
            ("-- Paso Bajos --", [
                "Plano 3x3", "Plano 5x5", "Plano 7x7",
                "Bartlett 3x3", "Bartlett 5x5", "Bartlett 7x7",
                "Gaussiano 5x5", "Gaussiano 7x7",
            ]),
            ("-- Detectores de Bordes --", [
                "Laplaciano v4", "Laplaciano v8",
                "Sobel E", "Sobel NE", "Sobel N", "Sobel NW",
                "Sobel W", "Sobel SW", "Sobel S", "Sobel SE",
            ]),
            ("-- Paso Altos / Banda --", [
                "Pasaaltos 0.2", "Pasaaltos 0.4",
                "Pasabanda 5x5",
            ]),
        ]
        todas_opciones = ["Sin procesamiento"]
        for _, ops in grupos:
            todas_opciones.extend(ops)

        self.combo_op = ttk.Combobox(
            hud,
            textvariable=self.operacion,
            values=todas_opciones,
            state="readonly",
            style="Dark.TCombobox",
            font=("Segoe UI", 10, "bold")
        )
        self.combo_op.pack(fill="x", pady=(2, 6))
        self.combo_op.bind("<<ComboboxSelected>>", self._al_cambiar_filtro)

        # -- Indicador de categoria del filtro --
        self.lbl_categoria = tk.Label(
            hud, text="",
            font=("Segoe UI", 8, "bold"),
            bg=self.COLOR_CARD, fg=self.ACCENT_CYAN,
            anchor="w"
        )
        self.lbl_categoria.pack(fill="x", pady=(0, 2))

        # -- Descripcion del filtro activo --
        self.lbl_desc = tk.Label(
            hud, text="",
            font=("Segoe UI", 8),
            bg="#0f172a", fg="#38bdf8",
            padx=8, pady=8,
            justify="left", wraplength=278,
            relief="flat"
        )
        self.lbl_desc.pack(fill="x", pady=(0, 10))

        # -- Visualizacion grafica del kernel --
        self._encabezado(hud, "\U0001f9ee 2. KERNEL ACTIVO")

        self.canvas_kernel = tk.Canvas(
            hud, width=286, height=130,
            bg="#090d16",
            highlightbackground="#334155", highlightthickness=1
        )
        self.canvas_kernel.pack(pady=(0, 10))

        # -- Seccion 3: Aplicar --
        self._encabezado(hud, "\U0001f680 3. PROCESAMIENTO")

        self._boton(
            hud, "\u26a1 APLICAR FILTRO",
            self._aplicar_operacion,
            self.ACCENT_INDIGO,
            font=("Segoe UI", 10, "bold"), pady=8
        ).pack(fill="x", pady=(4, 12))

        # -- Seccion 4: Info del kernel (coeficientes) --
        self._encabezado(hud, "\U0001f4ca 4. COEFICIENTES DEL KERNEL")

        self.txt_kernel = tk.Text(
            hud,
            height=7, width=32,
            font=("Consolas", 8),
            bg="#0f172a", fg="#a5f3fc",
            relief="flat", state="disabled",
            wrap="none",
            insertbackground="white"
        )
        self.txt_kernel.pack(fill="x", pady=(0, 10))

        # Inicializar visualizaciones
        self._actualizar_info_filtro()

    def _crear_barra_estado(self):
        barra = tk.Frame(
            self.ventana, bg="#0b0f19", height=28,
            highlightbackground="#1e293b", highlightthickness=1
        )
        barra.pack(side="bottom", fill="x")

        self.lbl_estado = tk.Label(
            barra,
            text="Listo. Abra una imagen para comenzar.",
            anchor="w", font=("Segoe UI", 8),
            bg="#0b0f19", fg="#94a3b8",
            padx=12, pady=4
        )
        self.lbl_estado.pack(side="left", fill="x", expand=True)

        self.lbl_tiempo = tk.Label(
            barra, text="\u0394t: 0.00 ms",
            anchor="e", font=("Segoe UI", 8, "bold"),
            bg="#0b0f19", fg="#38bdf8",
            padx=12, pady=4
        )
        self.lbl_tiempo.pack(side="right")

    # -----------------------------------------------------------------------
    # COMPONENTES REUTILIZABLES
    # -----------------------------------------------------------------------

    def _encabezado(self, padre, texto: str):
        lbl = tk.Label(
            padre, text=texto,
            font=("Segoe UI", 8, "bold"),
            bg=self.COLOR_CARD, fg="#94a3b8",
            anchor="w"
        )
        lbl.pack(fill="x", pady=(10, 4))
        return lbl

    def _boton(self, padre, texto: str, comando,
               bg: str, fg: str = "white",
               font=("Segoe UI", 9, "bold"), pady: int = 4):
        btn = tk.Button(
            padre, text=texto, command=comando,
            bg=bg, fg=fg,
            activebackground="#1e293b", activeforeground="white",
            font=font, bd=0, relief="flat",
            padx=10, pady=pady, cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.configure(highlightbackground="white", highlightthickness=1))
        btn.bind("<Leave>", lambda e: btn.configure(highlightthickness=0))
        return btn

    # -----------------------------------------------------------------------
    # VISUALIZACION DEL KERNEL EN CANVAS
    # -----------------------------------------------------------------------

    def _dibujar_kernel(self, kernel: np.ndarray):
        """Dibuja una representacion visual del kernel como grilla con colores."""
        c = self.canvas_kernel
        c.delete("all")
        W, H = 286, 130

        if kernel is None:
            c.create_text(W // 2, H // 2,
                          text="Sin kernel",
                          fill="#64748b", font=("Segoe UI", 9))
            return

        rows, cols = kernel.shape
        cw = W / cols
        ch = H / rows

        vmax = np.abs(kernel).max() if np.abs(kernel).max() > 0 else 1.0

        for r in range(rows):
            for col_i in range(cols):
                val = kernel[r, col_i]
                norm = val / vmax  # [-1, 1]

                if norm >= 0:
                    # Positivos: azul (0..255)
                    intensity = int(norm * 220)
                    color = f"#{intensity:02x}{intensity // 2:02x}ff"
                else:
                    # Negativos: rosa/rojo
                    intensity = int(-norm * 220)
                    color = f"#ff{intensity // 4:02x}{intensity // 4:02x}"

                x0 = col_i * cw + 1
                y0 = r * ch + 1
                x1 = (col_i + 1) * cw - 1
                y1 = (r + 1) * ch - 1

                c.create_rectangle(x0, y0, x1, y1, fill=color, outline="#1e293b")

                # Valor numerico
                if rows <= 7:
                    txt = f"{val:.3f}" if abs(val) < 1 else f"{val:.1f}"
                    c.create_text(
                        (x0 + x1) / 2, (y0 + y1) / 2,
                        text=txt,
                        fill="white" if abs(norm) > 0.3 else "#94a3b8",
                        font=("Segoe UI", 6 if rows > 5 else 7)
                    )

    def _mostrar_coeficientes(self, kernel: np.ndarray):
        """Muestra los coeficientes del kernel en el widget Text."""
        self.txt_kernel.config(state="normal")
        self.txt_kernel.delete("1.0", "end")
        if kernel is None:
            self.txt_kernel.insert("end", "--- Sin kernel ---")
        else:
            lines = []
            for row in kernel:
                parts = " ".join(f"{v:+.4f}" for v in row)
                lines.append(f"[ {parts} ]")
            self.txt_kernel.insert("end", "\n".join(lines))
        self.txt_kernel.config(state="disabled")

    def _obtener_kernel_actual(self):
        """Retorna el kernel numpy correspondiente a la operacion seleccionada."""
        op = self.operacion.get()
        if op == "Sin procesamiento":
            return None
        elif op == "Plano 3x3":      return pdi.flat_kernel(3)
        elif op == "Plano 5x5":      return pdi.flat_kernel(5)
        elif op == "Plano 7x7":      return pdi.flat_kernel(7)
        elif op == "Bartlett 3x3":   return pdi.bartlett_kernel(3)
        elif op == "Bartlett 5x5":   return pdi.bartlett_kernel(5)
        elif op == "Bartlett 7x7":   return pdi.bartlett_kernel(7)
        elif op == "Gaussiano 5x5":  return pdi.gaussian_kernel(5)
        elif op == "Gaussiano 7x7":  return pdi.gaussian_kernel(7)
        elif op == "Laplaciano v4":  return pdi.laplacian_kernel_v4()
        elif op == "Laplaciano v8":  return pdi.laplacian_kernel_v8()
        elif op.startswith("Sobel "):
            return pdi.sobel_kernel(op.split()[1])
        elif op == "Pasaaltos 0.2":  return pdi.high_pass_kernel(0.2)
        elif op == "Pasaaltos 0.4":  return pdi.high_pass_kernel(0.4)
        elif op == "Pasabanda 5x5":  return pdi.band_pass_kernel(5)
        return None

    def _actualizar_info_filtro(self):
        """Actualiza descripcion, kernel canvas y coeficientes segun el filtro activo."""
        op = self.operacion.get()
        info = FILTRO_INFO.get(op, (op, ""))
        titulo, desc = info

        self.lbl_categoria.config(text=titulo)
        self.lbl_desc.config(text=desc)

        kernel = self._obtener_kernel_actual()
        self._dibujar_kernel(kernel)
        self._mostrar_coeficientes(kernel)

    # -----------------------------------------------------------------------
    # EVENTOS
    # -----------------------------------------------------------------------

    def _al_cambiar_filtro(self, event=None):
        self._actualizar_info_filtro()

    def _al_redimensionar(self, event=None):
        if self.imagen_entrada is not None:
            self._mostrar_imagen(self.imagen_entrada, self.label_entrada)
        if self.imagen_procesada is not None:
            self._mostrar_imagen(self.imagen_procesada, self.label_resultado)

    # -----------------------------------------------------------------------
    # LOGICA DE IMAGENES
    # -----------------------------------------------------------------------

    def _abrir_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.bmp *.webp *.tif *.tiff")]
        )
        if not ruta:
            return

        imagen_pil = Image.open(ruta).convert("RGB")
        image = np.array(imagen_pil) / 255.0

        self.imagen_original  = image.astype(np.float32)
        self.imagen_entrada   = self.imagen_original.copy()
        self.imagen_procesada = self.imagen_original.copy()

        h, w = image.shape[:2]
        self.lbl_info_entrada.config(text=f"{w} x {h} px")
        self.lbl_info_resultado.config(text="Esperando operacion")

        self._mostrar_imagen(self.imagen_entrada, self.label_entrada)
        self._mostrar_imagen(self.imagen_procesada, self.label_resultado)
        self.lbl_estado.config(text=f"Imagen cargada: {ruta.split('/')[-1]}  ({w}x{h} px)")

    def _aplicar_operacion(self):
        if self.imagen_entrada is None:
            messagebox.showwarning("Atencion", "Primero abri una imagen.")
            return

        op = self.operacion.get()
        image = self.imagen_entrada

        t0 = time.perf_counter()

        if op == "Sin procesamiento":
            result = image.copy()

        else:
            # Extraer luminancia Y del espacio YIQ
            yiq       = pdi.rgb_to_yiq(image)
            luminance = yiq[:, :, 0]

            kernel = self._obtener_kernel_actual()

            if kernel is None:
                result = image.copy()
            else:
                filtered = pdi.apply_filter(luminance, kernel)

                # Detectores de bordes: centrar en 0.5 para visualizacion
                es_borde = (
                    op.startswith("Laplaciano") or
                    op.startswith("Sobel") or
                    op.startswith("Pasaaltos") or
                    op == "Pasabanda 5x5"
                )
                if es_borde:
                    filtered = np.clip(filtered + 0.5, 0.0, 1.0)
                else:
                    filtered = np.clip(filtered, 0.0, 1.0)

                result = np.stack([filtered, filtered, filtered], axis=2)

        dt_ms = (time.perf_counter() - t0) * 1000

        self.imagen_procesada = result
        self._mostrar_imagen(self.imagen_procesada, self.label_resultado)

        h, w = result.shape[:2]
        self.lbl_info_resultado.config(text=f"{w} x {h} px")
        self.lbl_estado.config(text=f"Filtro aplicado: {op}")
        self.lbl_tiempo.config(text=f"\u0394t: {dt_ms:.1f} ms")

    def _mostrar_imagen(self, array_img: np.ndarray, label: tk.Label):
        """Renderiza un array [H,W,3] float[0,1] en el label destino."""
        img_uint8 = (np.clip(array_img, 0, 1) * 255).astype(np.uint8)
        img_pil   = Image.fromarray(img_uint8)

        w = label.winfo_width()
        h = label.winfo_height()
        if w > 10 and h > 10:
            img_pil.thumbnail((w - 4, h - 4), Image.LANCZOS)
        else:
            img_pil.thumbnail((400, 520), Image.LANCZOS)

        foto = ImageTk.PhotoImage(img_pil)
        label.foto = foto
        label.config(image=foto, text="")

    def _pasar_resultado_a_entrada(self):
        if self.imagen_procesada is None:
            messagebox.showwarning("Atencion", "Primero abri una imagen.")
            return
        self.imagen_entrada = self.imagen_procesada.copy()
        h, w = self.imagen_entrada.shape[:2]
        self.lbl_info_entrada.config(text=f"{w} x {h} px")
        self._mostrar_imagen(self.imagen_entrada, self.label_entrada)
        self.lbl_estado.config(text="La imagen resultado paso a la entrada.")

    def _restaurar_original(self):
        if self.imagen_original is None:
            return
        self.imagen_entrada   = self.imagen_original.copy()
        self.imagen_procesada = self.imagen_original.copy()
        h, w = self.imagen_original.shape[:2]
        self.lbl_info_entrada.config(text=f"{w} x {h} px")
        self.lbl_info_resultado.config(text="Esperando operacion")
        self._mostrar_imagen(self.imagen_entrada, self.label_entrada)
        self._mostrar_imagen(self.imagen_procesada, self.label_resultado)
        self.lbl_estado.config(text="Imagen original restaurada.")

    def _guardar_resultado(self):
        if self.imagen_procesada is None:
            messagebox.showwarning("Atencion", "Primero abri una imagen.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar imagen procesada",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        if not ruta:
            return
        img_uint8 = (np.clip(self.imagen_procesada, 0, 1) * 255).astype(np.uint8)
        Image.fromarray(img_uint8).save(ruta)
        self.lbl_estado.config(text=f"Imagen guardada: {ruta.split('/')[-1]}")


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================

def main():
    ventana = tk.Tk()
    app = AppPDI(ventana)  # noqa: F841
    ventana.mainloop()


if __name__ == "__main__":
    main()
