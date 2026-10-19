import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_intent_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Função de extração de intenção
intent_func = '''
def extrair_intencao(prompt: str) -> str:
    p = prompt.lower()
    tags = []
    if any(k in p for k in ["velha", "tic tac toe"]): tags.append("velha")
    if any(k in p for k in ["placar", "placa", "pontuacao"]): tags.append("placar")
    if any(k in p for k in ["empate"]): tags.append("empate")
    if any(k in p for k in ["cor", "cores", "vermelho", "azul"]): tags.append("cores")
    if any(k in p for k in ["historico", "histórico"]): tags.append("historico")
    if any(k in p for k in ["calculadora"]): tags.append("calculadora")
    return "_".join(sorted(tags)) if tags else p.strip()

'''

if "def extrair_intencao" not in code:
    code = code.replace("class VirtualONNX:", intent_func + "\nclass VirtualONNX:")

# Substituir processar
old_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        # PRIORIDADE 1: Regras Hardcoded (Sempre)'''
new_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        intent = extrair_intencao(prompt)
        # PRIORIDADE 1: Regras Hardcoded (Sempre)'''
code = code.replace(old_proc, new_proc)

old_mem = '''        # PRIORIDADE 2: Memoria Aprendida (So para padroes NAO conhecidos)
        if norm in self.dynamic_tools:
            return self.dynamic_tools[norm], "APRENDIDO_NUVEM"

        return None, "NUVEM_NECESSARIA"'''
new_mem = '''        # PRIORIDADE 2: Memoria Aprendida (por intencao)
        if intent in self.dynamic_tools:
            return self.dynamic_tools[intent], "APRENDIDO_NUVEM"
        # Fallback para chave exata (compatibilidade)
        if norm in self.dynamic_tools:
            return self.dynamic_tools[norm], "APRENDIDO_NUVEM_LEGACY"

        return None, "NUVEM_NECESSARIA"'''
code = code.replace(old_mem, new_mem)

# Substituir aprender_da_nuvem
old_learn = '''    def aprender_da_nuvem(self, prompt: str, html: str):
        norm = prompt.lower().strip()
        self.dynamic_tools[norm] = html'''
new_learn = '''    def aprender_da_nuvem(self, prompt: str, html: str):
        intent = extrair_intencao(prompt)
        self.dynamic_tools[intent] = html'''
code = code.replace(old_learn, new_learn)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. virtual_onnx.py com intencao.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)