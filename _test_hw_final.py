import sys, time
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from core.hardware import alterar_brilho, ler_status_hardware

print("[STATUS]", ler_status_hardware())
print("[TESTE] Aplicar 30%...")
print(alterar_brilho(30))
time.sleep(1)
print("[TESTE] Aplicar 70%...")
print(alterar_brilho(70))