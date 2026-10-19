import re, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_fixnames_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Encontrar o bloco processar atual (o que tem os self._gerar_jogo_da_velha())
old_proc = re.search(r"    def processar\(self, prompt: str\):[\s\S]*?(?=    def aprender)", code)
if not old_proc:
    print("[ERRO] processar() nao encontrado.")
    sys.exit(1)

novo_proc = '''    def processar(self, prompt: str):
        from onnx_sota import compor_chave
        info = compor_chave(prompt)
        intencao_base = info["intencao"]
        features_pedidas = set(info["features"])
        posicoes_pedidas = set(info["posicoes"])

        # Mutacao forçada
        norm = prompt.lower()
        palavras_mutacao = ["mudar", "alterar", "mover", "trocar", "passar"]
        if any(k in norm for k in palavras_mutacao) and (features_pedidas or posicoes_pedidas):
            print(f"[ONNX-SOTA] Mutacao detetada para '{intencao_base}'.")
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
                    print(f"[ONNX-SOTA] Versao cobre o pedido (intencao='{intencao_base}').")
                    return versao["html"], f"APRENDIDO_{intencao_base}"
            if entry["versoes"]:
                mais_avancada = max(entry["versoes"], key=lambda v: len(v.get("features", [])))
                print(f"[ONNX-SOTA] Devolvendo base incompleta para '{intencao_base}'.")
                return mais_avancada["html"], f"BASE_INCOMPLETA_{intencao_base}"

        # Fallbacks com os nomes CORRETOS (com sufixo _slots)
        if intencao_base == "jogo_da_velha":
            return self._gerar_jogo_da_velha_slots(), "LOCAL_BASIC"
        if intencao_base == "calculadora":
            return self._gerar_calculadora_slots(), "LOCAL_BASIC"
        if intencao_base == "cronometro":
            return self._gerar_cronometro_slots(), "LOCAL_BASIC"
        if intencao_base == "pomodoro":
            return self._gerar_pomodoro_slots(), "LOCAL_BASIC"

        return SCAFFOLD_SLOTS, "SCAFFOLD_VAZIO"

'''

# Substituir o bloco inteiro
inicio = old_proc.start()
fim = old_proc.end()
code = code[:inicio] + novo_proc + code[fim:]

# 2. Garantir que os métodos existem (se nao existirem, criar stubs minimos)
metodos_faltantes = {
    "_gerar_jogo_da_velha_slots": 'return "<div>Jogo da Velha (stub)</div>"',
    "_gerar_calculadora_slots": 'return "<div>Calculadora (stub)</div>"',
    "_gerar_cronometro_slots": 'return "<div>Cronometro (stub)</div>"',
    "_gerar_pomodoro_slots": 'return "<div>Pomodoro (stub)</div>"',
}

for nome, corpo in metodos_faltantes.items():
    if f"def {nome}(self)" not in code:
        # Inserir antes de "def aprender"
        stub = f'''
    def {nome}(self):
        {corpo}

'''
        code = code.replace("    def aprender", stub + "    def aprender", 1)
        print(f"[OK] Metodo {nome} criado (stub).")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. virtual_onnx.py corrigido.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)