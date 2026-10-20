import os, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v94_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Importa o mutador no topo
if "from intelligence.mutador_stilb_v1 import aplicar_mutacoes" not in code:
    code = code.replace("from intelligence.onnx_sovereign import", "from intelligence.mutador_stilb_v1 import aplicar_mutacoes\nfrom intelligence.onnx_sovereign import")

# Blindagem: Aplica a mutação em TODOS os retornos de HTML
# Nível 1 (Cache)
code = code.replace(
    'self._send_json({"status": "success", "html": html_atual, "fonte": "ONNX_CACHE_PURO", "elapsed_ms": elapsed})',
    'html_mutado, _muts = aplicar_mutacoes(html_atual, prompt)\n                self._send_json({"status": "success", "html": html_mutado, "fonte": "ONNX_CACHE_PURO", "elapsed_ms": elapsed})'
)
# Nível 3 (Web Learner)
code = code.replace(
    'self._send_json({"status": "success", "html": codigo_web, "fonte": "WEB_LEARNER", "elapsed_ms": elapsed})',
    'html_mutado, _muts = aplicar_mutacoes(codigo_web, prompt)\n                self._send_json({"status": "success", "html": html_mutado, "fonte": "WEB_LEARNER", "elapsed_ms": elapsed})'
)
# Nível 4 (Autopoiese)
code = code.replace(
    'self._send_json({"status": "success", "html": fallback_html, "fonte": "AUTOPOIESE_LOCAL", "elapsed_ms": elapsed})',
    'html_mutado, _muts = aplicar_mutacoes(fallback_html, prompt)\n                self._send_json({"status": "success", "html": html_mutado, "fonte": "AUTOPOIESE_LOCAL", "elapsed_ms": elapsed})'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] app.py blindado. O mutador v1.4 atua na entrega final.")