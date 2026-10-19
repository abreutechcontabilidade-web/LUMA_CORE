
import difflib
import re

def buscar_no_genoma(prompt, memoria):
    if not memoria:
        return None, 0.0
        
    melhor_chave = None
    melhor_score = 0.0
    
    # O FIX REAL: [a-z0-9]+ quebra underscores e espacos, ignorando pontuacao
    tokens_prompt = re.findall(r'[a-z0-9]+', prompt.lower())
    p_clean = " ".join(tokens_prompt)

    for chave, entry in memoria.items():
        tokens_chave = re.findall(r'[a-z0-9]+', chave.lower())
        k_clean = " ".join(tokens_chave)
        
        score = difflib.SequenceMatcher(None, p_clean, k_clean).ratio()
        
        if score > melhor_score:
            melhor_score = score
            melhor_chave = chave

    return melhor_chave, melhor_score
