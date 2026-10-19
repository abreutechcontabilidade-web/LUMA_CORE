
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from intelligence.key_ring import KeyRing

vault_path = r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json"
if not os.path.exists(vault_path): vault_path = r"C:\Users\user\Desktop\lumazbit\vault.json"
anel = KeyRing(vault_path)

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from intelligence.key_ring import KeyRing

vault_path = r"C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json"
if not os.path.exists(vault_path): vault_path = r"C:\Users\user\Desktop\lumazbit\vault.json"
import socketserver
from http.server import ThreadingHTTPServer
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backup_manager import create_timestamped_backup
from patch_engine import apply_patch_transaction, calculate_sha256
import tempfile
import os
import json
# -*- coding: utf-8 -*-
import http.server, socketserver, json, sys, os, re, unicodedata, time
from datetime import datetime, timezone

BASE = r"C:\Users\user\Desktop\LUMA_CORE"
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, "intelligence"))

from core.hardware import alterar_brilho
from core.cortex import avaliar_bioritmo
from core.vigia import Vigia
from intelligence.virtual_onnx import VirtualONNX
from intelligence.key_ring import KeyRing

try:
    from intelligence.fallback import gerar_com_fallback
    INTELIGENCIA_OK = True
except Exception:
    INTELIGENCIA_OK = False

PORT = 8080
WEB_DIR = os.path.join(BASE, "cockpit_pwa")
cerebro = VirtualONNX()

# INICIALIZANDO KEY RING
vault_path = r'C:\Users\user\Desktop\cpf_arboreo_repo\_bancada\motor\lib\vault.json'
key_ring = KeyRing(vault_path)
_ledger_path = os.path.join(BASE, "intelligence", "zbit_ledger.jsonl")
vigia = Vigia(_ledger_path)
vigia.start(interval=2.0)

