# -*- coding: utf-8 -*-
import os, sys, shutil, time, py_compile, re, json

BASE = r"C:\Users\user\Desktop\LUMA_CORE"
INTEL = os.path.join(BASE, "intelligence")
SERVER = os.path.join(BASE, "server")

timestamp = time.strftime("%Y%m%d_%H%M%S")
for path in [os.path.join(INTEL, "feature_engine.py"),
             os.path.join(INTEL, "cure_engine.py"),
             os.path.join(INTEL, "virtual_onnx.py"),
             os.path.join(SERVER, "app.py")]:
    if os.path.exists(path):
        shutil.copy2(path, path + f".bak_v48_{timestamp}")

print("[OK] Backups criados.")

# 1. feature_engine.py
feature_code = '''# -*- coding: utf-8 -*-
import os, json

def extrair_chave_estavel(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["velha", "tic tac toe"]): return "jogo_da_velha"
    if "calculadora" in p: return "calculadora"
    if any(k in p for k in ["cronometro", "cronómetro"]): return "cronometro"
    if "pomodoro" in p: return "pomodoro"
    return "desconhecido"

def extrair_features(prompt: str) -> list:
    p = prompt.lower()
    features = []
    if any(k in p for k in ["placar", "placa", "pontuacao"]): features.append("placar")
    if "empate" in p: features.append("empate")
    if any(k in p for k in ["historico", "histórico"]): features.append("historico")
    if any(k in p for k in ["cor", "cores", "vermelho", "azul"]): features.append("cores")
    if any(k in p for k in ["cronometro", "cronómetro", "timer"]): features.append("cronometro")
    if any(k in p for k in ["proxima", "próxima", "rodada"]): features.append("proxima_rodada")
    if any(k in p for k in ["reiniciar", "zerar"]): features.append("reiniciar")
    return features

def carregar_memoria(db_path: str) -> dict:
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_memoria(db_path: str, memoria: dict):
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)
'''
with open(os.path.join(INTEL, "feature_engine.py"), "w", encoding="utf-8") as f:
    f.write(feature_code)
print("[OK] feature_engine.py reescrito.")

# 2. cure_engine.py
cure_code = '''# -*- coding: utf-8 -*-
import re

def higienizar_miolo(html: str) -> str:
    if not html: return ""
    html = re.sub(r'```[a-z]*\\n?', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', html, flags=re.IGNORECASE)
    return html.strip()
'''
with open(os.path.join(INTEL, "cure_engine.py"), "w", encoding="utf-8") as f:
    f.write(cure_code)
print("[OK] cure_engine.py reescrito.")

# 3. virtual_onnx.py
onnx_code = '''# -*- coding: utf-8 -*-
import os, json, sys
sys.path.insert(0, r'C:\\Users\\user\\Desktop\\LUMA_CORE')
from intelligence.feature_engine import extrair_chave_estavel, extrair_features, carregar_memoria, guardar_memoria

class VirtualONNX:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "dynamic_tools.json")
        self.dynamic_tools = carregar_memoria(self.db_path)

    def processar(self, prompt: str):
        norm = prompt.lower().strip()
        chave = extrair_chave_estavel(prompt)
        features_pedidas = set(extrair_features(prompt))
        
        palavras_mutacao = ["mudar", "alterar", "mover", "colocar", "trocar", "passar"]
        if any(k in norm for k in palavras_mutacao) and features_pedidas:
            print("[ONNX] Mutacao detetada.")
            return None, "NUVEM_MUTACAO"

        entry = self.dynamic_tools.get(chave)
        if entry and isinstance(entry, dict) and "html" in entry:
            features_salvas = set(entry.get("features", []))
            if features_pedidas.issubset(features_salvas):
                print(f"[ONNX] Chave '{chave}' tem todas as features pedidas.")
                return entry["html"], f"APRENDIDO_{chave}"
            else:
                print(f"[ONNX] Chave '{chave}' existe, mas faltam features: {features_pedidas - features_salvas}")
                return entry["html"], f"BASE_INCOMPLETA_{chave}"

        if chave == "jogo_da_velha":
            return self._gerar_jogo_da_velha(), "LOCAL_BASIC"
        if chave == "calculadora":
            return self._gerar_calculadora_cientifica(), "LOCAL_BASIC"
        return None, "NUVEM_NECESSARIA"

    def aprender_da_nuvem(self, prompt: str, html: str):
        chave = extrair_chave_estavel(prompt)
        features = extrair_features(prompt)
        self.dynamic_tools[chave] = {"html": html, "features": features}
        guardar_memoria(self.db_path, self.dynamic_tools)
        print(f"[FUSAO] Ouro guardado: '{chave}' (features: {features})")

    def _gerar_jogo_da_velha(self):
        return """<div class='app-container'><h2>Jogo da Velha Básico</h2><div class='grid' id='board'></div><p id='status'>Vez do X</p></div>"""
    def _gerar_calculadora_cientifica(self):
        return """<div class='app-container'><h2>Calculadora</h2></div>"""
'''
with open(os.path.join(INTEL, "virtual_onnx.py"), "w", encoding="utf-8") as f:
    f.write(onnx_code)
print("[OK] virtual_onnx.py reescrito.")

