import os, re, shutil, py_compile, time

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_sensei_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Verifica se o método já existe
if "def aprender_da_nuvem" in code:
    print("[AVISO] O metodo 'aprender_da_nuvem' ja existe no arquivo.")
else:
    # Procura o final da classe VirtualONNX (ou o início de outra classe)
    # Vamos inserir logo antes do método processar (ou no final da classe)
    target = "    def processar(self, prompt: str):"
    if target in code:
        novo_metodo = '''    def aprender_da_nuvem(self, prompt: str, html: str):
        """Salva o conhecimento da nuvem e as features na memoria local."""
        import os, json
        from intelligence.feature_engine import extrair_intencao, extrair_features
        
        intent = extrair_intencao(prompt)
        features = extrair_features(prompt)
        
        # Atualiza a memoria
        self.dynamic_tools[intent] = {"html": html, "features": features}
        
        # Salva no disco
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.dynamic_tools, f, ensure_ascii=False, indent=2)
            print(f"[FUSAO] Ouro guardado: '{intent}' | Features: {features}")
        except Exception as e:
            print(f"[FUSAO] Erro ao guardar: {e}")

'''
        code = code.replace(target, novo_metodo + target)
        print("[OK] Metodo 'aprender_da_nuvem' injetado com sucesso.")
    else:
        # Fallback: anexa ao final do arquivo com indentação de classe
        code += "\n    def aprender_da_nuvem(self, prompt, response):\n        print('[FUSAO] Metodo fallback acionado')\n        return True\n"
        print("[AVISO] Metodo injetado no final (fallback).")

# Escreve o arquivo atualizado
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] Sintaxe do virtual_onnx.py validada.")
except Exception as e:
    print(f"[FALHA] Erro de sintaxe: {e}")
    shutil.copy2(bak, path)
    sys.exit(1)