SCAFFOLD_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<style>
body{background:#0f172a;color:#f8fafc;font-family:system-ui,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}
.app-container{background:#1e293b;padding:20px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.5);display:flex;flex-direction:column;gap:12px}
.display{background:#0f172a;color:#38bdf8;font-size:24px;padding:10px;border-radius:6px;text-align:right;min-height:40px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
button{padding:15px;border:none;border-radius:6px;cursor:pointer;font-weight:bold;background:#38bdf8;color:#0f172a;font-size:16px}
</style></head><body><div class="app-container">{INNER}</div></body></html>"""

class WebCISOGate:
    VETOS = [r"javascript\s*:", r"<iframe\b", r"srcdoc\s*=", r"\beval\s*\(", r"\batob\s*\(", r"\bnew\s+Function\b", r"window\.parent", r"document\.cookie", r"localStorage", r"fetch\s*\("]
    @classmethod
    def validar_html(cls, html):
        norm = unicodedata.normalize("NFKC", html)
        for pat in cls.VETOS:
            if re.search(pat, norm, re.IGNORECASE):
                return False, f"VETO CISO: {pat}"
        return True, "OK"

class LumaCoreHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)
    def copyfile(self, source, outputfile):
        try: super().copyfile(source, outputfile)
        except (ConnectionAbortedError, BrokenPipeError): pass
    def _send_json(self, data, status=200):
        try:
            import json
            response = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        except Exception as e:
            print(f"[ERRO] Falha ao enviar JSON: {e}")
    def do_GET(self):
        if self.path == "/api/status":
            self._send_json({"status": "LUMA_CORE v60.0", "timestamp": datetime.now(timezone.utc).isoformat(), "vigia": vigia.last() is not None})
        elif self.path == "/api/telemetry":
            last = vigia.last()
            if last is None: self._send_json({"status": "warmup"})
            else: self._send_json(last)
        elif self.path == "/api/audit":
            self._send_json({"events": vigia.ledger.read_last(20)})
        elif self.path == "/api/cortex":
            self._send_json(avaliar_bioritmo())
        else:
            super().do_GET()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/action":
            try:
                length = int(self.headers['Content-Length'])
                payload = json.loads(self.rfile.read(length))
                if payload.get("action") == "set_brightness":
                    self._send_json({"status": "success", "resultado": alterar_brilho(payload.get("value", 50))})
                else:
                    self._send_json({"status": "error", "message": "Ação desconhecida"})
            except Exception as e: self._send_json({"status": "error", "message": str(e)})
        elif self.path == "/api/generate_local":
            try:
                length = int(self.headers['Content-Length'])
                payload = json.loads(self.rfile.read(length))
                prompt = payload.get("prompt", "")
                res, fonte = cerebro.processar(prompt)
                if res: self._send_json({"status": "success", "html": res, "fonte": fonte})
                else: self._send_json({"status": "error", "message": "Cérebro local não reconhece."})
            except Exception as e: self._send_json({"status": "error", "message": str(e)})
        elif self.path == "/api/generate_cloud":
            import time, json, os
            from intelligence.swarm_engine import disparar_enxame
            from intelligence.dom_parser import ler_miolo
            from intelligence.onnx_bridge import inferir_mutacao, aplicar_mutacoes
            from intelligence.onnx_sovereign import buscar_no_genoma
            from intelligence.local_synthesis import gerar_esqueleto_local
            from intelligence.background_learner import aprender_em_segundo_plano
            
            start_time = time.perf_counter()
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                req_data = json.loads(post_data)
                prompt = req_data.get("prompt", "")
            except Exception:
                self._send_json({"error": "JSON invalido"}, 400)
                return

            # NIVEL 1: ONNX
            print(f"[ONNX] Buscando correspondencia para: '{prompt[:30]}...'")
            intent_onnx, score = buscar_no_genoma(prompt, cerebro.dynamic_tools)
            
            if intent_onnx and score > 0.4:
                print(f"[ONNX] Match! Chave: '{intent_onnx}' | Score: {score:.2f}")
                with open(cerebro.db_path, "r", encoding="utf-8") as f:
                    mem_disco = json.load(f)
                entry = mem_disco.get(intent_onnx, {})
                html_atual = entry.get("html", "") if isinstance(entry, dict) else entry
                
                miolo = ler_miolo(html_atual)
                mutacoes = inferir_mutacao(prompt, miolo)
                
                # Dispara a Consciencia Paralela (Nuvem + Web) em background
                aprender_em_segundo_plano(prompt, intent_onnx, anel, cerebro.db_path)
                
                if mutacoes:
                    print(f"[ONNX] Mutacoes decididas: {len(mutacoes)}")
                    html_evoluido = aplicar_mutacoes(html_atual, mutacoes)
                    features_antigas = entry.get("features", []) if isinstance(entry, dict) else []
                    features_todas = list(set(features_antigas + ["mutacao_onnx"]))
                    mem_disco[intent_onnx] = {"html": html_evoluido, "features": features_todas}
                    
                    tmp_path = cerebro.db_path + ".tmp"
                    with open(tmp_path, "w", encoding="utf-8") as f:
                        json.dump(mem_disco, f, ensure_ascii=False, indent=2)
                    os.replace(tmp_path, cerebro.db_path)
                    cerebro.dynamic_tools = mem_disco
                    
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Evolucao aplicada via ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_evoluido, "fonte": "ONNX_MUTACAO_LOCAL", "elapsed_ms": elapsed})
                    return
                else:
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    print(f"[LOCAL] Cache puro ONNX em {elapsed}ms.")
                    self._send_json({"status": "success", "html": html_atual, "fonte": "ONNX_CACHE_PURO", "elapsed_ms": elapsed})
                    return

            # NIVEL 2 e 3: ENXAME e WEB (Se nao tiver no cache, espera o resultado)
            print(f"[LOCAL] Nenhum match. Acionando Enxame...")
            resposta_final, fonte = disparar_enxame(prompt, anel)
            
            if resposta_final:
                try:
                    cerebro.aprender_da_nuvem(prompt, resposta_final)
                except: pass
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": resposta_final, "fonte": fonte, "elapsed_ms": elapsed})
                return

            print("[DIRECT WEB] Enxame falhou. A ligar diretamente a Web (Wikipedia/GitHub)...")
            from intelligence.github_learner import aprender_do_github
            codigo_web = aprender_do_github(prompt)
            
            if codigo_web:
                intent_web = prompt.lower().replace(" ", "_")[:20]
                with open(cerebro.db_path, "r", encoding="utf-8") as f:
                    mem_disco = json.load(f)
                mem_disco[intent_web] = {"html": codigo_web, "features": ["aprendido_web"]}
                
                tmp_path = cerebro.db_path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(mem_disco, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, cerebro.db_path)
                cerebro.dynamic_tools = mem_disco
                
                elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                self._send_json({"status": "success", "html": codigo_web, "fonte": "WEB_LEARNER", "elapsed_ms": elapsed})
                return

            # NIVEL 4: AUTOPOIESE
            print("[AUTOPOIESE] Tudo falhou. Criando esqueleto local...")
            html_auto = gerar_esqueleto_local(prompt)
            miolo_auto = ler_miolo(html_auto)
            mutacoes_auto = inferir_mutacao(prompt, miolo_auto)
            if mutacoes_auto:
                html_auto = aplicar_mutacoes(html_auto, mutacoes_auto)
            
            intent_local = prompt.lower().replace(" ", "_")[:20]
            with open(cerebro.db_path, "r", encoding="utf-8") as f:
                mem_disco = json.load(f)
            mem_disco[intent_local] = {"html": html_auto, "features": ["autopoiese_evoluida"]}
            
            tmp_path = cerebro.db_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(mem_disco, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, cerebro.db_path)
            cerebro.dynamic_tools = mem_disco
            
            elapsed = round((time.perf_counter() - start_time) * 1000, 2)
            self._send_json({"status": "success", "html": html_auto, "fonte": "AUTOPOIESE_LOCAL", "elapsed_ms": elapsed})

    
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PORT = 8080
    socketserver.TCPServer.allow_reuse_address = True
    print(f"[LUMA_CORE] Servidor v67.0 (ONNX Soberano) ativo em http://127.0.0.1:{PORT}")
    try:
        with ThreadingHTTPServer(("127.0.0.1", PORT), LumaCoreHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"[ERRO FATAL] {e}")
