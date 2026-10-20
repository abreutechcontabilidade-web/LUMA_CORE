import os, json, py_compile, shutil

# ==========================================
# 1. ONNX SOVEREIGN (Match Estrito)
# ==========================================
onnx_code = r'''
def extrair_chave(prompt):
    p = prompt.lower()
    if "cobr" in p or "snake" in p: return "jogo da cobra"
    if "velha" in p or "tic" in p: return "jogo da velha"
    if "calculadora" in p or "calculator" in p: return "calculadora"
    if "cronometro" in p or "timer" in p: return "cronometro"
    if "tarefa" in p or "todo" in p: return "lista de tarefas"
    return " ".join(p.split()[:3])

def buscar_no_genoma(prompt, memoria):
    if not memoria:
        return None, 0.0
        
    chave_pedida = extrair_chave(prompt)
    
    # 1. Procura exata
    if chave_pedida in memoria:
        return chave_pedida, 1.0
    if chave_pedida.replace(" ", "_") in memoria:
        return chave_pedida.replace(" ", "_"), 1.0
        
    # 2. Procura por substring estrita (sem difflib)
    if "cobra" in chave_pedida:
        for k in memoria.keys():
            if "cobra" in k.lower() or "snake" in k.lower():
                return k, 1.0
    if "velha" in chave_pedida:
        for k in memoria.keys():
            if "velha" in k.lower() or "tic" in k.lower():
                return k, 1.0
    if "calculadora" in chave_pedida:
        for k in memoria.keys():
            if "calculadora" in k.lower():
                return k, 1.0
                
    return None, 0.0
'''

with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_sovereign.py", "w", encoding="utf-8") as f:
    f.write(onnx_code)
print("[OK] onnx_sovereign.py atualizado com Match Estrito (sem difflib).")

# ==========================================
# 2. LIMPANDO O GENOMA (Para forçar a procura da cobra)
# ==========================================
db_path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json"
shutil.copy2(db_path, db_path + ".bak_v90")
with open(db_path, "r", encoding="utf-8") as f:
    mem = json.load(f)

# Vamos apagar as chaves erradas que ele guardou (jogo da velha base, etc)
keys_to_remove = [k for k in mem.keys() if "velha" in k.lower() or "base" in k.lower()]
for k in keys_to_remove:
    del mem[k]
    print(f"[OK] Removido do genoma: {k}")

tmp_path = db_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(mem, f, ensure_ascii=False, indent=2)
os.replace(tmp_path, db_path)

py_compile.compile(r"C:\Users\user\Desktop\LUMA_CORE\server\app.py", doraise=True)
print("[OK] py_compile PASSOU. O Motor esta limpo.")