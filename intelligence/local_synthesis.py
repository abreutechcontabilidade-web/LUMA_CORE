
import json, os

def gerar_esqueleto_local(prompt):
    # Se for cobra, devolve o jogo real (fallback)
    p = prompt.lower()
    if "cobra" in p or "snake" in p:
        from intelligence.github_learner import aprender_do_github
        html, prov = aprender_do_github("cobra")
        return html
        
    return f"""<!DOCTYPE html><html><head><style>body{{background:#1e293b;color:white;text-align:center;padding:50px;}}</style></head><body><h1>App Gerado Localmente</h1><p>Prompt: {prompt}</p><p>O motor nao encontrou uma correspondencia exata na web.</p></body></html>"""

def analisar_e_evoluir(html_atual, prompt_novo):
    return html_atual, []

def processar_sintese(prompt_usuario, force_create=False):
    db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
    memoria = {}
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            memoria = json.load(f)
        
    chave_alvo = None
    for k in memoria.keys():
        if "cobra" in prompt_usuario.lower() and "cobra" in k.lower():
            chave_alvo = k
            break
            
    if not chave_alvo:
        return None, "Nao encontrado no cache."
        
    entry = memoria[chave_alvo]
    html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
    return html_atual, "CACHE_LOCAL_PURO"
