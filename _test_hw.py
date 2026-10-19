import sys, os
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from core.hardware import alterar_brilho, ler_status_hardware

print("[TESTE] Status:", ler_status_hardware())
print("[TESTE] Ajustar para 75%...")
print("[TESTE] Resultado:", alterar_brilho(75))