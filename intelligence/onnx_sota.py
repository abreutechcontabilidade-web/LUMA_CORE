# -*- coding: utf-8 -*-
"""
LUMA ONNX-SOTA (v1.0)
Motor de Ontologia Universal - o dicionário vivo do ecossistema.
Mapeia prompts em: intenção-base + features + posições + modificadores.
"""
import unicodedata

# ═══════════════════════════════════════════════════════════════════
# 1. ONTOLOGIA BASE (Intents por categoria)
# ═══════════════════════════════════════════════════════════════════
ONTOLOGIA = {
    "jogos": {
        "jogo_da_velha": {"keywords": ["jogo da velha", "tic tac toe", "velha", "jogo velha"]},
        "snake": {"keywords": ["snake", "cobra", "cobrinha", "jogo da cobra"]},
        "tetris": {"keywords": ["tetris", "blocos", "jogo dos blocos"]},
        "jogo_da_forca": {"keywords": ["forca", "hangman", "jogo da forca"]},
        "pong": {"keywords": ["pong", "ping pong"]},
        "memoria": {"keywords": ["jogo da memoria", "memoria", "memory"]},
    },
    "ferramentas": {
        "calculadora": {"keywords": ["calculadora", "calc", "calculadora cientifica", "calculadora romana"]},
        "cronometro": {"keywords": ["cronometro", "cronometro regressivo", "timer", "temporizador", "contagem"]},
        "pomodoro": {"keywords": ["pomodoro"]},
        "gerador_senha": {"keywords": ["gerador de senha", "password", "senha"]},
        "conversor": {"keywords": ["conversor", "converter", "conversao"]},
    },
    "produtividade": {
        "lista_tarefas": {"keywords": ["lista de tarefas", "todo", "to-do", "tarefas"]},
        "kanban": {"keywords": ["kanban", "quadro"]},
        "notas": {"keywords": ["notas", "notes", "bloco de notas"]},
    },
    "dashboards": {
        "dashboard": {"keywords": ["dashboard", "painel"]},
        "relogio": {"keywords": ["relogio", "relógio", "clock", "hora"]},
        "calendario": {"keywords": ["calendario", "calendário", "agenda"]},
    },
}

# ═══════════════════════════════════════════════════════════════════
# 2. FEATURES (Funcionalidades)
# ═══════════════════════════════════════════════════════════════════
FEATURES = {
    "placar": {"keywords": ["placar", "pontuacao", "score", "pontos", "marcador"]},
    "empate": {"keywords": ["empate", "velha", "draw", "tie"]},
    "historico": {"keywords": ["historico", "historico", "log", "registro", "history"]},
    "cores": {"keywords": ["cor", "cores", "colorido", "colorir", "vermelho", "azul", "verde", "amarelo", "roxo", "rosa"]},
    "animacao": {"keywords": ["animacao", "animacao", "anime", "transicao", "transicao", "piscar", "brilho"]},
    "som": {"keywords": ["som", "audio", "audio", "sound", "barulho", "efeito sonoro"]},
    "proxima_rodada": {"keywords": ["proxima", "proxima", "nova", "reiniciar", "reinicio", "replay", "nova rodada"]},
    "zerar": {"keywords": ["zerar", "reset", "limpar", "apagar"]},
    "dificuldade": {"keywords": ["dificuldade", "nivel", "nivel", "facil", "medio", "dificil"]},
    "tempo_limite": {"keywords": ["tempo limite", "limite de tempo", "timeout"]},
}

# ═══════════════════════════════════════════════════════════════════
# 3. POSIÇÕES
# ═══════════════════════════════════════════════════════════════════
POSICOES = {
    "topo": {"keywords": ["topo", "cima", "superior", "acima", "header", "cabecalho", "cabeçalho", "top"]},
    "baixo": {"keywords": ["baixo", "fundo", "inferior", "abaixo", "footer", "rodape", "rodapé", "bottom", "base"]},
    "esquerda": {"keywords": ["esquerda", "left", "lateral esquerda"]},
    "direita": {"keywords": ["direita", "right", "lateral direita"]},
    "centro": {"keywords": ["centro", "meio", "middle", "central"]},
}

