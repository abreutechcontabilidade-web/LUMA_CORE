import sys
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE\intelligence")
from slot_engine import SCAFFOLD_SLOTS, aplicar_delta
import json

delta_teste = json.dumps({
    "target_slot": "slot-main",
    "action": "replace_inner",
    "html": "<h2>Jogo da Velha</h2><div id='board'>...</div>",
    "css_delta": "#board { display: grid; grid-template-columns: repeat(3, 80px); gap: 8px; }",
    "js_hooks": {"play": "function play(i) { console.log('jogada ' + i); }"}
})

novo, msg = aplicar_delta(SCAFFOLD_SLOTS, delta_teste)
print(f"[TESTE] Resultado: {msg}")
if novo:
    assert "<h2>Jogo da Velha</h2>" in novo
    assert "#board { display: grid" in novo
    assert "function play(i)" in novo
    print("[TESTE] OK: HTML, CSS e JS foram injetados nos slots corretos.")
else:
    print("[TESTE] FALHOU.")