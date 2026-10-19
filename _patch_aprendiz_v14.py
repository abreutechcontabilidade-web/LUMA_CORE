import re, sys, py_compile, shutil, time

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak." + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print("[OK] Backup:", bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove o metodo _gerar_jogo_da_velha_premium
code = re.sub(r"    def _gerar_jogo_da_velha_premium\(self\):[\s\S]*?(?=    def _gerar_calculadora_cientifica)", "", code)

# Corrige a rota no processar() para mandar "placar/historico" para a nuvem
old_route = '''        if "jogo da velha" in norm or "tic tac toe" in norm:
            if "placar" in norm or "historico" in norm or "histórico" in norm or "placa" in norm:
                return self._gerar_jogo_da_velha_premium(), "LOCAL_PREMIUM_ONISCIENTE"
            return self._gerar_jogo_da_velha(), "LOCAL_ONNX_HARDCODED"
'''
new_route = '''        if "jogo da velha" in norm or "tic tac toe" in norm:
            if "placar" in norm or "historico" in norm or "histórico" in norm or "placa" in norm:
                return None, "NUVEM_NECESSARIA"  # Forca a nuvem a ser chamada
            return self._gerar_jogo_da_velha(), "LOCAL_ONNX_HARDCODED"
'''

if old_route in code:
    code = code.replace(old_route, new_route)
    print("[OK] Rota corrigida: O Local agora manda pedidos de 'placar' para a Nuvem.")
else:
    print("[AVISO] Rota nao encontrada. Verificando o codigo...")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. O Motor Aprendiz esta pronto.")
except Exception as e:
    print(f"[FALHA] py_compile falhou: {e}")
    shutil.copy2(bak, path)
    sys.exit(1)