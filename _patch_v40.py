import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_v40_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

start_marker = 'elif self.path == "/api/generate_cloud":'
end_marker = 'else:\n            self.send_response(404)'
start = code.find(start_marker)
end = code.find(end_marker, start)

if start == -1 or end == -1:
    print("[ERRO] Nao foi possivel localizar /api/generate_cloud.")
    sys.exit(1)

novo_bloco = '''elif self.path == "/api/generate_cloud":
            if not INTELIGENCIA_OK:
                self._send_json({"status": "error", "message": "Nuvem offline."})
                return
            try:
                length = int(self.headers['Content-Length'])
                payload = json.loads(self.rfile.read(length))
                prompt = payload.get("prompt", "")
                t0 = time.perf_counter()

                # 1. O Prompt pede o HTML COMPLETO dentro do Scaffold
                sys_prompt = (
                    f"Voce e um Engenheiro de Software Sênior. Gere o codigo HTML/CSS/JS COMPLETO para: {prompt}.\\n"
                    "REGRAS:\\n"
                    "1. Use o seguinte esqueleto (Scaffold) e preencha o {INNER}:\\n"
                    f"{SCAFFOLD_TEMPLATE}\\n\\n"
                    "2. Inclua todo o JavaScript necessario para a logica funcionar.\\n"
                    "3. Retorne APENAS o codigo HTML final, sem explicacoes ou markdown."
                )
                
                res, provider, _ = gerar_com_fallback(sys_prompt)
                if not res:
                    self._send_json({"status": "error", "message": "Cascata falhou."})
                    return

                res_text = str(res).strip()
                # Limpeza profunda
                res_text = re.sub(r'```[a-z]*\\n?', '', res_text, flags=re.IGNORECASE)
                res_text = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', res_text, flags=re.IGNORECASE)
                # NAO removemos o <style>!
                
                # 3. Envolve no Scaffold
                final_html = SCAFFOLD_TEMPLATE.replace("{INNER}", res_text)

                # 4. Validacao CISO
                ok, motivo = WebCISOGate.validar_html(final_html)
                if not ok:
                    self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    return

                elapsed = round((time.perf_counter() - t0) * 1000, 2)
                
                # 5. GUARDA O OURO NA MEMORIA (Sempre)
                cerebro.aprender_da_nuvem(prompt, final_html)
                print(f"[MEMORIA] Ouro guardado para: '{prompt[:30]}...'")
                
                self._send_json({"status": "success", "html": final_html, "fonte": f"Nuvem ({provider}) + Scaffold", "elapsed_ms": elapsed})

            except Exception as e:
                self._send_json({"status": "error", "message": f"Erro: {str(e)}"})
        '''

code = code[:start] + novo_bloco + code[end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado (Scaffold Completo).")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)