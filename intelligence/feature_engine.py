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
    if "velha" in p or "tic tac toe" in p: return "jogo_da_velha"
    if "calculadora" in p or "calcular" in p: return "calculadora"
    return "desconhecido"

def extrair_features(prompt: str) -> list:
    p = prompt.lower()
    f = []
    if "cor" in p or "vermelho" in p: f.append("cor_vermelha")
    if "som" in p: f.append("som")
    return f