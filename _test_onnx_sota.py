import sys
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE\intelligence")
from onnx_sota import compor_chave, inspecionar

prompts_teste = [
    "criar jogo da velha",
    "criar jogo da velha com placar",
    "criar jogo da velha com placar na parte inferior",
    "criar jogo da velha com placar na base e historico",
    "criar jogo da velha com placar no topo, cores e animacao",
    "criar cronometro regressivo de 2 minutos",
    "criar calculadora cientifica com tema escuro",
    "criar pomodoro grande com animacao",
    "criar lista de tarefas com historico",
    "criar snake com placar em cima",
]

print("=" * 70)
print("BATERIA ONNX-SOTA (10 PROMPTS)")
print("=" * 70)
for p in prompts_teste:
    r = compor_chave(p)
    print(f"\nPROMPT: {p}")
    print(f"  Chave:  {r['chave']}")
    print(f"  Intent: {r['intencao']} (categoria: {r['categoria']})")
    print(f"  Feats:  {r['features']}")
    print(f"  Pos:    {r['posicoes']}")
    print(f"  Mods:   {r['modificadores']}")

print("\n" + "=" * 70)
print("CATALOGO")
print("=" * 70)
print(inspecionar("teste")["catalogo"])