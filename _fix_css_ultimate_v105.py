import os, shutil, time, py_compile, re, json

mut_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\mutador_local_v1.py"
bak = mut_path + ".bak_ultimate_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(mut_path, bak)

with open(mut_path, "r", encoding="utf-8") as f:
    code = f.read()

# O CSS SUPREMO (v1.5): Domina todas as janelas, botoes e o canvas
new_css = r'''_CSS = (
    '<style id="' + _MUT_STYLE + '">\n'
    'html,body{background-color:#050510 !important;color:#00ffe1 !important}\n'
    '/* 1. Forca todos os containers, cartoes e modais a serem escuros */\n'
    'div, main, section, .arena, .card, .container, header, footer, .score-board, .stat-box, .modal, .modal-content, .dialog, [role="dialog"], .preferences-panel, .achievement-item {\n'
    '  background-color: #0f172a !important;\n'
    '  background-image: none !important;\n'
    '  border-color: #38bdf8 !important;\n'
    '  color: #f8fafc !important;\n'
    '}\n'
    '/* 2. Forca o Canvas (tabuleiro) a inverter as cores */\n'
    'canvas {\n'
    '  filter: invert(1) hue-rotate(180deg) brightness(1.2) contrast(1.2) !important;\n'
    '  background-color: #0a0a1a !important;\n'
    '  border: 2px solid #ff2fd6 !important;\n'
    '  box-shadow: 0 0 20px #ff2fd6, inset 0 0 10px #00ffe1 !important;\n'
    '}\n'
    '/* 3. Cores dos textos */\n'
    'h1,h2,h3,p,span,div,label { color: #e0f7ff !important; text-shadow: 0 0 4px #00ffe1 !important; }\n'
    'h1,h2,h3 { color: #ff2fd6 !important; text-shadow: 0 0 10px #ff2fd6 !important; }\n'
    '/* 4. Botoes normais e BOTOES DE FECHAR */\n'
    'button, .btn, .close, .close-btn, button[aria-label="Close"], button:has(svg) {\n'
    '  background-color: #1a1a2e !important;\n'
    '  color: #00ffe1 !important;\n'
    '  border: 1px solid #00ffe1 !important;\n'
    '  box-shadow: 0 0 10px #00ffe1 !important;\n'
    '  border-radius: 4px !important;\n'
    '}\n'
    'button:hover, .btn:hover, .close:hover { background-color: #ff2fd6 !important; color: #000 !important; }\n'
    '</style>'
)'''

pattern = r"_CSS = \([\s\S]*?\)"
code = re.sub(pattern, new_css, code, count=1)

with open(mut_path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(mut_path, doraise=True)
print("[OK] mutador_local_v1.py atualizado para v1.5 (Dominação Total).")

# Limpar o cache para forçar a re-mutação
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

keys_to_remove = [k for k in mem.keys() if "cobr" in k.lower()]
for k in keys_to_remove:
    del mem[k]

tmp = db_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp, db_path)
print("[OK] Genoma limpo para forçar a re-mutação.")