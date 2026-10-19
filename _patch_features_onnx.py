import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_features_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Importar do feature_engine
if "from intelligence.feature_engine import carregar_memoria, guardar_memoria, extrair_intencao" not in code:
    code = code.replace(
        "import json",
        "import json\nimport sys\nsys.path.insert(0, r'C:\\Users\\user\\Desktop\\LUMA_CORE')\nfrom intelligence.feature_engine import carregar_memoria, guardar_memoria, extrair_intencao"
    )
    print("[OK] Import do feature_engine adicionado.")

# 2. Atualizar o __init__ para usar carregar_memoria
old_init = '''    def __init__(self):
        self.dynamic_tools = {}
        self.db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
        self._load_dynamic_tools()

    def _load_dynamic_tools(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.dynamic_tools = json.load(f)
            except Exception:
                self.dynamic_tools = {}'''

new_init = '''    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
        self.dynamic_tools = carregar_memoria(self.db_path)'''

if old_init in code:
    code = code.replace(old_init, new_init)
    print("[OK] __init__ atualizado para usar feature_engine.")

# 3. Atualizar processar() para ler a estrutura {html, features}
old_proc = '''    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        intent = extrair_intencao(prompt)
        print(f"[ONNX] Prompt: '{prompt[:40]}...' | Intencao: '{intent}' | Memoria: {list(self.dynamic_tools.keys())}")
        
        # PRIORIDADE 1: Memoria Aprendida (se a intencao tiver palavras-chave especificas)
        if intent in self.dynamic_tools and any(k in intent for k in ["placar", "cores", "historico", "empate"]):
            print(f"[ONNX] Usando memoria PRIORITARIA para '{intent}'")
            return self.dynamic_tools[intent], "APRENDIDO_NUVEM_PRIORITY"'''

new_proc = '''    def processar(self, prompt: str):
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

if old_proc in code:
    code = code.replace(old_proc, new_proc)
    print("[OK] processar() atualizado para ler {html, features}.")

# 4. Atualizar aprender_da_nuvem() para guardar {html, features}
old_learn = '''    def aprender_da_nuvem(self, prompt: str, html: str):
        intent = extrair_intencao(prompt)
        self.dynamic_tools[intent] = html
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.dynamic_tools, f, ensure_ascii=False, indent=2)
            print(f"[FUSAO] Ouro guardado na memoria: '{prompt[:30]}...'")
        except Exception as e:
            print(f"[FUSAO] Erro ao guardar: {e}")'''

new_learn = '''    def aprender_da_nuvem(self, prompt: str, html: str):
        intent = extrair_intencao(prompt)
        # Extrai features do prompt
        from intelligence.feature_engine import extrair_features
        features = extrair_features(prompt)
        # Guarda no formato {html, features}
        self.dynamic_tools[intent] = {"html": html, "features": features}
        guardar_memoria(self.db_path, self.dynamic_tools)
        print(f"[FUSAO] Ouro guardado na memoria: '{prompt[:30]}...' (features: {features})")'''

if old_learn in code:
    code = code.replace(old_learn, new_learn)
    print("[OK] aprender_da_nuvem() atualizado para guardar {html, features}.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. virtual_onnx.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)