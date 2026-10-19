
import json, re, os

def gerar_esqueleto_local(prompt):
    p = prompt.lower()
    if "cobra" in p or "snake" in p:
        return """<!DOCTYPE html><html><head><style>body{background:#1e293b;color:white;display:flex;justify-content:center;align-items:center;height:100vh;} canvas{background:#0f172a;border:2px solid #38bdf8;}</style></head><body><canvas id="game" width="400" height="400"></canvas><script>const ctx=document.getElementById("game").getContext("2d");ctx.fillStyle="red";ctx.fillRect(50,50,10,10);</script></body></html>"""
    
    return f"""<!DOCTYPE html><html><head><style>body{{background:#1e293b;color:white;text-align:center;}}</style></head><body><h1>App Gerado Localmente</h1><p>Prompt: {prompt}</p></body></html>"""

def analisar_e_evoluir(html_atual, prompt_novo):
    html_novo = str(html_atual)
    features_adicionadas = []
    prompt_lower = prompt_novo.lower()
    
    if "cor" in prompt_lower or "vermelho" in prompt_lower:
        if "background-color: #8b0000" not in html_novo:
            html_novo = html_novo.replace("</style>", "body { background-color: #8b0000 !important; color: white; }</style>")
            features_adicionadas.append("cor_vermelha")
            
    if "som" in prompt_lower or "audio" in prompt_lower:
        if "function tocarSom()" not in html_novo:
            js_som = "\nfunction tocarSom() { var audio = new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA='); audio.play(); }\n"
            if "</script>" in html_novo:
                html_novo = html_novo.replace("</script>", js_som + "</script>")
            html_novo = html_novo.replace("</body>", "<button onclick='tocarSom()' style='position:fixed; bottom:10px; right:10px;'>Tocar Som</button></body>")
            features_adicionadas.append("som")

    return html_novo, features_adicionadas

def processar_sintese(prompt_usuario, force_create=False):
    db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
    memoria = {}
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            memoria = json.load(f)
        
    chave_alvo = None
    for k in memoria.keys():
        if "velha" in prompt_usuario.lower() and "velha" in k.lower():
            chave_alvo = k
            break
        if "cobra" in prompt_usuario.lower() and "cobra" in k.lower():
            chave_alvo = k
            break
            
    if not chave_alvo:
        if force_create:
            return None, "Precisa criar"
        return None, "Nao encontrado no cache."
        
    entry = memoria[chave_alvo]
    if isinstance(entry, dict):
        html_atual = entry.get("html", "")
        features_antigas = entry.get("features", [])
    else:
        html_atual = entry
        features_antigas = []
        
    html_evoluido, novas_features = analisar_e_evoluir(html_atual, prompt_usuario)
    
    if novas_features:
        features_todas = list(set(features_antigas + novas_features))
        memoria[chave_alvo] = {"html": html_evoluido, "features": features_todas}
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
        return html_evoluido, f"EVOLUIDO_LOCAL_{novas_features}"
        
    return html_atual, "CACHE_LOCAL_PURO"
