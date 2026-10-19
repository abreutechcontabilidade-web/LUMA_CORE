import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_hooks_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Adiciona ganchos ao Jogo da Velha (Básico e Premium)
# 1. HTML: Antes do fecho do app-container
code = code.replace("            </div>\n            <script>", "            </div>\n            <!-- [HOOK_EXTRA_PANELS] -->\n            <script>")
# 2. JS: Dentro da funcao play, apos a logica existente
code = code.replace("                    }\n                }\n                function checkWin()", "                    }\n                    // [HOOK_AFTER_PLAY]\n                }\n                function checkWin()")

# Adiciona ganchos a Calculadora
code = code.replace("    def _gerar_calculadora_cientifica(self):\n        return \"\"\"<div style='background:#1e293b; padding:20px;", "    def _gerar_calculadora_cientifica(self):\n        return \"\"\"<div style='background:#1e293b; padding:20px;")
# Gancho HTML no fim do container da calculadora
code = code.replace("            </div>\n            <script>\n                let cStr = \"\";", "            </div>\n            <!-- [HOOK_EXTRA_PANELS] -->\n            <script>\n                let cStr = \"\";")
# Gancho JS apos o resultado
code = code.replace("                    catch(e) { document.getElementById(\"calc-display\").value = \"Erro\"; cStr = \"\"; }\n                }", "                    catch(e) { document.getElementById(\"calc-display\").value = \"Erro\"; cStr = \"\"; }\n                    // [HOOK_AFTER_PLAY]\n                }")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. Ganchos adicionados ao virtual_onnx.py.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)