# -*- coding: utf-8 -*-
"""Morfología matemática y filtros espaciales no lineales (TP5 - PDI Grupo 9)."""
import numpy as np
from PIL import Image

ELEMENTO_ESTRUCTURANTE = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)

def convertir_escala_grises(img):
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    return np.clip(0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2], 0, 255).astype(np.uint8)

def binarizar_umbral(img, u=127):
    return np.where(img > u, 255, 0).astype(np.uint8)

def _cruz(img, mode="edge", cval=None):
    kw = {"constant_values": cval} if cval is not None else {}
    p = np.pad(img, 1, mode=mode, **kw)
    return [p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 1:-1], p[1:-1, 2:], p[2:, 1:-1]]

erosion = lambda img: np.minimum.reduce(_cruz(img, "edge"))
dilatacion = lambda img: np.maximum.reduce(_cruz(img, "edge"))
apertura = lambda img: dilatacion(erosion(img))
cierre = lambda img: erosion(dilatacion(img))
borde_ext = lambda img: np.clip(dilatacion(img).astype(np.int16) - img, 0, 255).astype(np.uint8)
borde_int = lambda img: np.clip(img.astype(np.int16) - erosion(img), 0, 255).astype(np.uint8)
grad_morf = lambda img: np.clip(dilatacion(img).astype(np.int16) - erosion(img), 0, 255).astype(np.uint8)
top_hat = lambda img: np.clip(img.astype(np.int16) - apertura(img), 0, 255).astype(np.uint8)

def mediana_3x3(img):
    h, w = img.shape
    p = np.pad(img, 1, mode="edge")
    return np.round(np.median([p[i:i + h, j:j + w] for i in range(3) for j in range(3)], axis=0)).astype(np.uint8)

def esqueletizacion(img, u=127):
    act, esq = binarizar_umbral(img, u), np.zeros_like(img)
    ero_b = lambda x: np.minimum.reduce(_cruz(x, "constant", 0))
    dil_b = lambda x: np.maximum.reduce(_cruz(x, "constant", 0))
    while np.any(act):
        ab = dil_b(ero_b(act))
        esq = np.maximum(esq, np.where((act > 0) & (ab == 0), 255, 0).astype(np.uint8))
        sig = ero_b(act)
        if np.array_equal(sig, act): break
        act = sig
    return esq

def mean_shift(img, hs=3, hr=25, iters=10):
    h, w = img.shape
    src, res = img.astype(np.float32), np.empty_like(img)
    hs, hr = max(1, int(hs)), max(1, int(hr))
    ys, xs = np.mgrid[0:h, 0:w]
    for r in range(h):
        for c in range(w):
            cy, cx, cg = float(r), float(c), float(src[r, c])
            for _ in range(iters):
                y0, y1 = max(0, int(round(cy)) - hs), min(h, int(round(cy)) + hs + 1)
                x0, x1 = max(0, int(round(cx)) - hs), min(w, int(round(cx)) + hs + 1)
                sub, sub_y, sub_x = src[y0:y1, x0:x1], ys[y0:y1, x0:x1], xs[y0:y1, x0:x1]
                m = ((sub_y - cy)**2 + (sub_x - cx)**2 <= hs**2) & (np.abs(sub - cg) <= hr)
                if not np.any(m): break
                ny, nx, ng = np.mean(sub_y[m]), np.mean(sub_x[m]), np.mean(sub[m])
                if (nx - cx)**2 + (ny - cy)**2 < 0.01 and abs(ng - cg) < 0.5: break
                cx, cy, cg = nx, ny, ng
            res[r, c] = int(np.clip(round(cg), 0, 255))
    return res

OPERACIONES = {
    "Erosión 3x3": erosion,
    "Dilatación 3x3": dilatacion,
    "Apertura (erosión y dilatación)": apertura,
    "Cierre (dilatación y erosión)": cierre,
    "Borde exterior": borde_ext,
    "Borde interior": borde_int,
    "Gradiente morfológico": grad_morf,
    "Top Hat blanco": top_hat,
    "Mediana 3x3": mediana_3x3,
    "Binarización por umbral": binarizar_umbral,
    "Esqueletización binaria": esqueletizacion,
    "Mean Shift": mean_shift,
}
