import json
with open(r'C:\Users\user\Desktop\LUMA_CORE\intelligence\dynamic_tools.json', 'r', encoding='utf-8') as f:
    mem = json.load(f)
cobra_keys = [k for k in mem.keys() if 'cobra' in k.lower()]
if cobra_keys:
    print(f'[OK] Jogo guardado no genoma com a chave: {cobra_keys}')
    print(f'   Tamanho do HTML: {len(mem[cobra_keys[0]]["html"])} caracteres.')
else:
    print('[AVISO] Nenhuma chave de cobra encontrada.')