
import threading
import json
import os
from intelligence.swarm_engine import disparar_enxame
from intelligence.github_learner import aprender_do_github
from intelligence.onnx_sovereign import extrair_chave

json_lock = threading.Lock()

def _atualizar_genoma(db_path, intent, novo_html, fonte):
    with json_lock:
        try:
            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    mem = json.load(f)
            else:
                mem = {}
                
            antigo = mem.get(intent, {}).get("html", "")
            if novo_html and novo_html != antigo:
                if intent not in mem or not isinstance(mem[intent], dict):
                    mem[intent] = {"html": novo_html, "features": ["background_learn"]}
                else:
                    mem[intent]["html"] = novo_html
                    if "background_learn" not in mem[intent].get("features", []):
                        mem[intent].setdefault("features", []).append("background_learn")
                
                tmp_path = db_path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(mem, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, db_path)
                print(f"[BACKGROUND] Genoma evoluido via {fonte} para '{intent}'.")
        except Exception as e:
            print(f"[BACKGROUND] Erro ao atualizar genoma: {e}")

def _tarefa_nuvem(prompt, intent, anel, db_path):
    print(f"[BACKGROUND] Disparando Enxame para evoluir '{intent}'...")
    resposta, fonte = disparar_enxame(prompt, anel)
    if resposta:
        _atualizar_genoma(db_path, intent, resposta, fonte)

def _tarefa_web(prompt, intent, db_path):
    print(f"[BACKGROUND] Pesquisando na Web (GitHub) para evoluir '{intent}'...")
    # G-149 FIX: Usar a chave limpa em vez do prompt gigante
    codigo_web, prov = aprender_do_github(intent)
    if codigo_web:
        _atualizar_genoma(db_path, intent, codigo_web, "Web Learner")

def aprender_em_segundo_plano(prompt, intent, anel, db_path):
    t1 = threading.Thread(target=_tarefa_nuvem, args=(prompt, intent, anel, db_path))
    t2 = threading.Thread(target=_tarefa_web, args=(prompt, intent, db_path))
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()
