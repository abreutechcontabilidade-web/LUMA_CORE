import math

def similaridade_cosseno(v1, v2):
    """O Algoritmo do Spotify (Recomendação)"""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if not magnitude1 or not magnitude2: return 0
    return dot_product / (magnitude1 * magnitude2)

def analisar_dna(sequencia):
    """O Algoritmo do CPF Arbóreo (Bioinformática)"""
    if not sequencia: return {}
    seq = sequencia.upper()
    gc = sum(1 for base in seq if base in 'GC')
    return {
        "tamanho": len(seq),
        "gc_percent": round((gc / len(seq)) * 100, 2),
        "at_percent": round(((len(seq) - gc) / len(seq)) * 100, 2)
    }

def classificar_intencao(prompt):
    """O Orquestrador (Matching de Intenções)"""
    p = prompt.lower()
    if any(x in p for x in ["dna", "fasta", "rna", "genoma"]):
        return "dna"
    if any(x in p for x in ["recomendar", "similar", "match", "spotify"]):
        return "recommend"
    if any(x in p for x in ["jogo", "game", "arcade"]):
        return "game"
    return "unknown"
