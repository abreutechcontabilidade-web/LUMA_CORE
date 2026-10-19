import sys, time
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from core.hardware import alterar_brilho, ler_status_hardware

print("[TESTE] Status:", ler_status_hardware())
print("[TESTE] A escurecer o ecrã para 30%...")
print(alterar_brilho(30))
time.sleep(3)
print("[TESTE] A restaurar o brilho para 90%...")
print(alterar_brilho(90))