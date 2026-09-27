# -*- coding: utf-8 -*-
"""
TP 3 - Operaciones de Luminancia en Espacio YIQ
Asignatura: Procesamiento Digital de Imágenes (PDI)
Facultad de Ingeniería - Universidad Nacional de Jujuy (UNJu)

Integrantes:
- Alex Gabriel Calatayud
- Santiago Balceda
- Robinson Elias Cala

Objetivos:
- Abrir y visualizar imágenes normalizadas.
- Conversión bidireccional RGB <-> YIQ.
- Manipulación de la componente de luminancia Y manteniendo crominancias (I, Q) inalteradas.
- Filtro Raíz Cuadrada (aclarado no lineal de sombras).
- Filtro Cuadrático (oscurecimiento no lineal / realce de altas luces).
- Filtro Lineal a Trozos (expansión y compresión del rango dinámico entre Y_min e Y_max).
- Análisis visual de la función de transferencia y del histograma de luminancia (32 bins, [0, 1]).
"""

import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

# Importar el módulo de operaciones de PDI
try:
    from TP3 import utils as pdi
except ImportError:
    import utils as pdi


# ==============================================================================
# CLASE PRINCIPAL DE LA APLICACIÓN (HUD MODERNO)
# ==============================================================================

class AppPDI:
    """
    Controlador y Vista de la aplicación interactiva para operaciones
    de luminancia en el espacio YIQ con HUD moderno de estilo Dark Slate.
    """

    # Paleta de diseño Dark Slate / Studio
    COLOR_BG = "#0f172a"          # Slate 900 profundo (Fondo general)
    COLOR_CARD = "#1e293b"        # Slate 800 (Fondo tarjetas y paneles)
    COLOR_CARD_BORDER = "#334155" # Slate 700 (Bordes y separadores)
    COLOR_CANVAS = "#090d16"      # Negro carbón (Fondo visores de imagen)
    COLOR_TEXT = "#f8fafc"        # Blanco grisáceo (Texto principal)
    COLOR_TEXT_MUTED = "#94a3b8"  # Slate 400 (Texto secundario / hints)
    
    # Acentos
    ACCENT_BLUE = "#2563eb"       # Azul primario (Abrir)
    ACCENT_SLATE = "#475569"      # Slate (Restaurar)
    ACCENT_EMERALD = "#059669"    # Esmeralda (Guardar)
    ACCENT_PURPLE = "#7c3aed"     # Violeta (Usar resultado como entrada)
    ACCENT_INDIGO = "#4f46e5"     # Índigo vibrante (Aplicar filtro)
    ACCENT_CYAN = "#06b6d4"       # Cyan (Curvas y destacados)
    ACCENT_AMBER = "#d97706"      # Ámbar (Alertas e información)

    def __init__(self, ventana: tk.Tk):
        self.ventana = ventana
        self.ventana.title("PDI - TP3: Operaciones de Luminancia en Espacio YIQ (UNJu)")
        self.ventana.geometry("1240x780")
        self.ventana.minsize(1050, 680)
        self.ventana.configure(bg=self.COLOR_BG)

        # Matrices de imágenes normalizadas [0.0, 1.0] en float32
        self.imagen_original = None
        self.imagen_entrada = None
        self.imagen_procesada = None

        # Variables de control
        self.operacion = tk.StringVar(value="Lineal a trozos")
        self.y_min = tk.StringVar(value="0.20")
        self.y_max = tk.StringVar(value="0.80")
        self.histograma_de = tk.StringVar(value="Comparativo")
        self.auto_preview = tk.BooleanVar(value=True)

        # Construir HUD
        self.configurar_estilos_ttk()
        self.crear_interfaz()
        self.actualizar_curva_transferencia()
        self.actualizar_descripcion_filtro()


    def configurar_estilos_ttk(self):
        """Configuración de estilos TTK para integrarse al tema oscuro."""
        style = ttk.Style()
        style.theme_use("clam")

        # Combobox
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

        # Checkbutton
        style.configure(
            "Dark.TCheckbutton",
            background=self.COLOR_CARD,
            foreground=self.COLOR_TEXT,
            font=("Segoe UI", 9)
        )
        style.map(
            "Dark.TCheckbutton",
            background=[("active", self.COLOR_CARD)],
            foreground=[("active", self.ACCENT_CYAN)]
        )


    # ==========================================================================
    # CONSTRUCCIÓN DE LA INTERFAZ (HUD)
    # ==========================================================================

    def crear_interfaz(self):
        """Genera la estructura visual completa del HUD."""

        # 1. HEADER SUPERIOR
        self.crear_header()

        # 2. BARRA DE ACCIONES RÁPIDAS
        self.crear_barra_herramientas()

        # 3. CONTENEDOR PRINCIPAL (VISORES + PANEL DERECHO)
        cuerpo = tk.Frame(self.ventana, bg=self.COLOR_BG)
        cuerpo.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        # 3.1. ZONA DE IMÁGENES (DUAL VIEWPORT)
        self.crear_zona_imagenes(cuerpo)

        # 3.2. PANEL LATERAL DERECHO (INSPECTOR DE CONTROLES)
        self.crear_panel_controles(cuerpo)

        # 4. BARRA DE ESTADO INFERIOR
        self.crear_barra_estado()


    def crear_header(self):
        """Barra superior de marca institucional y créditos del equipo."""
        header = tk.Frame(self.ventana, bg=self.COLOR_BG)
        header.pack(fill="x", padx=16, pady=(10, 6))

        # Título y Subtítulo
        info_frame = tk.Frame(header, bg=self.COLOR_BG)
        info_frame.pack(side="left")

        titulo_box = tk.Frame(info_frame, bg=self.COLOR_BG)
        titulo_box.pack(anchor="w")

        lbl_badge = tk.Label(
            titulo_box,
            text="PDI • GRUPO 9",
            font=("Segoe UI", 8, "bold"),
            bg="#1e3a8a",
            fg="#93c5fd",
            padx=7,
            pady=2,
            relief="flat"
        )
        lbl_badge.pack(side="left", padx=(0, 8))

        lbl_titulo = tk.Label(
            titulo_box,
            text="TP 3 — Operaciones de Luminancia en Espacio YIQ",
            font=("Segoe UI", 12, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        )
        lbl_titulo.pack(side="left")

        lbl_subtitulo = tk.Label(
            info_frame,
            text="Facultad de Ingeniería (UNJu) • Procesamiento Digital de Imágenes • NTSC YIQ Standard",
            font=("Segoe UI", 8),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED
        )
        lbl_subtitulo.pack(anchor="w", pady=(2, 0))

        # Autores a la derecha
        lbl_autores = tk.Label(
            header,
            text="Integrantes: Alex Gabriel Calatayud • Santiago Balceda • Robinson Elias Cala",
            font=("Segoe UI", 9),
            bg=self.COLOR_BG,
            fg="#94a3b8"
        )
        lbl_autores.pack(side="right", pady=4)


    def crear_barra_herramientas(self):
        """Barra moderna de acciones principales."""
        barra = tk.Frame(self.ventana, bg=self.COLOR_CARD, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1)
        barra.pack(fill="x", padx=14, pady=(0, 10))

        contenedor_botones = tk.Frame(barra, bg=self.COLOR_CARD)
        contenedor_botones.pack(fill="x", padx=8, pady=6)

        # Botón Abrir Imagen
        self.crear_boton(
            contenedor_botones,
            texto="📁 Abrir Imagen",
            comando=self.abrir_imagen,
            bg=self.ACCENT_BLUE,
            fg="white"
        ).pack(side="left", padx=4)

        # Botón Restaurar Original
        self.crear_boton(
            contenedor_botones,
            texto="↺ Restaurar Original",
            comando=self.restaurar_original,
            bg=self.ACCENT_SLATE,
            fg="white"
        ).pack(side="left", padx=4)

        # Botón Pasar Resultado a Entrada (Pipeline)
        self.crear_boton(
            contenedor_botones,
            texto="⇄ Usar Resultado como Entrada",
            comando=self.pasar_resultado_a_entrada,
            bg=self.ACCENT_PURPLE,
            fg="white"
        ).pack(side="left", padx=4)

        # Botón Guardar Resultado
        self.crear_boton(
            contenedor_botones,
            texto="💾 Guardar Resultado",
            comando=self.guardar_resultado,
            bg=self.ACCENT_EMERALD,
            fg="white"
        ).pack(side="left", padx=4)

        # Indicador rápido del pipeline
        self.lbl_pipeline_hint = tk.Label(
            contenedor_botones,
            text="Pipeline: RGB -> YIQ -> Operación sobre Y (I, Q const.) -> RGB",
            font=("Segoe UI", 8, "italic"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_MUTED
        )
        self.lbl_pipeline_hint.pack(side="right", padx=10)


    def crear_zona_imagenes(self, padre):
        """Crea los visores gemelos de Entrada y Resultado con diseño de tarjeta."""
        zona = tk.Frame(padre, bg=self.COLOR_BG)
        zona.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Cuadrícula 1 fila, 2 columnas con peso igual
        zona.columnconfigure(0, weight=1)
        zona.columnconfigure(1, weight=1)
        zona.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # TARJETA 1: IMAGEN DE ENTRADA
        # ----------------------------------------------------
        card_entrada = tk.Frame(
            zona,
            bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=8,
            pady=8
        )
        card_entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Header de tarjeta entrada
        header_e = tk.Frame(card_entrada, bg=self.COLOR_CARD)
        header_e.pack(fill="x", pady=(0, 6))

        tk.Label(
            header_e,
            text="IMAGEN DE ENTRADA",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLOR_CARD,
            fg="#60a5fa"
        ).pack(side="left")

        self.lbl_info_entrada = tk.Label(
            header_e,
            text="Sin imagen",
            font=("Segoe UI", 8),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_MUTED
        )
        self.lbl_info_entrada.pack(side="right")

        # Viewport de entrada
        frame_canvas_e = tk.Frame(card_entrada, bg=self.COLOR_CANVAS, highlightbackground="#1e293b", highlightthickness=1)
        frame_canvas_e.pack(fill="both", expand=True)

        self.label_entrada = tk.Label(
            frame_canvas_e,
            text="Abrí una imagen para comenzar\n(JPG, PNG, BMP, WEBP, TIFF)",
            font=("Segoe UI", 10),
            bg=self.COLOR_CANVAS,
            fg="#64748b"
        )
        self.label_entrada.pack(fill="both", expand=True)

        # ----------------------------------------------------
        # TARJETA 2: RESULTADO PROCESADO
        # ----------------------------------------------------
        card_resultado = tk.Frame(
            zona,
            bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=8,
            pady=8
        )
        card_resultado.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # Header de tarjeta resultado
        header_r = tk.Frame(card_resultado, bg=self.COLOR_CARD)
        header_r.pack(fill="x", pady=(0, 6))

        tk.Label(
            header_r,
            text="RESULTADO PROCESADO",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLOR_CARD,
            fg="#34d399"
        ).pack(side="left")

        self.lbl_info_resultado = tk.Label(
            header_r,
            text="Esperando operación",
            font=("Segoe UI", 8),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_MUTED
        )
        self.lbl_info_resultado.pack(side="right")

        # Viewport de resultado
        frame_canvas_r = tk.Frame(card_resultado, bg=self.COLOR_CANVAS, highlightbackground="#1e293b", highlightthickness=1)
        frame_canvas_r.pack(fill="both", expand=True)

        self.label_resultado = tk.Label(
            frame_canvas_r,
            text="El resultado aparecerá aquí\ntras seleccionar y aplicar un filtro",
            font=("Segoe UI", 10),
            bg=self.COLOR_CANVAS,
            fg="#64748b"
        )
        self.label_resultado.pack(fill="both", expand=True)

        # Detección de redimensionamiento dinámico
        self.label_entrada.bind("<Configure>", self.al_redimensionar_visores)


    def crear_panel_controles(self, padre):
        """Panel lateral derecho (Inspector) con diseño HUD tecnológico."""
        contenedor = tk.Frame(
            padre,
            bg=self.COLOR_CARD,
            width=330,
            highlightbackground=self.COLOR_CARD_BORDER,
            highlightthickness=1
        )
        contenedor.pack(side="right", fill="y")
        contenedor.pack_propagate(False)

        # Scrollable canvas para asegurar visibilidad en cualquier resolución
        canvas_hud = tk.Canvas(contenedor, bg=self.COLOR_CARD, highlightthickness=0)
        scroll_hud = ttk.Scrollbar(contenedor, orient="vertical", command=canvas_hud.yview)
        
        hud = tk.Frame(canvas_hud, bg=self.COLOR_CARD, padx=12, pady=10)
        hud.bind(
            "<Configure>",
            lambda e: canvas_hud.configure(scrollregion=canvas_hud.bbox("all"))
        )
        canvas_hud.create_window((0, 0), window=hud, anchor="nw", width=310)
        canvas_hud.configure(yscrollcommand=scroll_hud.set)

        canvas_hud.pack(side="left", fill="both", expand=True)
        scroll_hud.pack(side="right", fill="y")

        # --- SECCIÓN 1: OPERACIONES DE LUMINANCIA ---
        self.crear_encabezado_seccion(hud, "⚡ 1. FILTRO DE LUMINANCIA (Y)")

        opciones = [
            "Lineal a trozos",
            "Raíz",
            "Cuadrado",
            "Sin procesamiento"
        ]

        combo_op = ttk.Combobox(
            hud,
            textvariable=self.operacion,
            values=opciones,
            state="readonly",
            style="Dark.TCombobox",
            font=("Segoe UI", 10, "bold")
        )
        combo_op.pack(fill="x", pady=(2, 6))
        combo_op.bind("<<ComboboxSelected>>", self.al_cambiar_operacion)

        # Caja de descripción matemática del filtro activo
        self.lbl_desc_filtro = tk.Label(
            hud,
            text="",
            font=("Segoe UI", 8),
            bg="#0f172a",
            fg="#38bdf8",
            padx=8,
            pady=6,
            justify="left",
            wraplength=290,
            relief="flat"
        )
        self.lbl_desc_filtro.pack(fill="x", pady=(0, 10))

        # --- SECCIÓN 2: PARÁMETROS LINEAL A TROZOS ---
        self.frame_parametros = tk.Frame(hud, bg=self.COLOR_CARD)
        self.frame_parametros.pack(fill="x", pady=(0, 8))

        self.crear_encabezado_seccion(self.frame_parametros, "📈 2. CURVA Y PARÁMETROS [Y_min, Y_max]")

        # Gráfico interactivo en vivo de la función de transferencia
        self.canvas_curva = tk.Canvas(
            self.frame_parametros,
            width=286,
            height=130,
            bg="#090d16",
            highlightbackground="#334155",
            highlightthickness=1
        )
        self.canvas_curva.pack(pady=(0, 8))

        # Control Y_min
        f_ymin = tk.Frame(self.frame_parametros, bg=self.COLOR_CARD)
        f_ymin.pack(fill="x", pady=2)

        lbl_ymin_title = tk.Label(f_ymin, text="Y min (Corte inferior):", font=("Segoe UI", 8, "bold"), bg=self.COLOR_CARD, fg="#cbd5e1")
        lbl_ymin_title.pack(side="left")

        self.lbl_ymin_val = tk.Label(f_ymin, text="0.20", font=("Segoe UI", 8, "bold"), bg=self.COLOR_CARD, fg="#38bdf8")
        self.lbl_ymin_val.pack(side="right")

        self.scale_ymin = tk.Scale(
            self.frame_parametros,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            showvalue=0,
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT,
            troughcolor="#090d16",
            activebackground=self.ACCENT_CYAN,
            highlightthickness=0,
            command=self.al_mover_slider_ymin
        )
        self.scale_ymin.set(0.20)
        self.scale_ymin.pack(fill="x", pady=(0, 6))

        # Control Y_max
        f_ymax = tk.Frame(self.frame_parametros, bg=self.COLOR_CARD)
        f_ymax.pack(fill="x", pady=2)

        lbl_ymax_title = tk.Label(f_ymax, text="Y max (Saturación superior):", font=("Segoe UI", 8, "bold"), bg=self.COLOR_CARD, fg="#cbd5e1")
        lbl_ymax_title.pack(side="left")

        self.lbl_ymax_val = tk.Label(f_ymax, text="0.80", font=("Segoe UI", 8, "bold"), bg=self.COLOR_CARD, fg="#38bdf8")
        self.lbl_ymax_val.pack(side="right")

        self.scale_ymax = tk.Scale(
            self.frame_parametros,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            showvalue=0,
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT,
            troughcolor="#090d16",
            activebackground=self.ACCENT_CYAN,
            highlightthickness=0,
            command=self.al_mover_slider_ymax
        )
        self.scale_ymax.set(0.80)
        self.scale_ymax.pack(fill="x", pady=(0, 8))

        # Presets rápidos para Lineal a Trozos
        f_presets = tk.Frame(self.frame_parametros, bg=self.COLOR_CARD)
        f_presets.pack(fill="x", pady=(0, 6))

        tk.Label(f_presets, text="Presets rápidos:", font=("Segoe UI", 8), bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED).pack(anchor="w")

        p_btns = tk.Frame(f_presets, bg=self.COLOR_CARD)
        p_btns.pack(fill="x", pady=2)

        self.crear_boton_mini(p_btns, "Estándar [0.2 - 0.8]", lambda: self.aplicar_preset(0.20, 0.80)).pack(side="left", padx=2, expand=True, fill="x")
        self.crear_boton_mini(p_btns, "Alto Contraste [0.35 - 0.65]", lambda: self.aplicar_preset(0.35, 0.65)).pack(side="left", padx=2, expand=True, fill="x")

        p_btns2 = tk.Frame(f_presets, bg=self.COLOR_CARD)
        p_btns2.pack(fill="x", pady=2)

        self.crear_boton_mini(p_btns2, "Expandir Sombras [0.05 - 0.50]", lambda: self.aplicar_preset(0.05, 0.50)).pack(side="left", padx=2, expand=True, fill="x")
        self.crear_boton_mini(p_btns2, "Expandir Luces [0.50 - 0.95]", lambda: self.aplicar_preset(0.50, 0.95)).pack(side="left", padx=2, expand=True, fill="x")

        # --- SECCIÓN 3: BOTÓN DE EJECUCIÓN ---
        self.crear_encabezado_seccion(hud, "🚀 3. PROCESAMIENTO")

        btn_aplicar = self.crear_boton(
            hud,
            texto="⚡ APLICAR FILTRO",
            comando=self.aplicar_operacion,
            bg=self.ACCENT_INDIGO,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            pady=8
        )
        btn_aplicar.pack(fill="x", pady=(4, 6))

        # Checkbox de vista previa en tiempo real
        chk_preview = ttk.Checkbutton(
            hud,
            text="Aplicación en tiempo real al ajustar",
            variable=self.auto_preview,
            style="Dark.TCheckbutton"
        )
        chk_preview.pack(anchor="w", pady=(0, 10))

        # --- SECCIÓN 4: HISTOGRAMA DE LUMINANCIA ---
        self.crear_encabezado_seccion(hud, "📊 4. HISTOGRAMA DE LUMINANCIA")

        f_hist_opt = tk.Frame(hud, bg=self.COLOR_CARD)
        f_hist_opt.pack(fill="x", pady=2)

        tk.Label(f_hist_opt, text="Origen:", font=("Segoe UI", 8), bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED).pack(side="left", padx=(0, 6))

        combo_hist = ttk.Combobox(
            f_hist_opt,
            textvariable=self.histograma_de,
            values=["Entrada", "Resultado", "Comparativo"],
            state="readonly",
            style="Dark.TCombobox",
            font=("Segoe UI", 9),
            width=14
        )
        combo_hist.pack(side="left", fill="x", expand=True)

        btn_hist = self.crear_boton(
            hud,
            texto="📊 Visualizar Histograma (32 bins)",
            comando=self.mostrar_histograma,
            bg="#334155",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            pady=5
        )
        btn_hist.pack(fill="x", pady=(6, 12))


    def crear_barra_estado(self):
        """Barra de estado en el footer con retroalimentación en vivo."""
        barra = tk.Frame(self.ventana, bg="#0b0f19", height=28, highlightbackground="#1e293b", highlightthickness=1)
        barra.pack(side="bottom", fill="x")

        self.lbl_estado = tk.Label(
            barra,
            text="Listo. Abra una imagen para comenzar el análisis.",
            anchor="w",
            font=("Segoe UI", 8),
            bg="#0b0f19",
            fg="#94a3b8",
            padx=12,
            pady=4
        )
        self.lbl_estado.pack(side="left", fill="x", expand=True)

        self.lbl_tiempo = tk.Label(
            barra,
            text="Δt: 0.00 ms",
            anchor="e",
            font=("Segoe UI", 8, "bold"),
            bg="#0b0f19",
            fg="#38bdf8",
            padx=12,
            pady=4
        )
        self.lbl_tiempo.pack(side="right")


    # ==========================================================================
    # COMPONENTES GRÁFICOS REUTILIZABLES
    # ==========================================================================

    def crear_encabezado_seccion(self, padre, texto):
        lbl = tk.Label(
            padre,
            text=texto,
            font=("Segoe UI", 8, "bold"),
            bg=self.COLOR_CARD,
            fg="#94a3b8",
            anchor="w"
        )
        lbl.pack(fill="x", pady=(10, 4))
        return lbl


    def crear_boton(self, padre, texto, comando, bg, fg="white", font=("Segoe UI", 9, "bold"), pady=4):
        btn = tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=bg,
            fg=fg,
            activebackground="#1e293b",
            activeforeground="white",
            font=font,
            bd=0,
            relief="flat",
            padx=10,
            pady=pady,
            cursor="hand2"
        )
        # Efecto hover sutil
        btn.bind("<Enter>", lambda e: btn.configure(highlightbackground="white", highlightthickness=1))
        btn.bind("<Leave>", lambda e: btn.configure(highlightthickness=0))
        return btn


    def crear_boton_mini(self, padre, texto, comando):
        btn = tk.Button(
            padre,
            text=texto,
            command=comando,
            bg="#334155",
            fg="#e2e8f0",
            activebackground=self.ACCENT_CYAN,
            activeforeground="#090d16",
            font=("Segoe UI", 7, "bold"),
            bd=0,
            relief="flat",
            padx=4,
            pady=3,
            cursor="hand2"
        )
        return btn


    # ==========================================================================
    # DIBUJO EN VIVO DE LA FUNCIÓN DE TRANSFERENCIA T(Y)
    # ==========================================================================

    def actualizar_curva_transferencia(self):
        """
        Dibuja en tiempo real sobre el Canvas la función de transferencia de luminancia
        T(Y) correspondiente al filtro seleccionado y a los umbrales Y_min e Y_max.
        """
        self.canvas_curva.delete("all")
        w = 286
        h = 130
        margin_l = 30
        margin_r = 15
        margin_t = 12
        margin_b = 24

        plot_w = w - margin_l - margin_r
        plot_h = h - margin_t - margin_b

        # Coordenadas a canvas
        def to_canvas(x, y):
            cx = margin_l + x * plot_w
            cy = margin_t + (1.0 - y) * plot_h
            return cx, cy

        # 1. Grilla y ejes de referencia
        for val in [0.0, 0.25, 0.5, 0.75, 1.0]:
            # Línea vertical
            cx, _ = to_canvas(val, 0.0)
            self.canvas_curva.create_line(cx, margin_t, cx, margin_t + plot_h, fill="#1e293b", dash=(2, 2))
            # Línea horizontal
            _, cy = to_canvas(0.0, val)
            self.canvas_curva.create_line(margin_l, cy, margin_l + plot_w, cy, fill="#1e293b", dash=(2, 2))

        # Eje de identidad Y' = Y (diagonal gris tenue)
        p0 = to_canvas(0.0, 0.0)
        p1 = to_canvas(1.0, 1.0)
        self.canvas_curva.create_line(p0[0], p0[1], p1[0], p1[1], fill="#334155", dash=(4, 3))

        # Etiquetas de ejes
        self.canvas_curva.create_text(margin_l - 6, to_canvas(0.0, 1.0)[1], text="1", fill="#64748b", font=("Segoe UI", 7), anchor="e")
        self.canvas_curva.create_text(margin_l - 6, to_canvas(0.0, 0.0)[1], text="0", fill="#64748b", font=("Segoe UI", 7), anchor="e")
        self.canvas_curva.create_text(to_canvas(0.0, 0.0)[0], h - 10, text="0", fill="#64748b", font=("Segoe UI", 7), anchor="n")
        self.canvas_curva.create_text(to_canvas(1.0, 0.0)[0], h - 10, text="1", fill="#64748b", font=("Segoe UI", 7), anchor="n")
        self.canvas_curva.create_text(w // 2, h - 8, text="Y entrada", fill="#64748b", font=("Segoe UI", 7), anchor="n")
        self.canvas_curva.create_text(10, h // 2, text="Y'", fill="#64748b", font=("Segoe UI", 7, "bold"), anchor="w")

        # 2. Dibujar la curva activa según el filtro
        op = self.operacion.get()

        if op == "Sin procesamiento":
            self.canvas_curva.create_line(p0[0], p0[1], p1[0], p1[1], fill="#10b981", width=2)
            self.canvas_curva.create_text(w // 2, margin_t + 10, text="T(Y) = Y", fill="#10b981", font=("Segoe UI", 8, "bold"))

        elif op == "Raíz":
            puntos = []
            for xi in np.linspace(0.0, 1.0, 40):
                yi = np.sqrt(xi)
                puntos.extend(to_canvas(xi, yi))
            self.canvas_curva.create_line(puntos, fill="#38bdf8", width=2, smooth=True)
            self.canvas_curva.create_text(w // 2, margin_t + 10, text="T(Y) = √Y (Aclara)", fill="#38bdf8", font=("Segoe UI", 8, "bold"))

        elif op == "Cuadrado":
            puntos = []
            for xi in np.linspace(0.0, 1.0, 40):
                yi = xi ** 2
                puntos.extend(to_canvas(xi, yi))
            self.canvas_curva.create_line(puntos, fill="#f59e0b", width=2, smooth=True)
            self.canvas_curva.create_text(w // 2, margin_t + 10, text="T(Y) = Y² (Oscurece)", fill="#f59e0b", font=("Segoe UI", 8, "bold"))

        elif op == "Lineal a trozos":
            try:
                ymin = float(self.y_min.get())
                ymax = float(self.y_max.get())
            except ValueError:
                ymin, ymax = 0.20, 0.80

            # Líneas guía de corte vertical
            cx_min, _ = to_canvas(ymin, 0.0)
            cx_max, _ = to_canvas(ymax, 1.0)
            self.canvas_curva.create_line(cx_min, margin_t, cx_min, margin_t + plot_h, fill="#ef4444", dash=(3, 2))
            self.canvas_curva.create_line(cx_max, margin_t, cx_max, margin_t + plot_h, fill="#10b981", dash=(3, 2))

            # Segmentos a trozos
            pt0 = to_canvas(0.0, 0.0)
            pt_min = to_canvas(ymin, 0.0)
            pt_max = to_canvas(ymax, 1.0)
            pt1 = to_canvas(1.0, 1.0)

            # Tramo 1: [0, ymin] -> 0
            self.canvas_curva.create_line(pt0[0], pt0[1], pt_min[0], pt_min[1], fill="#06b6d4", width=3)
            # Tramo 2: [ymin, ymax] -> lineal [0, 1]
            self.canvas_curva.create_line(pt_min[0], pt_min[1], pt_max[0], pt_max[1], fill="#a855f7", width=3)
            # Tramo 3: [ymax, 1] -> 1
            self.canvas_curva.create_line(pt_max[0], pt_max[1], pt1[0], pt1[1], fill="#06b6d4", width=3)

            # Puntos clave con circulitos
            r = 3
            self.canvas_curva.create_oval(pt_min[0]-r, pt_min[1]-r, pt_min[0]+r, pt_min[1]+r, fill="#ef4444", outline="white")
            self.canvas_curva.create_oval(pt_max[0]-r, pt_max[1]-r, pt_max[0]+r, pt_max[1]+r, fill="#10b981", outline="white")

            # Indicadores de texto
            self.canvas_curva.create_text(cx_min, margin_t - 2, text=f"min:{ymin:.2f}", fill="#ef4444", font=("Segoe UI", 7, "bold"), anchor="s")
            self.canvas_curva.create_text(cx_max, margin_t - 2, text=f"max:{ymax:.2f}", fill="#10b981", font=("Segoe UI", 7, "bold"), anchor="s")


    def actualizar_descripcion_filtro(self):
        """Actualiza el texto descriptivo del filtro activo."""
        op = self.operacion.get()
        if op == "Sin procesamiento":
            desc = "• Sin filtro: Copia directa sin alterar luminancia Y ni crominancias I, Q."
        elif op == "Raíz":
            desc = "• Raíz Cuadrada (Y' = √Y):\nExpande el rango dinámico de las sombras y medios tonos oscuros, incrementando el brillo global de la escena de forma suave y no lineal."
        elif op == "Cuadrado":
            desc = "• Cuadrado (Y' = Y²):\nComprime las zonas medias y oscuras, acentuando el contraste hacia las altas luces y reduciendo el brillo general."
        elif op == "Lineal a trozos":
            desc = "• Transformación Lineal a Trozos:\nSatura a 0 los valores inferiores a Y_min y a 1 los superiores a Y_max, expandiendo linealmente el contraste del intervalo [Y_min, Y_max]."
        else:
            desc = ""
        self.lbl_desc_filtro.config(text=desc)


    # ==========================================================================
    # MANEJO DE EVENTOS Y CONTROLES DEL HUD
    # ==========================================================================

    def al_cambiar_operacion(self, event=None):
        """Evento de selección de filtro en el combobox."""
        op = self.operacion.get()
        self.actualizar_descripcion_filtro()
        self.actualizar_curva_transferencia()

        if self.auto_preview.get() and self.imagen_entrada is not None:
            self.aplicar_operacion()


    def al_mover_slider_ymin(self, val):
        """Maneja el slider de Y_min garantizando coherencia con Y_max."""
        ymin = float(val)
        ymax = float(self.scale_ymax.get())
        if ymin >= ymax:
            ymin = max(0.0, ymax - 0.02)
            self.scale_ymin.set(ymin)

        self.y_min.set(f"{ymin:.2f}")
        self.lbl_ymin_val.config(text=f"{ymin:.2f}")
        self.actualizar_curva_transferencia()

        if self.auto_preview.get() and self.imagen_entrada is not None and self.operacion.get() == "Lineal a trozos":
            self.aplicar_operacion()


    def al_mover_slider_ymax(self, val):
        """Maneja el slider de Y_max garantizando coherencia con Y_min."""
        ymax = float(val)
        ymin = float(self.scale_ymin.get())
        if ymax <= ymin:
            ymax = min(1.0, ymin + 0.02)
            self.scale_ymax.set(ymax)

        self.y_max.set(f"{ymax:.2f}")
        self.lbl_ymax_val.config(text=f"{ymax:.2f}")
        self.actualizar_curva_transferencia()

        if self.auto_preview.get() and self.imagen_entrada is not None and self.operacion.get() == "Lineal a trozos":
            self.aplicar_operacion()


    def aplicar_preset(self, ymin, ymax):
        """Aplica un preset numérico a los sliders y actualiza."""
        self.scale_ymin.set(ymin)
        self.scale_ymax.set(ymax)
        self.y_min.set(f"{ymin:.2f}")
        self.y_max.set(f"{ymax:.2f}")
        self.lbl_ymin_val.config(text=f"{ymin:.2f}")
        self.lbl_ymax_val.config(text=f"{ymax:.2f}")
        self.operacion.set("Lineal a trozos")
        self.actualizar_descripcion_filtro()
        self.actualizar_curva_transferencia()

        if self.auto_preview.get() and self.imagen_entrada is not None:
            self.aplicar_operacion()


    def al_redimensionar_visores(self, event=None):
        """Ajusta proporcionalmente las imágenes si cambia el tamaño de ventana."""
        if self.imagen_entrada is not None:
            self.mostrar_imagen(self.imagen_entrada, self.label_entrada)
        if self.imagen_procesada is not None:
            self.mostrar_imagen(self.imagen_procesada, self.label_resultado)


    # ==========================================================================
    # GESTIÓN DE ARCHIVOS Y VISUALIZACIÓN
    # ==========================================================================

    def abrir_imagen(self):
        """Abre un diálogo de selección de archivo y carga la imagen normalizada."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen para TP3",
            filetypes=[
                ("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.webp *.tif *.tiff"),
                ("Todos los archivos", "*.*")
            ]
        )

        if not ruta:
            return

        try:
            imagen_pil = Image.open(ruta).convert("RGB")
            # Normalización a float32 en rango [0.0, 1.0]
            image = np.array(imagen_pil, dtype=np.float32) / 255.0

            self.imagen_original = image
            self.imagen_entrada = self.imagen_original.copy()
            self.imagen_procesada = self.imagen_original.copy()

            h, w = image.shape[:2]
            stats = pdi.calcular_estadisticas_luminancia(image)

            self.lbl_info_entrada.config(text=f"{w}x{h} px | Y_med: {stats['mean']:.2f}")
            self.lbl_info_resultado.config(text=f"{w}x{h} px | Inicial")

            self.mostrar_imagen(self.imagen_entrada, self.label_entrada)
            self.mostrar_imagen(self.imagen_procesada, self.label_resultado)

            self.lbl_estado.config(
                text=f"✓ Imagen cargada exitosamente: {w}x{h} px (Luminancia Media Y = {stats['mean']:.3f})"
            )
            self.lbl_tiempo.config(text="Carga: OK")

            # Si auto_preview está activo, aplicar filtro de inmediato
            if self.auto_preview.get():
                self.aplicar_operacion()

        except Exception as e:
            messagebox.showerror("Error al abrir imagen", f"No se pudo cargar la imagen:\n{e}")


    def restaurar_original(self):
        """Restaura la imagen de entrada a la copia original cargada del disco."""
        if self.imagen_original is None:
            return

        self.imagen_entrada = self.imagen_original.copy()
        self.mostrar_imagen(self.imagen_entrada, self.label_entrada)
        
        h, w = self.imagen_entrada.shape[:2]
        stats = pdi.calcular_estadisticas_luminancia(self.imagen_entrada)
        self.lbl_info_entrada.config(text=f"{w}x{h} px | Y_med: {stats['mean']:.2f}")

        self.lbl_estado.config(text="✓ Imagen original restaurada en el visor de entrada.")
        
        if self.auto_preview.get():
            self.aplicar_operacion()


    def pasar_resultado_a_entrada(self):
        """Pasa la imagen resultado actual como nueva imagen de entrada (feedback pipeline)."""
        if self.imagen_procesada is None:
            messagebox.showwarning("Atención", "Primero abrí una imagen y generá un resultado.")
            return

        self.imagen_entrada = self.imagen_procesada.copy()
        self.mostrar_imagen(self.imagen_entrada, self.label_entrada)

        h, w = self.imagen_entrada.shape[:2]
        stats = pdi.calcular_estadisticas_luminancia(self.imagen_entrada)
        self.lbl_info_entrada.config(text=f"{w}x{h} px | Y_med: {stats['mean']:.2f}")

        self.lbl_estado.config(text="✓ El resultado procesado se asignó como nueva Imagen de Entrada.")


    def guardar_resultado(self):
        """Exporta el resultado actual a archivo PNG/JPG/BMP."""
        if self.imagen_procesada is None:
            messagebox.showwarning("Atención", "No hay ninguna imagen resultado para guardar.")
            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar resultado de luminancia",
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
            imagen_uint8 = (np.clip(self.imagen_procesada, 0.0, 1.0) * 255.0).round().astype(np.uint8)
            Image.fromarray(imagen_uint8).save(ruta)
            self.lbl_estado.config(text=f"✓ Imagen guardada exitosamente en: {ruta}")
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{e}")


    def mostrar_imagen(self, array_imagen, label_widget):
        """
        Renderiza un array NumPy normalizado [0.0, 1.0] dentro del widget Label,
        escalándolo con preservación estricta de la relación de aspecto.
        """
        if array_imagen is None:
            return

        # Dimensiones del contenedor del visor
        w_max = max(label_widget.winfo_width() - 8, 320)
        h_max = max(label_widget.winfo_height() - 8, 360)

        imagen_uint8 = (np.clip(array_imagen, 0.0, 1.0) * 255.0).round().astype(np.uint8)
        imagen_pil = Image.fromarray(imagen_uint8)

        # Redimensionado de alta calidad manteniendo relación de aspecto
        imagen_pil.thumbnail((w_max, h_max), Image.Resampling.LANCZOS)
        foto = ImageTk.PhotoImage(imagen_pil)

        # Conservar referencia para el garbage collector de Tkinter
        label_widget.foto = foto
        label_widget.config(image=foto, text="")


    # ==========================================================================
    # ALGORITMO CENTRAL: APLICACIÓN DE FILTRO DE LUMINANCIA
    # ==========================================================================

    def aplicar_operacion(self):
        """
        Ejecuta la operación de luminancia seleccionada midiendo el tiempo de cálculo.
        Flujo de trabajo:
            1. Imagen RGB normalizada [0.0, 1.0].
            2. Conversión a espacio YIQ.
            3. Modificación exclusiva de la matriz de Luminancia Y (I, Q fijos).
            4. Retransformación YIQ a RGB clampeado en [0.0, 1.0].
        """
        if self.imagen_entrada is None:
            messagebox.showwarning("Atención", "Primero abrí una imagen para operar.")
            return

        t_inicio = time.perf_counter()
        operacion = self.operacion.get()
        image = self.imagen_entrada

        if operacion == "Sin procesamiento":
            result = image.copy()

        elif operacion == "Raíz":
            yiq = pdi.rgb_to_yiq(image)
            yiq = pdi.square_root_luminance(yiq)
            result = pdi.yiq_to_rgb(yiq)

        elif operacion == "Cuadrado":
            yiq = pdi.rgb_to_yiq(image)
            yiq = pdi.square_luminance(yiq)
            result = pdi.yiq_to_rgb(yiq)

        elif operacion == "Lineal a trozos":
            try:
                y_min = float(self.y_min.get())
                y_max = float(self.y_max.get())
            except ValueError:
                messagebox.showwarning("Atención", "Y min e Y max deben ser números decimales válidos.")
                return

            if not (0.0 <= y_min < y_max <= 1.0):
                messagebox.showwarning(
                    "Atención",
                    f"Rango inválido: se debe cumplir 0 <= Y min < Y max <= 1.\n(Recibido: Y_min={y_min}, Y_max={y_max})"
                )
                return

            yiq = pdi.rgb_to_yiq(image)
            yiq = pdi.piecewise_linear_luminance(yiq, y_min, y_max)
            result = pdi.yiq_to_rgb(yiq)

        else:
            result = image.copy()

        t_total_ms = (time.perf_counter() - t_inicio) * 1000.0

        self.imagen_procesada = result
        self.mostrar_imagen(self.imagen_procesada, self.label_resultado)

        # Estadísticas del resultado
        stats_r = pdi.calcular_estadisticas_luminancia(result)
        h, w = result.shape[:2]
        self.lbl_info_resultado.config(text=f"{w}x{h} px | Y_med: {stats_r['mean']:.2f}")

        detalle_params = ""
        if operacion == "Lineal a trozos":
            detalle_params = f" [Ymin={self.y_min.get()}, Ymax={self.y_max.get()}]"

        self.lbl_estado.config(
            text=f"✓ Operación aplicada con éxito: '{operacion}'{detalle_params} en {t_total_ms:.2f} ms."
        )
        self.lbl_tiempo.config(text=f"Δt: {t_total_ms:.2f} ms")


    # ==========================================================================
    # ANÁLISIS DE HISTOGRAMA DE LUMINANCIA CON MATPLOTLIB
    # ==========================================================================

    def mostrar_histograma(self):
        """
        Calcula y grafica el histograma de la componente de luminancia Y
        con 32 bins en el intervalo canónico [0.0, 1.0], ofreciendo vista individual
        o comparativa (Entrada vs Resultado) con estilo visual dark/slate.
        """
        if self.imagen_entrada is None:
            messagebox.showwarning("Atención", "Primero abrí una imagen para ver su histograma.")
            return

        modo = self.histograma_de.get()

        if modo == "Resultado" and self.imagen_procesada is None:
            messagebox.showwarning("Atención", "Primero generá un resultado para ver su histograma.")
            return

        # Configuración estética de Matplotlib para coordinar con el HUD
        plt.style.use("dark_background")
        fig = plt.figure(figsize=(9, 5), facecolor="#0f172a")

        if modo == "Comparativo":
            ax1 = fig.add_subplot(1, 2, 1, facecolor="#1e293b")
            ax2 = fig.add_subplot(1, 2, 2, facecolor="#1e293b")

            # 1. Histograma Entrada
            yiq_e = pdi.rgb_to_yiq(self.imagen_entrada)
            y_e = yiq_e[:, :, 0].ravel()
            mean_e = np.mean(y_e)
            std_e = np.std(y_e)

            ax1.hist(y_e, bins=32, range=(0.0, 1.0), color="#38bdf8", edgecolor="#0284c7", alpha=0.85)
            ax1.axvline(mean_e, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Media: {mean_e:.3f}")
            ax1.set_title("Histograma Y — ENTRADA", fontsize=11, fontweight="bold", color="#60a5fa", pad=10)
            ax1.set_xlabel("Luminancia Y [0.0, 1.0]", fontsize=9, color="#cbd5e1")
            ax1.set_ylabel("Frecuencia (Píxeles)", fontsize=9, color="#cbd5e1")
            ax1.grid(True, linestyle=":", alpha=0.4, color="#64748b")
            ax1.legend(loc="upper right", fontsize=8)
            ax1.tick_params(colors="#94a3b8")

            # 2. Histograma Resultado
            img_res = self.imagen_procesada if self.imagen_procesada is not None else self.imagen_entrada
            yiq_r = pdi.rgb_to_yiq(img_res)
            y_r = yiq_r[:, :, 0].ravel()
            mean_r = np.mean(y_r)
            std_r = np.std(y_r)

            op_nombre = self.operacion.get()
            ax2.hist(y_r, bins=32, range=(0.0, 1.0), color="#34d399", edgecolor="#059669", alpha=0.85)
            ax2.axvline(mean_r, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Media: {mean_r:.3f}")
            ax2.set_title(f"Histograma Y — RESULTADO ({op_nombre})", fontsize=11, fontweight="bold", color="#34d399", pad=10)
            ax2.set_xlabel("Luminancia Y [0.0, 1.0]", fontsize=9, color="#cbd5e1")
            ax2.set_ylabel("Frecuencia (Píxeles)", fontsize=9, color="#cbd5e1")
            ax2.grid(True, linestyle=":", alpha=0.4, color="#64748b")
            ax2.legend(loc="upper right", fontsize=8)
            ax2.tick_params(colors="#94a3b8")

            fig.suptitle("PDI TP3 — Análisis Comparativo de Distribución de Luminancia (32 bins)",
                         fontsize=12, fontweight="bold", color="#f8fafc", y=0.98)

        else:
            # Gráfico único (Entrada o Resultado)
            ax = fig.add_subplot(1, 1, 1, facecolor="#1e293b")
            if modo == "Entrada":
                img = self.imagen_entrada
                color_barras = "#38bdf8"
                edge_col = "#0284c7"
                nombre = "Entrada"
            else:
                img = self.imagen_procesada
                color_barras = "#34d399"
                edge_col = "#059669"
                nombre = f"Resultado ({self.operacion.get()})"

            yiq = pdi.rgb_to_yiq(img)
            lum = yiq[:, :, 0].ravel()
            mean_val = np.mean(lum)
            std_val = np.std(lum)

            ax.hist(lum, bins=32, range=(0.0, 1.0), color=color_barras, edgecolor=edge_col, alpha=0.85)
            ax.axvline(mean_val, color="#ef4444", linestyle="--", linewidth=1.8, label=f"Media (μ): {mean_val:.3f}")
            ax.axvline(mean_val + std_val, color="#f59e0b", linestyle=":", linewidth=1.2, label=f"μ + σ: {mean_val+std_val:.3f}")
            ax.axvline(max(0.0, mean_val - std_val), color="#f59e0b", linestyle=":", linewidth=1.2, label=f"μ - σ: {max(0.0, mean_val-std_val):.3f}")

            ax.set_title(f"Histograma de Luminancia Y — {nombre} (32 bins)", fontsize=12, fontweight="bold", color="#f8fafc", pad=12)
            ax.set_xlabel("Luminancia Y [0.0, 1.0]", fontsize=10, color="#cbd5e1")
            ax.set_ylabel("Frecuencia (Píxeles)", fontsize=10, color="#cbd5e1")
            ax.grid(True, linestyle=":", alpha=0.4, color="#64748b")
            ax.legend(loc="upper right", fontsize=9)
            ax.tick_params(colors="#94a3b8")

        plt.tight_layout()
        plt.show()


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ==============================================================================

def main():
    root = tk.Tk()
    app = AppPDI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
