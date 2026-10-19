import shutil, time, py_compile, os

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_keyring_fix_" + time.strftime("%H%M%S")
shutil.copy2(path, bak)

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui o caminho errado pelo caminho correto (onde o Inventário provou que o vault está)
vault_wrong = r"C:\Users\user\Desktop\LUMA_CORE\_bancada\motor\lib\vault.json"
vault_correct = r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json"

if vault_wrong in code:
    code = code.replace(vault_wrong, vault_correct)
    print("[OK] Caminho do vault.json corrigido no app.py.")
else:
    print("[AVISO] Caminho antigo não encontrado. Verifique se o app.py já foi alterado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

py_compile.compile(path, doraise=True)
print("[OK] Sintaxe do app.py validada.")