# ═══════════════════════════════════════════════════════════════════
# 4. MODIFICADORES
# ═══════════════════════════════════════════════════════════════════
TAMANHOS = {
    "grande": ["grande", "big", "maior", "enorme"],
    "pequeno": ["pequeno", "small", "menor", "mini"],
    "medio": ["medio", "medio", "medium", "normal", "padrao", "padrao"],
}
ESTILOS = {
    "escuro": ["escuro", "dark", "preto", "sombrio"],
    "claro": ["claro", "light", "branco", "luminoso"],
    "neon": ["neon", "brilhante", "glow", "brilho"],
}

# ═══════════════════════════════════════════════════════════════════
# 5. NORMALIZAÇÃO
# ═══════════════════════════════════════════════════════════════════
def _norm(texto):
    texto = unicodedata.normalize("NFKC", texto).lower()
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return texto

def _match(texto_norm, keywords):
    return any(_norm(k) in texto_norm for k in keywords)

# ═══════════════════════════════════════════════════════════════════
# 6. DETETORES
# ═══════════════════════════════════════════════════════════════════
def detectar_intencao(prompt):
    p = _norm(prompt)
    melhores = []
    for categoria, intents in ONTOLOGIA.items():
        for nome, config in intents.items():
            score = sum(1 for kw in config.get("keywords", []) if _norm(kw) in p)
            if score > 0:
                melhores.append({"categoria": categoria, "intencao": nome, "score": score})
    if not melhores:
        return None
    melhores.sort(key=lambda x: -x["score"])
    return melhores[0]

def detectar_features(prompt):
    p = _norm(prompt)
    return [nome for nome, cfg in FEATURES.items() if _match(p, cfg["keywords"])]

def detectar_posicoes(prompt):
    p = _norm(prompt)
    return [nome for nome, cfg in POSICOES.items() if _match(p, cfg["keywords"])]

def detectar_modificadores(prompt):
    p = _norm(prompt)
    mods = {"tamanho": None, "estilo": None}
    for t, kws in TAMANHOS.items():
        if _match(p, kws): mods["tamanho"] = t; break
    for e, kws in ESTILOS.items():
        if _match(p, kws): mods["estilo"] = e; break
    return mods

# ═══════════════════════════════════════════════════════════════════
# 7. COMPOSITOR DE CHAVE
# ═══════════════════════════════════════════════════════════════════
def compor_chave(prompt):
    intencao = detectar_intencao(prompt)
    if not intencao:
        return {
            "chave": "desconhecido",
            "intencao": None,
            "categoria": None,
            "features": [],
            "posicoes": [],
            "modificadores": {},
        }
    features = sorted(detectar_features(prompt))
    posicoes = sorted(detectar_posicoes(prompt))
    mods = detectar_modificadores(prompt)
    
    partes = [intencao["intencao"]]
    if features: partes.append("_".join(features))
    if posicoes: partes.append("_".join(posicoes))
    if mods.get("tamanho"): partes.append(mods["tamanho"])
    if mods.get("estilo"): partes.append(mods["estilo"])
    
    return {
        "chave": "__".join(partes),
        "intencao": intencao["intencao"],
        "categoria": intencao["categoria"],
        "features": features,
        "posicoes": posicoes,
        "modificadores": mods,
    }

# ═══════════════════════════════════════════════════════════════════
# 8. INSPEÇÃO (Raio-X)
# ═══════════════════════════════════════════════════════════════════
def inspecionar(prompt):
    return {
        "prompt_original": prompt,
        "prompt_normalizado": _norm(prompt),
        "deteccao": compor_chave(prompt),
        "catalogo": {
            "total_intents": sum(len(v) for v in ONTOLOGIA.values()),
            "total_features": len(FEATURES),
            "total_posicoes": len(POSICOES),
            "total_modificadores": len(TAMANHOS) + len(ESTILOS),
        }
    }

# ═══════════════════════════════════════════════════════════════════
# 9. APRENDIZADO DINÂMICO
# ═══════════════════════════════════════════════════════════════════
def adicionar_intencao(categoria, nome, keywords):
    if categoria not in ONTOLOGIA:
        ONTOLOGIA[categoria] = {}
    ONTOLOGIA[categoria][nome] = {"keywords": keywords}

def adicionar_feature(nome, keywords):
    FEATURES[nome] = {"keywords": keywords}

def adicionar_posicao(nome, keywords):
    POSICOES[nome] = {"keywords": keywords}