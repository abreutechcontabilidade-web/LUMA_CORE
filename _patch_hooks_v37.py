import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_hooks_v37_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Adiciona os hooks no Jogo da Velha Básico
old_velha = '''            <p id='status' style='margin-top:20px; font-size:20px; color:#10b981;'>Vez do Jogador: X</p>
            
            <!-- GANCHO: A NUVEM VAI INJETAR O PLACAR/HISTÓRICO AQUI -->
            <!-- [HOOK_EXTRA_PANELS] -->'''

new_velha = '''            <!-- [HOOK_TOP] -->
            <p id='status' style='margin-top:20px; font-size:20px; color:#10b981;'>Vez do Jogador: X</p>
            <!-- [HOOK_BOTTOM] -->'''

if old_velha in code:
    code = code.replace(old_velha, new_velha)
    print("[OK] Ganchos [HOOK_TOP] e [HOOK_BOTTOM] adicionados ao Jogo da Velha.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. virtual_onnx.py atualizado com ganchos.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)