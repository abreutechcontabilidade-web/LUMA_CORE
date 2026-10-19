import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_priority_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui o processar para priorizar o hardcoded
old_processar = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        
        # PRIORIDADE 1: Memoria Aprendida (se o prompt exato ja foi aprendido, usa-o)
        if norm in self.dynamic_tools:
            return self.dynamic_tools[norm], "APRENDIDO_NUVEM"

        # PRIORIDADE 2: Regras Hardcoded (Fallback)
        if "tetris" in norm:
            return self._gerar_tetris(), "LOCAL_ONNX"
        if "cobra" in norm or "snake" in norm or "cobrinha" in norm:
            return self._gerar_snake(), "LOCAL_ONNX"
        if "jogo da velha" in norm or "tic tac toe" in norm:
            if "placar" in norm or "historico" in norm or "histórico" in norm or "placa" in norm:
                return self._gerar_jogo_da_velha_premium(), "LOCAL_PREMIUM_ONISCIENTE"
            return self._gerar_jogo_da_velha(), "LOCAL_ONNX"
        if ("roman" in norm or "romano" in norm or "romana" in norm) and "calculadora" in norm:
            return self._gerar_calculadora_romana(), "LOCAL_ONNX"
        if "calculadora" in norm:
            return self._gerar_calculadora_cientifica(), "LOCAL_ONNX"
        if "pomodoro" in norm or "temporizador" in norm or "timer" in norm:
            return self._gerar_pomodoro(), "LOCAL_ONNX"
        if "tarefa" in norm or "todo" in norm or "to-do" in norm:
            return self._gerar_todo(), "LOCAL_ONNX"
            
        return None, "NUVEM_NECESSARIA"'''

new_processar = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        
        # PRIORIDADE 1: Regras Hardcoded (Sempre)
        if "tetris" in norm:
            return self._gerar_tetris(), "LOCAL_ONNX"
        if "cobra" in norm or "snake" in norm or "cobrinha" in norm:
            return self._gerar_snake(), "LOCAL_ONNX"
        if "jogo da velha" in norm or "tic tac toe" in norm:
            if "placar" in norm or "historico" in norm or "histórico" in norm or "placa" in norm:
                return self._gerar_jogo_da_velha_premium(), "LOCAL_PREMIUM_ONISCIENTE"
            return self._gerar_jogo_da_velha(), "LOCAL_ONNX"
        if ("roman" in norm or "romano" in norm or "romana" in norm) and "calculadora" in norm:
            return self._gerar_calculadora_romana(), "LOCAL_ONNX"
        if "calculadora" in norm:
            return self._gerar_calculadora_cientifica(), "LOCAL_ONNX"
        if "pomodoro" in norm:
            return self._gerar_pomodoro(), "LOCAL_ONNX"
        if "cronometro" in norm or "cronómetro" in norm or "stopwatch" in norm:
            return self._gerar_cronometro(), "LOCAL_ONNX"
        if "forca" in norm or "hangman" in norm:
            return self._gerar_forca(), "LOCAL_ONNX"
        if "tarefa" in norm or "todo" in norm or "to-do" in norm:
            return self._gerar_todo(), "LOCAL_ONNX"
            
        # PRIORIDADE 2: Memoria Aprendida (So para padroes NAO conhecidos)
        if norm in self.dynamic_tools:
            return self.dynamic_tools[norm], "APRENDIDO_NUVEM"

        return None, "NUVEM_NECESSARIA"'''

if old_processar in code:
    code = code.replace(old_processar, new_processar)
    print("[OK] VirtualONNX prioriza hardcoded.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Substituindo a funcao inteira por regex.")
    pattern = r"    def processar\(self, prompt: str\):[\s\S]*?(?=    def aprender_da_nuvem)"
    code = re.sub(pattern, new_processar + "\n\n", code)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. virtual_onnx.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)