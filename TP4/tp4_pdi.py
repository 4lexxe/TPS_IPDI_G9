# -*- coding: utf-8 -*-
"""
Punto de entrada alternativo para TP4 - Procesamiento por Convolucion.
Permite ejecutar la aplicacion directamente como `python TP4/tp4_pdi.py`.
"""

import sys
import os

# Asegurar que el directorio de TP4 se encuentre en el path de modulos
dir_actual = os.path.dirname(os.path.abspath(__file__))
if dir_actual not in sys.path:
    sys.path.insert(0, dir_actual)

from main import main, AppPDI  # noqa: F401

if __name__ == "__main__":
    main()
