import os, shutil, glob, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
backups = glob.glob(path + ".bak_*")
if backups:
    latest_bak = max(backups, key=os.path.getctime)
    shutil.copy2(latest_bak, path)
    print(f"[OK] app.py restaurado do backup: {latest_bak}")

try:
    py_compile.compile(path, doraise=True)
    print("[OK] app.py esta valido novamente.")
except Exception as e:
    print(f"[AVISO] O backup mais recente tambem tem erro: {e}")