import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_subset_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui a funcao processar para usar a melhor correspondencia
old_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        intent = extrair_intencao(prompt)
        print(f"[ONNX] Prompt: '{prompt[:40]}...' | Intencao: '{intent}' | Memoria: {list(self.dynamic_tools.keys())}")
        
        # PRIORIDADE 1: Memoria Aprendida (se a intencao tiver palavras-chave especificas)
        if intent in self.dynamic_tools and any(k in intent for k in ["placar", "cores", "historico", "empate"]):
            print(f"[ONNX] Usando memoria PRIORITARIA para '{intent}'")
            entry = self.dynamic_tools[intent]
            if isinstance(entry, dict) and "html" in entry:
                return entry["html"], "APRENDIDO_NUVEM_PRIORITY"
            return entry, "APRENDIDO_NUVEM_PRIORITY"'''

new_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        intent = extrair_intencao(prompt)
        tags_pedido = set(intent.split("_"))
        
        # PRIORIDADE 1: Melhor Correspondência (Subset Matching)
        melhor_chave = None
        melhor_score = -1
        melhor_html = None

        for chave, valor in self.dynamic_tools.items():
            tags_memoria = set(chave.split("_"))
            # Quanto maior a interseccao, melhor
            score = len(tags_pedido.intersection(tags_memoria))
            if score > melhor_score:
                melhor_score = score
                melhor_chave = chave
                melhor_html = valor

        # Se encontrou uma correspondencia com pelo menos 2 tags (ex: velha + placar), usa
        if melhor_score >= 2 and melhor_chave:
            print(f"[ONNX] Usando melhor correspondencia: '{melhor_chave}' (score: {melhor_score})")
            if isinstance(melhor_html, dict) and "html" in melhor_html:
                return melhor_html["html"], f"APRENDIDO_SUBSET_{melhor_chave}"
            return melhor_html, f"APRENDIDO_SUBSET_{melhor_chave}"'''

if old_proc in code:
    code = code.replace(old_proc, new_proc)
    print("[OK] processar() atualizado com Subset Matching.")
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