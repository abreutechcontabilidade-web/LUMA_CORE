import os, shutil, time, py_compile

mut_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\mutador_local_v1.py"
bak = mut_path + ".bak_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(mut_path, bak)

with open(mut_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Substituir o bloco CSS para forçar o escurecimento do canvas
old_css = """_CSS = (
    '<style id="' + _MUT_STYLE + '">\\n'
    'html,body{background:#050510 !important;color:#e0f7ff !important}\\n'
    'canvas{background:#0a0a1a !important;border:2px solid #00ffe1 !important;box-shadow:0 0 24px #ff2fd6, inset 0 0 12px #001a1a !important;filter:invert(0.9) hue-rotate(180deg) saturate(1.8) !important}\\n'
    'button,.btn{background:#0a0a1a !important;color:#00ffe1 !important;border:1px solid #ff2fd6 !important;text-shadow:0 0 6px #00ffe1 !important}\\n'
    'h1,h2,h3,p{color:#ff2fd6 !important;text-shadow:0 0 10px #ff2fd6 !important}\\n'
    '</style>'
)"""

new_css = """_CSS = (
    '<style id="' + _MUT_STYLE + '">\\n'
    'html,body{background:#050510 !important;color:#e0f7ff !important}\\n'
    /* Forca o canvas a ser escuro e aplica blend mode */
    'canvas{background:#0a0a1a !important;border:2px solid #00ffe1 !important;box-shadow:0 0 24px #ff2fd6 !important; filter: invert(1) hue-rotate(180deg) brightness(0.8) contrast(1.5) !important; mix-blend-mode: screen !important;}\\n'
    'button,.btn{background:#0a0a1a !important;color:#00ffe1 !important;border:1px solid #ff2fd6 !important;text-shadow:0 0 6px #00ffe1 !important}\\n'
    'h1,h2,h3,p{color:#ff2fd6 !important;text-shadow:0 0 10px #ff2fd6 !important}\\n'
    '</style>'
)"""

if old_css in code:
    code = code.replace(old_css, new_css)
    print("[OK] CSS do canvas atualizado para forcar o modo escuro.")
else:
    # Tenta substituicao mais flexivel
    import re
    code = re.sub(r"filter:invert\([^)]*\).*?!important", "filter: invert(1) hue-rotate(180deg) brightness(0.8) contrast(1.5) !important; mix-blend-mode: screen !important;", code)
    print("[OK] CSS do canvas atualizado via regex.")

with open(mut_path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(mut_path, doraise=True)
print("[OK] mutador_local_v1.py reescrito e compilado.")