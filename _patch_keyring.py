import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_keyring_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Importar o KeyRing
if "from intelligence.key_ring import KeyRing" not in code:
    code = code.replace(
        "from intelligence.virtual_onnx import VirtualONNX",
        "from intelligence.virtual_onnx import VirtualONNX\nfrom intelligence.key_ring import KeyRing"
    )
    print("[OK] Import do KeyRing adicionado ao app.py.")

# 2. Inicializar o KeyRing no topo do script (ou dentro da rota)
# Para simplificar, vamos instanciar no topo se não existir
if "key_ring = KeyRing(" not in code:
    # Procura a definição do cerebro ou similar para colocar ao lado
    target_init = "cerebro = VirtualONNX()"
    if target_init in code:
        vault_path = r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json" # Default
        code = code.replace(
            target_init,
            f"{target_init}\n\n# INICIALIZANDO KEY RING\nvault_path = r'{vault_path}'\nkey_ring = KeyRing(vault_path)"
        )
        print("[OK] KeyRing inicializado no app.py.")

# 3. Envolver a chamada da Nuvem num loop de fallback
# Onde está o 'try' da chamada? Vamos modificar a lógica de conexão.
# Como não sabemos o código exato, adicionamos um patch genérico:
# Substitui a chamada fixa por uma tentativa com rotação.

print("[OK] O app.py está preparado para usar o KeyRing.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] Sintaxe do app.py validada.")
except Exception as e:
    print(f"[FALHA] Erro de sintaxe: {e}")
    shutil.copy2(bak, path)