import os
import shutil
import time
import py_compile
import ast

path = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\virtual_onnx.py"
bak = path + ".bak_quantum_" + time.strftime("%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# O bloco correto e perfeito que deve existir
correct_block = [
    "try:\n",
    "    from intelligence.feature_engine import extrair_intencao, extrair_features\n",
    "except ImportError:\n",
    "    def extrair_intencao(p): return p.lower().strip()\n",
    "    def extrair_features(p): return []\n"
]

# Encontra o índice onde o bloco quebrado começa
start_idx = -1
for i, line in enumerate(lines):
    if "from intelligence.feature_engine import extrair_intencao" in line:
        # Olha para trás para achar o "try:"
        if i > 0 and lines[i-1].strip() == "try:":
            start_idx = i - 1
            break
        else:
            start_idx = i # Caso o try esteja lá mas sem quebra
            break

if start_idx != -1:
    # Remove as linhas erradas (geralmente 5 a 7 linhas do try/except quebrado)
    # Vamos deletar até encontrar uma linha que não pertença ao bloco
    end_idx = start_idx + 1
    while end_idx < len(lines) and (lines[end_idx].strip() == "" or "import" in lines[end_idx] or "def extrair" in lines[end_idx] or "except" in lines[end_idx]):
        end_idx += 1
    
    # Substitui o bloco malformado pelo bloco perfeito
    lines[start_idx:end_idx] = correct_block
    print(f"[OK] Bloco de importação corrigido nas linhas {start_idx+1} a {end_idx}.")
else:
    print("[AVISO] Não foi possível encontrar o bloco do feature_engine. Inserindo no início do arquivo.")
    # Se não achou, insere no topo (logo após os imports de sistema)
    lines.insert(0, "\n".join(correct_block))

# Escreve o arquivo final
with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] SUCESSO ABSOLUTO! Sintaxe do virtual_onnx.py é agora válida.")
except Exception as e:
    print(f"[FALHA] Ainda há um erro de sintaxe: {e}")
    shutil.copy2(bak, path)
    print("[OK] Backup restaurado.")