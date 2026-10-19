
import difflib

def buscar_no_genoma(prompt, memoria):
    if not memoria:
        return None, 0.0
        
    melhor_chave = None
    melhor_score = 0.0
    p_clean = prompt.lower().replace("_", " ").strip()

    for chave, entry in memoria.items():
        k_clean = chave.lower().replace("_", " ").strip()
        # SequenceMatcher faz a similaridade de forma inteligente
        score = difflib.SequenceMatcher(None, p_clean, k_clean).ratio()
        
        if score > melhor_score:
            melhor_score = score
            melhor_chave = chave

    return melhor_chave, melhor_score
