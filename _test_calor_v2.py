import sys, time
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from core.hardware import alterar_calor, alterar_brilho, ler_status_hardware

print("[STATUS]", ler_status_hardware())
print("[TESTE] Aplicando FRIO (0)...")
print(alterar_calor(0))
time.sleep(2)
print("[TESTE] Aplicando NEUTRO (50)...")
print(alterar_calor(50))
time.sleep(2)
print("[TESTE] Aplicando QUENTE (100)...")
print(alterar_calor(100))
time.sleep(2)
print("[TESTE] Voltando a NEUTRO (50)...")
print(alterar_calor(50))