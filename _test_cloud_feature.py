import sys, os
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE")
sys.path.insert(0, r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib")
from intelligence.fallback import gerar_com_fallback

prompt_teste = (
    "Gere APENAS o codigo HTML e JavaScript para um placar (Jogador X, Empates, Jogador O) "
    "e um historico de partidas. NAO inclua o tabuleiro. "
    "Retorne APENAS um JSON valido: {\"feature\": \"<html/js do placar e historico>\"}. "
    "Sem markdown, sem explicacoes."
)

print("[TESTE] A chamar a Nuvem com o prompt de feature...")
res, provider, _ = gerar_com_fallback(prompt_teste)

if res:
    print(f"\n[PROVIDER] {provider}")
    print(f"[RESPOSTA BRUTA]:\n{res[:1000]}...")
else:
    print("[ERRO] A Nuvem nao devolveu resposta.")