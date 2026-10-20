import os, json, py_compile, shutil

# ==========================================
# 1. ATIVANDO A EDIÇÃO LOCAL NO WEB LEARNER
# ==========================================
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v94"
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Vamos adicionar a injeção de CSS no bloco do Web Learner
old_web = '''            if codigo_web:
                # G-144 FIX: Usar a mesma chave que o ONNX vai procurar
                intent_web = chave_limpa.replace(" ", "_")
                memoria[intent_web] = {"html": codigo_web, "features": ["aprendido_web"], "proveniencia": proveniencia}'''

new_web = '''            if codigo_web:
                # G-144 FIX: Usar a mesma chave que o ONNX vai procurar
                intent_web = chave_limpa.replace(" ", "_")
                
                # --- NOVO: EDICAO LOCAL (FASE 1 BASICA) ---
                # Se o prompt pedir cores, vamos injetar CSS no HTML do Ramazan
                p_lower = prompt.lower()
                if "neon" in p_lower or "cyberpunk" in p_lower:
                    css_neon = "<style>body { background-color: #050510 !important; } .arena { box-shadow: 0 0 20px #ff00ff !important; }</style>"
                    codigo_web = codigo_web.replace("</head>", css_neon + "</head>")
                    print("[EDICAO] CSS Neon injetado no codigo.")
                elif "vermelho" in p_lower or "red" in p_lower:
                    css_red = "<style>body { background-color: #4a0000 !important; }</style>"
                    codigo_web = codigo_web.replace("</head>", css_red + "</head>")
                    print("[EDICAO] CSS Vermelho injetado no codigo.")
                
                memoria[intent_web] = {"html": codigo_web, "features": ["aprendido_web", "editado"], "proveniencia": proveniencia}'''

if old_web in code:
    code = code.replace(old_web, new_web)
    print("[OK] app.py atualizado com o Pipeline de Edicao Local.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Verificando...")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU.")

# ==========================================
# 2. LIMPANDO O GENOMA DA COBRA (Para forçar nova edição)
# ==========================================
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

keys_to_remove = [k for k in mem.keys() if "cobr" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido do genoma: {k}")

tmp = db_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp, db_path)
print("[OK] Genoma limpo para forçar a edicao.")