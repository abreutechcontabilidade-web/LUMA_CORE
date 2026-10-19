import re, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_onnx_sota_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substituir a funcao processar inteira
novo_processar = '''    def processar(self, prompt: str):
        from onnx_sota import compor_chave
        info = compor_chave(prompt)
        intencao_base = info["intencao"]
        features_pedidas = set(info["features"])
        posicoes_pedidas = set(info["posicoes"])

        # Mutacao forçada
        norm = prompt.lower()
        palavras_mutacao = ["mudar", "alterar", "mover", "trocar", "passar"]
        if any(k in norm for k in palavras_mutacao) and (features_pedidas or posicoes_pedidas):
            print(f"[ONNX-SOTA] Mutação detetada para '{intencao_base}'.")
            return None, "NUVEM_MUTACAO"

        if not intencao_base:
            return None, "NUVEM_NECESSARIA"

        entry = self.memoria.get(intencao_base)
        if entry and isinstance(entry, dict) and "versoes" in entry:
            for versao in entry["versoes"]:
                feats_v = set(versao.get("features", []))
                pos_v = set(versao.get("posicoes", []))
                feats_ok = features_pedidas.issubset(feats_v)
                pos_ok = posicoes_pedidas.issubset(pos_v) if posicoes_pedidas else True
                
                if feats_ok and pos_ok:
                    print(f"[ONNX-SOTA] Versão cobre o pedido (intencao='{intencao_base}').")
                    return versao["html"], f"APRENDIDO_{intencao_base}"
            if entry["versoes"]:
                mais_avancada = max(entry["versoes"], key=lambda v: len(v.get("features", [])))
                print(f"[ONNX-SOTA] Devolvendo base incompleta para '{intencao_base}'.")
                return mais_avancada["html"], f"BASE_INCOMPLETA_{intencao_base}"

        # Fallbacks
        if intencao_base == "jogo_da_velha":
            return self._gerar_jogo_da_velha(), "LOCAL_BASIC"
        if intencao_base == "calculadora":
            return self._gerar_calculadora(), "LOCAL_BASIC"
        if intencao_base == "cronometro":
            return self._gerar_cronometro(), "LOCAL_BASIC"
        if intencao_base == "pomodoro":
            return self._gerar_pomodoro(), "LOCAL_BASIC"

        return SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO"
'''

# Encontra a funcao processar antiga e substitui
pattern = r'    def processar\(self, prompt: str\):[\s\S]*?(?=    def aprender)'
if re.search(pattern, code):
    code = re.sub(pattern, novo_processar + "\n\n", code)
    print("[OK] processar() substituido para usar ONNX-SOTA.")
else:
    print("[ERRO] Nao foi possivel localizar processar().")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. virtual_onnx.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)