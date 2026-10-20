import os, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_g138_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# GATE-23: Injeta o import no topo absoluto
if "from intelligence.onnx_sovereign import extrair_chave" not in code:
    header = "import sys\nimport os\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nfrom intelligence.onnx_sovereign import extrair_chave\n"
    code = header + code
    print("[GATE-23] Import 'extrair_chave' injetado no topo do app.py.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O app.py agora tem o import vivo.")