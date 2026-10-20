import sys
import os
import webbrowser

# Adiciona o diretorio ao path
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")

try:
    from intelligence.github_learner import aprender_do_github
    from intelligence.mutador_stilb_v1 import aplicar_mutacoes
except Exception as e:
    print(f"[ERRO] Falha ao importar modulos: {e}")
    sys.exit(1)

print("[GERADOR] A procurar o jogo no GitHub (Web Learner)...")
html_original, proveniencia = aprender_do_github("jogo da cobra")

if not html_original:
    print("[ERRO] O Web Learner nao conseguiu descarregar o jogo. Verifique a rede/Token.")
    sys.exit(1)

print(f"[GERADOR] Jogo descarregado ({len(html_original)} bytes). A aplicar a mutacao STILB...")

prompt = "criar jogo da cobra cyberpunk com fundo neon e mais velocidade"
html_mutado, mutacoes = aplicar_mutacoes(html_original, prompt)

print(f"[GERADOR] Mutacoes aplicadas: {mutacoes}")

# Gravar o ficheiro final sem BOM
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
final_path = os.path.join(desktop, "jogo_cobra_CTO_ISOLADO.html")

with open(final_path, "w", encoding="utf-8") as f:
    f.write(html_mutado)

print(f"[SUCESSO ABSOLUTO] Jogo guardado em: {final_path}")
print("A abrir o navegador...")
webbrowser.open(f"file:///{final_path.replace(chr(92), '/')}")