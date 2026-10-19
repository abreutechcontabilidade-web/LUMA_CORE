import json, os

def carregar_memoria(db_path):
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def guardar_memoria(db_path, memoria):
    with open(db_path, "w", encoding="utf-8") as f: json.dump(memoria, f, ensure_ascii=False, indent=2)

def extrair_intencao(prompt: str) -> str:
    p = prompt.lower()
    tags = []
    if "velha" in p or "tic tac toe" in p: tags.append("jogo_da_velha")
    if "placar" in p or "placa" in p: tags.append("placar")
    if "empate" in p: tags.append("empate")
    if "historico" in p or "histórico" in p: tags.append("historico")
    # Nao adiciona "cores" ou "som" na chave base, pois sao features de sintese
    return "_".join(sorted(tags)) if tags else "jogo_da_velha" 

def extrair_features(prompt: str) -> list:
    p = prompt.lower()
    f = []
    if "cor" in p or "vermelho" in p: f.append("cor_vermelha")
    if "som" in p: f.append("som")
    return f