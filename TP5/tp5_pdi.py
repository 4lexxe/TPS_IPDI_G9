# -*- coding: utf-8 -*-
"""
Punto de entrada alternativo para TP5 - Morfologia Matematica y Filtros No Lineales.
Permite ejecutar la aplicacion directamente como `python TP5/tp5_pdi.py`.
"""

import os
import sys

# Asegurar que el directorio de TP5 se encuentre en el path de modulos
dir_actual = os.path.dirname(os.path.abspath(__file__))
if dir_actual not in sys.path:
    sys.path.insert(0, dir_actual)

from main import AppMorfologia, main  # noqa: F401

if __name__ == "__main__":
    main()
