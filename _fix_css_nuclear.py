import os, shutil, time, py_compile, re, json

mut_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\mutador_local_v1.py"
bak = mut_path + ".bak_nuclear_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(mut_path, bak)

with open(mut_path, "r", encoding="utf-8") as f:
    code = f.read()

# O CSS NUCLEAR: Força tudo a ser transparente/escuro e aplica o filtro
new_css = r'''_CSS = (
    '<style id="' + _MUT_STYLE + '">\n'
    'html,body{background-color:#050510 !important;color:#00ffe1 !important}\n'
    '/* Limpa os fundos brancos dos divs do Ramazan */\n'
    'div, main, section, .arena, .card, .container, header, footer, .score-board, .modal-content {\n'
    '  background-color: transparent !important;\n'
    '  background-image: none !important;\n'
    '  border-color: #ff2fd6 !important;\n'
    '  box-shadow: none !important;\n'
    '}\n'
    '/* O Canvas (tabuleiro) tem de ser escuro e brilhar */\n'
    'canvas {\n'
    '  background-color: #0a0a1a !important;\n'
    '  border: 2px solid #ff2fd6 !important;\n'
    '  box-shadow: 0 0 20px #ff2fd6, inset 0 0 10px #00ffe1 !important;\n'
    '  filter: invert(0.9) hue-rotate(180deg) !important;\n'
    '}\n'
    '/* Cores dos textos */\n'
    'h1,h2,h3,p,span,div,label { color: #e0f7ff !important; text-shadow: 0 0 4px #00ffe1 !important; }\n'
    'h1,h2,h3 { color: #ff2fd6 !important; text-shadow: 0 0 10px #ff2fd6 !important; }\n'
    '/* Botoes */\n'
    'button,.btn{background:#1a1a2e !important;color:#00ffe1 !important;border:1px solid #00ffe1 !important;}\n'
    '</style>'
)'''

# Substitui o bloco CSS antigo
pattern = r"_CSS = \([\s\S]*?\)"
code = re.sub(pattern, new_css, code, count=1)

with open(mut_path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(mut_path, doraise=True)
print("[OK] mutador_local_v1.py atualizado com o CSS Nuclear (Tudo Escuro).")

# Limpar o cache do jogo para forçar o motor a aplicar o novo CSS
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