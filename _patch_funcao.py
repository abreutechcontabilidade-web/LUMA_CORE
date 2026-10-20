import os, re

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

nova_funcao = """def extrair_chave(prompt):
    p = (prompt or "").lower()
    # Hard match com suporte a plural (s opcional no final)
    for chave, marcas in CHAVES:
        for m in marcas:
            if re.search(r"(?<![a-z0-9])" + re.escape(m) + r"s?(?![a-z0-9])", p):
                return chave
    # Fuzzy match (Levenshtein)
    universo = {}
    for chave, ws in PALAVRAS.items():
        for w in ws: universo[w] = chave
    for w in re.findall(r'[a-z0-9]+', p):
        m = difflib.get_close_matches(w, list(universo.keys()), n=1, cutoff=0.75)
        if m and abs(len(w) - len(m[0])) <= 1:
            return universo[m[0]]
    return ""
"""

# A magia: substitui tudo entre 'def extrair_chave' e 'def decifrar_seguro'
padrao = re.compile(r'def extrair_chave\(prompt\):.*?(?=def decifrar_seguro)', re.DOTALL)
if padrao.search(code):
    code = padrao.sub(nova_funcao + "\n", code)
    with open(APP, "w", encoding="utf-8") as f:
        f.write(code)
    print("[OK] Funcao extrair_chave substituida cirurgicamente.")
else:
    print("[AVISO] Nao foi possivel encontrar a funcao extrair_chave para substituir.")
