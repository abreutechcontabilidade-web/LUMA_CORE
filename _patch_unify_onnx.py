import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_unify_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remover a funcao extrair_intencao local (agora vem do cure_engine)
if "def extrair_intencao(prompt: str)" in code and "class VirtualONNX" in code:
    # Substitui a funcao local por um import
    pattern = r'def extrair_intencao\(prompt: str\)[\s\S]*?(?=\nclass VirtualONNX|\ndef )'
    code = re.sub(pattern, '', code)
    print("[OK] Funcao local 'extrair_intencao' removida.")

# 2. Importar do cure_engine
if "from intelligence.cure_engine import extrair_intencao" not in code:
    code = code.replace(
        "import json",
        "import json\nimport sys\nsys.path.insert(0, r'C:\\Users\\user\\Desktop\\LUMA_CORE')\nfrom intelligence.cure_engine import extrair_intencao"
    )
    print("[OK] Import do cure_engine adicionado.")

# 3. Garantir que processar() usa a memoria especifica primeiro
old_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        intent = extrair_intencao(prompt)
        
        # PRIORIDADE 1: Memoria Aprendida (se a intencao tiver palavras-chave especificas)
        if intent in self.dynamic_tools and any(k in intent for k in ["placar", "cores", "historico", "empate"]):
            return self.dynamic_tools[intent], "APRENDIDO_NUVEM_PRIORITY"'''

new_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        intent = extrair_intencao(prompt)
        print(f"[ONNX] Prompt: '{prompt[:40]}...' | Intencao: '{intent}' | Memoria: {list(self.dynamic_tools.keys())}")
        
        # PRIORIDADE 1: Memoria Aprendida (se a intencao tiver palavras-chave especificas)
        if intent in self.dynamic_tools and any(k in intent for k in ["placar", "cores", "historico", "empate"]):
            print(f"[ONNX] Usando memoria PRIORITARIA para '{intent}'")
            return self.dynamic_tools[intent], "APRENDIDO_NUVEM_PRIORITY"'''

if old_proc in code:
    code = code.replace(old_proc, new_proc)
    print("[OK] processar() atualizado com logs.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando regex...")
    pattern = r'    def processar\(self, prompt: str\):[\s\S]*?(?=    def aprender_da_nuvem)'
    code = re.sub(pattern, new_proc + "\n\n", code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. virtual_onnx.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)