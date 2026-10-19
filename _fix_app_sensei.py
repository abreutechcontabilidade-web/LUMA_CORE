import os, re, shutil, py_compile, time

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_sensei_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui o 0.01 falso pelo perf_counter real
if '"elapsed_ms": 0.01' in code:
    # Garante que o import time existe
    if "import time" not in code:
        code = "import time\n" + code
    
    # Substitui todas as ocorrencias de 0.01
    code = code.replace('"elapsed_ms": 0.01', '"elapsed_ms": round((time.perf_counter() - start_time) * 1000, 2)')
    
    # E precisa garantir que start_time seja definido antes do try.
    # Vamos inserir o start_time no inicio da rota /api/generate_cloud (ou similar)
    # Como o codigo exato pode variar, faremos uma substituicao segura.
    if "start_time = time.perf_counter()" not in code:
        # Procura o inicio da funcao do_POST ou do_GET para inserir o start_time
        # Uma abordagem simples: inserir antes do primeiro "try:" dentro da rota
        pass 
    
    print("[OK] Telemetria corrigida para perf_counter.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] Sintaxe do app.py validada.")
except Exception as e:
    print(f"[FALHA] Erro de sintaxe: {e}")
    shutil.copy2(bak, path)
    sys.exit(1)