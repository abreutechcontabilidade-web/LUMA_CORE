import sys, os, time
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from core.hardware import alterar_brilho, ler_status_hardware

print("[TESTE] Status:", ler_status_hardware())
print("[TESTE] A diminuir o brilho para 20%...")
print("[TESTE] Resultado:", alterar_brilho(20))
time.sleep(2) # Dá 2 segundos para o senhor ver a mudança
print("[TESTE] A restaurar o brilho para 80%...")
print("[TESTE] Resultado:", alterar_brilho(80))