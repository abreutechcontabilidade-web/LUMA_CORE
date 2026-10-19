import sys
sys.path.insert(0, r'C:\Users\user\Desktop\LUMA_CORE')
from intelligence.key_ring import KeyRing

ring = KeyRing(r'C:\Users\user\Desktop\LUMA_CORE\intelligence\vault.json')
if ring.keys:
    print(f'[TESTE] Chave 1: {ring.get_key()[:10]}...')
    print(f'[TESTE] Chave 2: {ring.get_key()[:10]}...')
    print(f'[TESTE] Chave 3: {ring.get_key()[:10]}...')
else:
    print('[TESTE] O KeyRing está vazio. As chaves não foram extraídas.')