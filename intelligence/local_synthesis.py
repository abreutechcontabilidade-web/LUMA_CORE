import json, re, os

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
            js_som = "\nfunction tocarSom() { var audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg'); audio.play(); }\n"
            if "</script>" in html_novo: html_novo = html_novo.replace("</script>", js_som + "</script>")
            html_novo = html_novo.replace("</body>", "<button onclick='tocarSom()' style='position:fixed; bottom:10px; right:10px;'>Tocar Som</button></body>")
            features_adicionadas.append("som")
    return html_novo, features_adicionadas

def processar_sintese(prompt_usuario):
    db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
    if not os.path.exists(db_path): return None, "Sem memoria"
        
    with open(db_path, "r", encoding="utf-8") as f: memoria = json.load(f)
        
    chave_alvo = None
    if "velha" in prompt_usuario.lower(): chave_alvo = "jogo_da_velha"
    elif "calculadora" in prompt_usuario.lower(): chave_alvo = "calculadora"
            
    if chave_alvo and chave_alvo not in memoria:
        # AUTOPOIESE (Criacao Local)
        if chave_alvo == "calculadora":
            html_base = """<!DOCTYPE html><html><head><style>body{background:#1e293b;color:white;display:flex;justify-content:center;align-items:center;height:100vh;} .calc{background:#0f172a;padding:20px;border-radius:10px;display:grid;grid-template-columns:repeat(4,1fr);gap:10px;}</style></head><body><div class="calc"><input type="text" style="grid-column:span 4;padding:10px;font-size:20px;"><button>7</button><button>8</button><button>9</button><button>/</button><button>4</button><button>5</button><button>6</button><button>*</button><button>1</button><button>2</button><button>3</button><button>-</button><button>0</button><button>.</button><button>=</button><button>+</button></div></body></html>"""
            memoria[chave_alvo] = {"html": html_base, "features": []}
            with open(db_path, "w", encoding="utf-8") as f: json.dump(memoria, f, ensure_ascii=False, indent=2)
            return html_base, "CRIADO_LOCAL_BASE"
            
    if chave_alvo and chave_alvo in memoria:
        entry = memoria[chave_alvo]
        html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
        features_antigas = entry.get("features", []) if isinstance(entry, dict) else []
        
        html_evoluido, novas_features = analisar_e_evoluir(html_atual, prompt_usuario)
        
        if novas_features:
            features_todas = list(set(features_antigas + novas_features))
            memoria[chave_alvo] = {"html": html_evoluido, "features": features_todas}
            with open(db_path, "w", encoding="utf-8") as f: json.dump(memoria, f, ensure_ascii=False, indent=2)
            return html_evoluido, f"EVOLUIDO_LOCAL_{novas_features}"
            
        return html_atual, "CACHE_LOCAL_PURO"
        
    return None, "Nao encontrado no cache."