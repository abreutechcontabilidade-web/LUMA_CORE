import os, re, shutil, py_compile, time

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
ONNX = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_bridge.py"

# 1. Reparar o onnx_bridge.py (Adicionar a função fantasma para não crashar)
with open(ONNX, "w", encoding="utf-8") as f:
    f.write("from intelligence.mutador_stilb_v1 import aplicar_mutacoes, _stilb_mutar_seguro\n")
    f.write("def inferir_mutacao(prompt): return []\n")

with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# 2. Remover o import quebrado de dentro do do_POST
code = re.sub(r'^\s*from intelligence\.onnx_bridge import.*$', '', code, flags=re.M)

# 3. Corrigir as chamadas antigas que passavam 'mutacoes' em vez de 'prompt'
code = code.replace("html_evoluido = aplicar_mutacoes(html_atual, mutacoes)", "html_evoluido = _stilb_mutar_seguro(html_atual, prompt)")
code = code.replace("html_auto = aplicar_mutacoes(html_auto, mutacoes_auto)", "html_auto = _stilb_mutar_seguro(html_auto, prompt)")

# 4. Garantir o import correto no topo
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes, _stilb_mutar_seguro" not in code:
    code = code.replace("import json", "import json\nfrom intelligence.mutador_stilb_v1 import aplicar_mutacoes, _stilb_mutar_seguro", 1)

tmp = APP + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(code)

if os.path.exists(tmp):
    try:
        py_compile.compile(tmp, doraise=True)
        bak = APP + ".bak_v111_" + time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(APP, bak)
        os.replace(tmp, APP)
        print("[OK] app.py e onnx_bridge.py cirurgicamente corrigidos e compilados.")
    except Exception as e:
        os.remove(tmp)
        print(f"[CRITICO] Compilacao falhou: {e}")