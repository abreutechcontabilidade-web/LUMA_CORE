# -*- coding: utf-8 -*-
"""
LUMA_CORE Hardware Adapter (Gamma Ramp v2)
Escala de temperatura: 0 (frio/azul) -- 50 (neutro) -- 100 (quente/amarelo)
"""
import ctypes
from ctypes import wintypes

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
gdi32.SetDeviceGammaRamp.argtypes = [wintypes.HDC, ctypes.POINTER(ctypes.c_ushort)]
gdi32.SetDeviceGammaRamp.restype = wintypes.BOOL

_brilho_atual = 80
_calor_atual = 50  # 50 = neutro (novo default)

def _build_ramp(brilho, calor):
    f = max(50.0, min(100.0, brilho)) / 100.0
    c = max(0.0, min(100.0, calor))

    if c < 50:
        # Frio: azul aumenta, vermelho diminui (neutro a azul)
        factor = (50 - c) / 50.0
        rf = 1.0 - 0.30 * factor
        gf = 1.0 - 0.05 * factor
        bf = 1.0 + 0.35 * factor
    elif c > 50:
        # Quente: vermelho aumenta, azul diminui (neutro a amarelo)
        factor = (c - 50) / 50.0
        rf = 1.0 + 0.30 * factor
        gf = 1.0 + 0.05 * factor
        bf = 1.0 - 0.60 * factor
    else:
        rf, gf, bf = 1.0, 1.0, 1.0

    ramp = (ctypes.c_ushort * 768)()
    for i in range(256):
        k = i * 257
        ramp[i] = min(65535, int(k * f * rf + 0.5))
        ramp[256 + i] = min(65535, int(k * f * gf + 0.5))
        ramp[512 + i] = min(65535, int(k * f * bf + 0.5))
    return ramp

def _apply(ramp):
    # Pega HDC novo a cada chamada (alguns drivers invalidam o antigo)
    hdc = user32.GetDC(0)
    if not hdc:
        return False
    try:
        return bool(gdi32.SetDeviceGammaRamp(hdc, ramp))
    finally:
        user32.ReleaseDC(0, hdc)

def alterar_brilho(nivel):
    global _brilho_atual
    _brilho_atual = max(50, min(100, int(nivel)))
    if _apply(_build_ramp(_brilho_atual, _calor_atual)):
        return f"Brilho: {_brilho_atual}% (calor {_calor_atual})"
    return "Erro: driver recusou Gamma Ramp"

def alterar_calor(nivel):
    global _calor_atual
    _calor_atual = max(0, min(100, int(nivel)))
    if _apply(_build_ramp(_brilho_atual, _calor_atual)):
        label = "frio" if _calor_atual < 50 else ("neutro" if _calor_atual == 50 else "quente")
        return f"Temperatura: {_calor_atual} ({label})"
    return "Erro: driver recusou Gamma Ramp"

def ler_status_hardware():
    return {"monitor": "Gamma Ramp v2", "brilho": _brilho_atual, "calor": _calor_atual, "status": "hardware_real"}