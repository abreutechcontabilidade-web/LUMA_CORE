# -*- coding: utf-8 -*-
"""
LUMA Injector Engine (v37.0)
Injeta features no HTML do Local, respeitando a posicao pedida no prompt.
"""
import re

def detectar_posicao(prompt: str) -> str:
    """Deteta se o utilizador quer a feature no topo ou na parte debaixo."""
    p = prompt.lower()
    if any(k in p for k in ["debaixo", "baixo", "fundo", "rodape", "rodapé", "inferior"]):
        return "bottom"
    if any(k in p for k in ["topo", "cima", "superior", "cabecalho", "cabeçalho"]):
        return "top"
    return "auto"  # Posicao padrao (depende da feature)

def extrair_feature(llm_html: str, feature_name: str) -> str:
    """Extrai um bloco HTML/JS da resposta da LLM para uma feature especifica."""
    # Se a LLM devolveu um JSON, extrai o campo correspondente
    try:
        import json
        data = json.loads(llm_html)
        if isinstance(data, dict) and feature_name in data:
            return data[feature_name]
    except Exception:
        pass
    # Fallback: devolve o HTML inteiro
    return llm_html

def injetar_feature(local_html: str, feature_html: str, posicao: str) -> str:
    """
    Injeta o HTML da feature no Local, na posicao pedida.
    Assume que o Local tem os marcadores [HOOK_TOP] e [HOOK_BOTTOM].
    """
    if not local_html:
        return feature_html

    if posicao == "top":
        if "[HOOK_TOP]" in local_html:
            return local_html.replace("[HOOK_TOP]", feature_html + "\n[HOOK_TOP]")
        else:
            # Insere antes do primeiro <div class="app-container">
            return local_html.replace('<div class="app-container">', '<div class="app-container">\n' + feature_html, 1)
    elif posicao == "bottom":
        if "[HOOK_BOTTOM]" in local_html:
            return local_html.replace("[HOOK_BOTTOM]", feature_html + "\n[HOOK_BOTTOM]")
        else:
            # Insere antes do fecho do <div class="app-container">
            return local_html.replace('</div>', '\n' + feature_html + '\n</div>', 1)
    else:
        # Posicao auto: injeta no hook padrao
        if "[HOOK_TOP]" in local_html:
            return local_html.replace("[HOOK_TOP]", feature_html + "\n[HOOK_TOP]")
        return local_html + "\n" + feature_html