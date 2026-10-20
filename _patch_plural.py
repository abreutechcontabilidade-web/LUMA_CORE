import os

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
with open(APP, "r", encoding="utf-8") as f:
    code = f.read()

# O alvo exato que a Bancada deixou
alvo = 're.escape(m) + r"(?![a-z0-9])"'
novo = 're.escape(m) + r"s?(?![a-z0-9])"'

if alvo in code:
    code = code.replace(alvo, novo)
    with open(APP, "w", encoding="utf-8") as f:
        f.write(code)
    print("[OK] Regex do GATE-32 atualizada com sucesso (aceita plural).")
else:
    # Fallback caso os espacos estejam diferentes
    alvo2 = 're.escape(m)+r"(?![a-z0-9])"'
    if alvo2 in code:
        code = code.replace(alvo2, novo)
        with open(APP, "w", encoding="utf-8") as f:
            f.write(code)
        print("[OK] Regex do GATE-32 atualizada (formato alternativo).")
    else:
        print("[AVISO] Padrao nao encontrado. O ficheiro pode ter sido alterado novamente.")
