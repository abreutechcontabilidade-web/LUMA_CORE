import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_mem_priority_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Função de extração de intenção (reforçada)
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

# Substituir processar para dar prioridade à memória específica
old_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        intent = extrair_intencao(prompt)
        # PRIORIDADE 1: Regras Hardcoded (Sempre)
        if "tetris" in norm:
            return self._gerar_tetris(), "LOCAL_ONNX"
        if "cobra" in norm or "snake" in norm:
            return self._gerar_snake(), "LOCAL_ONNX"
        if "jogo da velha" in norm or "tic tac toe" in norm:
            return self._gerar_jogo_da_velha(), "LOCAL_BASIC"
        if ("roman" in norm or "romano" in norm) and "calculadora" in norm:
            return self._gerar_calculadora_romana(), "LOCAL_ONNX"
        if "calculadora" in norm:
            return self._gerar_calculadora_cientifica(), "LOCAL_ONNX"
        if "pomodoro" in norm:
            return self._gerar_pomodoro(), "LOCAL_ONNX"

        # PRIORIDADE 2: Memoria Aprendida (por intencao)
        if intent in self.dynamic_tools:
            return self.dynamic_tools[intent], "APRENDIDO_NUVEM"
        # Fallback para chave exata (compatibilidade)
        if norm in self.dynamic_tools:
            return self.dynamic_tools[norm], "APRENDIDO_NUVEM_LEGACY"

        return None, "NUVEM_NECESSARIA"'''

new_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        intent = extrair_intencao(prompt)
        
        # PRIORIDADE 1: Memoria Aprendida (se a intencao tiver palavras-chave especificas)
        if intent in self.dynamic_tools and any(k in intent for k in ["placar", "cores", "historico", "empate"]):
            return self.dynamic_tools[intent], "APRENDIDO_NUVEM_PRIORITY"
        
        # PRIORIDADE 2: Regras Hardcoded (Sempre)
        if "tetris" in norm:
            return self._gerar_tetris(), "LOCAL_ONNX"
        if "cobra" in norm or "snake" in norm:
            return self._gerar_snake(), "LOCAL_ONNX"
        if "jogo da velha" in norm or "tic tac toe" in norm:
            return self._gerar_jogo_da_velha(), "LOCAL_BASIC"
        if ("roman" in norm or "romano" in norm) and "calculadora" in norm:
            return self._gerar_calculadora_romana(), "LOCAL_ONNX"
        if "calculadora" in norm:
            return self._gerar_calculadora_cientifica(), "LOCAL_ONNX"
        if "pomodoro" in norm:
            return self._gerar_pomodoro(), "LOCAL_ONNX"

        # PRIORIDADE 3: Memoria Aprendida (fallback para outros padroes)
        if intent in self.dynamic_tools:
            return self.dynamic_tools[intent], "APRENDIDO_NUVEM"
        if norm in self.dynamic_tools:
            return self.dynamic_tools[norm], "APRENDIDO_NUVEM_LEGACY"

        return None, "NUVEM_NECESSARIA"'''

if old_proc in code:
    code = code.replace(old_proc, new_proc)
    print("[OK] processar() atualizado para priorizar memoria especifica.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Substituindo por regex...")
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