# 4. app.py
app_path = os.path.join(SERVER, "app.py")
with open(app_path, "r", encoding="utf-8") as f:
    app_code = f.read()

app_code = re.sub(r"from intelligence\.feature_engine import [^\n]+", 
                  "from intelligence.feature_engine import extrair_chave_estavel, extrair_features, carregar_memoria, guardar_memoria",
                  app_code)

app_code = re.sub(r"res_text = re\.sub\(r'<div class=\[\"\\'\]app-container[\"\\'\]\[\^>\]\*>', '', res_text, flags=re\.IGNORECASE\)",
                  "res_text = re.sub(r'<div[^>]*class=[\"\\']app-container[\"\\'][^>]*>', '', res_text, flags=re.IGNORECASE)",
                  app_code)

start_marker = 'elif self.path == "/api/generate_cloud":'
end_marker = 'else:\n            self.send_response(404)'
start = app_code.find(start_marker)
end = app_code.find(end_marker, start)

if start != -1 and end != -1:
    novo_bloco = '''elif self.path == "/api/generate_cloud":
            if not INTELIGENCIA_OK:
                self._send_json({"status": "error", "message": "Nuvem offline."})
                return
            try:
                length = int(self.headers['Content-Length'])
                payload = json.loads(self.rfile.read(length))
                prompt = payload.get("prompt", "")
                t0 = time.perf_counter()

                from intelligence.feature_engine import extrair_chave_estavel, extrair_features
                chave = extrair_chave_estavel(prompt)
                features_pedidas = extrair_features(prompt)

                res_base = cerebro.processar(prompt)
                if isinstance(res_base, tuple) and len(res_base) == 2 and res_base[0]:
                    local_base, fonte = res_base
                else:
                    local_base = SCAFFOLD_TEMPLATE.replace("{INNER}", "")

                entry_atual = cerebro.dynamic_tools.get(chave, {})
                features_salvas = set(entry_atual.get("features", []))
                features_em_falta = set(features_pedidas) - features_salvas

                if features_em_falta:
                    delta_prompt = (
                        f"Voce e um Engenheiro de Software Sênior.\\n"
                        f"CODIGO BASE:\\n{local_base}\\n\\n"
                        f"TAREFA: Adicione APENAS as seguintes funcionalidades: {', '.join(features_em_falta)}.\\n"
                        "REGRAS:\\n"
                        "1. NAO altere o que ja existe.\\n"
                        "2. Adicione o HTML da nova funcionalidade dentro do container principal.\\n"
                        "3. Adicione o JavaScript necessario.\\n"
                        "4. Retorne o codigo HTML COMPLETO e MODIFICADO.\\n"
                        "5. Nao inclua explicacoes ou markdown."
                    )
                    print(f"[NUVEM] A pedir features em falta: {features_em_falta}")
                else:
                    print(f"[LOCAL] Todas as features ja existem. A devolver cache.")
                    self._send_json({"status": "success", "html": local_base, "fonte": "Local Cache", "elapsed_ms": 0.01})
                    return

                res, provider, _ = gerar_com_fallback(delta_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                miolo = str(res).strip()
                from intelligence.cure_engine import higienizar_miolo
                miolo = higienizar_miolo(miolo)
                miolo = re.sub(r'<div[^>]*class=["\\']app-container["\\'][^>]*>', '', miolo, flags=re.IGNORECASE)

                final_html = SCAFFOLD_TEMPLATE.replace("{INNER}", miolo)

                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                for f in features_em_falta:
                    if f not in final_html.lower():
                        print(f"[TESTE] Feature '{f}' nao encontrada no HTML final.")
                        self._send_json({"status": "error", "message": f"A Nuvem nao gerou a feature '{f}'."})
                        return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
                cerebro.dynamic_tools[chave] = {"html": final_html, "features": list(features_pedidas)}
                from intelligence.feature_engine import guardar_memoria
                guardar_memoria(cerebro.db_path, cerebro.dynamic_tools)
                print(f"[MEMORIA] Versao '{chave}' guardada com features: {features_pedidas}")
                
                self._send_json({"status": "success", "html": final_html, "fonte": f"Nuvem ({provider}) + Delta", "elapsed_ms": elapsed})

            except Exception as e:
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''
    app_code = app_code[:start] + novo_bloco + app_code[end:]
    print("[OK] Bloco /api/generate_cloud substituido.")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_code)

try:
    py_compile.compile(os.path.join(INTEL, "feature_engine.py"), doraise=True)
    py_compile.compile(os.path.join(INTEL, "cure_engine.py"), doraise=True)
    py_compile.compile(os.path.join(INTEL, "virtual_onnx.py"), doraise=True)
    py_compile.compile(app_path, doraise=True)
    print("[OK] Todos os ficheiros compilados com sucesso.")
except Exception as e:
    print(f"[FALHA] {e}")
    sys.exit(1)

db = os.path.join(INTEL, "dynamic_tools.json")
if os.path.exists(db):
    shutil.copy2(db, db + ".bak_limpeza_v48")
    os.remove(db)
    print("[OK] Memoria limpa (backup criado).")

print("\\n[SUCESSO] v48.0 instalada. Reinicie o servidor.")