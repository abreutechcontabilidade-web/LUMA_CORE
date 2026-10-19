import os, shutil, time, py_compile, glob

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
baks = glob.glob(path + ".bak_hard_*")
baks.sort(key=os.path.getmtime, reverse=True)

if not baks:
    print("[ERRO] Backup nao encontrado.")
    exit(1)

bak = baks[0]
print(f"[OK] Lendo backup: {bak}")

with open(bak, "r", encoding="utf-8") as f:
    linhas_bak = f.readlines()

main_block = []
in_main = False
for line in linhas_bak:
    if 'if __name__ == "__main__":' in line:
        in_main = True
    if in_main:
        main_block.append(line)

if not main_block:
    print("[ERRO] Nao achei o bloco __main__ no backup.")
    exit(1)

with open(path, "a", encoding="utf-8") as f:
    f.write("\n")
    for line in main_block:
        f.write(line)
        
print("[OK] Bloco de ignicao (__main__) restaurado.")
    
try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. Pronto para ligar.")
except Exception as e:
    print(f"[FALHA] {e}")