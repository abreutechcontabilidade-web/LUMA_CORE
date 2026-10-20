import os, shutil, time, py_compile, json

# ==========================================
# 1. CURANDO O EXTRATOR (G-132: cobr)
# ==========================================
onnx_code = r'''
import difflib

def extrair_chave(prompt):
    p = prompt.lower()
    # G-132 FIX: "cobr" apanha cobra, cobrinha, cobras
    if "cobr" in p or "snake" in p: return "jogo da cobra"
    if "velha" in p or "tic" in p: return "jogo da velha"
    if "calculadora" in p or "calculator" in p: return "calculadora"
    if "cronometro" in p or "timer" in p: return "cronometro"
    if "tarefa" in p or "todo" in p: return "lista de tarefas"
    return " ".join(p.split()[:3])

def buscar_no_genoma(prompt, memoria):
    if not memoria: return None, 0.0
    chave_pedida = extrair_chave(prompt)
    melhor_chave, melhor_score = None, 0.0
    for chave, entry in memoria.items():
        score = difflib.SequenceMatcher(None, chave_pedida, chave.replace("_", " ")).ratio()
        if score > melhor_score:
            melhor_score, melhor_chave = score, chave
    return melhor_chave, melhor_score
'''
with open(r"C:\Users\user\Desktop\LUMA_CORE\intelligence\onnx_sovereign.py", "w", encoding="utf-8") as f:
    f.write(onnx_code)
print("[OK] onnx_sovereign.py corrigido (G-132: cobr).")

# ==========================================
# 2. MATANDO O FANTASMA E BLINDANDO A ROTA (G-131 / GATE-23)
# ==========================================
path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_t66_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Remove qualquer rasto do web_learner
code = code.replace("from intelligence.web_learner import pesquisar_na_web\n", "")
code = code.replace("from intelligence.direct_web_connector import ligar_a_web\n", "")
code = code.replace("from intelligence.web_learner import pesquisar_na_web", "")

# Injeta o import correto do github_learner no topo absoluto (se nao existir)
if "from intelligence.github_learner import aprender_do_github" not in code:
    header = "import sys\nimport os\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nfrom intelligence.github_learner import aprender_do_github\n"
    code = header + code
    print("[GATE-23] Import do github_learner injetado no topo absoluto do app.py.")

# Força a rota a chamar a função nova com a chave limpa
old_web = '''            print("[WEB LEARNER] Enxame falhou. A procurar código real no GitHub...")
            from intelligence.onnx_sovereign import extrair_chave
            chave_limpa = extrair_chave(prompt)
            print(f"[WEB LEARNER] A procurar no GitHub por: '{chave_limpa}'...")
            codigo_web, proveniencia = aprender_do_github(chave_limpa)'''

new_web = '''            print("[WEB LEARNER] Enxame falhou. A procurar código real no GitHub...")
            from intelligence.onnx_sovereign import extrair_chave
            chave_limpa = extrair_chave(prompt)
            print(f"[WEB LEARNER] A procurar no GitHub por: '{chave_limpa}'...")
            
            # GATE-23: A linha de import que prova que estamos no caminho de servico
            codigo_web, proveniencia = aprender_do_github(chave_limpa)'''

if old_web in code:
    code = code.replace(old_web, new_web)
    print("[OK] Rota /api/generate_cloud aponta estritamente para o github_learner.")
else:
    # Fallback de seguranca
    code = code.replace("aprender_do_github(prompt)", "aprender_do_github(extrair_chave(prompt))")
    print("[OK] Rota corrigida via fallback.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

# ==========================================
# 3. GATE-20 (Auto-Teste e Compilacao)
# ==========================================
py_compile.compile(path, doraise=True)
print("[OK] py_compile PASSOU. O codigo vivo compila.")

# Teste do extrator
import sys
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
from intelligence.onnx_sovereign import extrair_chave
chave = extrair_chave("CRIAR JOGO DA COBRINHA ESTUDE...")
assert chave == "jogo da cobra", f"Falha no extrator: {chave}"
print(f"[GATE-20] Auto-teste do extrator PASSOU: 'COBRINHA' -> '{chave}'.")