# -*- coding: utf-8 -*-
"""
Punto de entrada alternativo / Alias para TP3 - Operaciones de Luminancia.
Permite ejecutar la aplicación directamente como `python TP3/tp3_pdi.py`.
"""

import sys
import os

# Asegurar que el directorio de TP3 se encuentre en el path de módulos
dir_actual = os.path.dirname(os.path.abspath(__file__))
if dir_actual not in sys.path:
    sys.path.insert(0, dir_actual)

from main import main, AppPDI

if __name__ == "__main__":
    main()
