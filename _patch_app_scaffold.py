# -*- coding: utf-8 -*-
import os, sys, shutil, time, py_compile, re

APP_PATH = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = APP_PATH + ".bak_scaffold_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(APP_PATH, bak)
print(f"[OK] Backup: {bak}")

with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Adicionar o SCAFFOLD_TEMPLATE no topo (apos as importacoes)
scaffold_code = '''
# ═══════════════════════════════════════════════════════════════════
# SCAFFOLD NATIVO (v24.0) - O Motor Local fornece o esqueleto
# ═══════════════════════════════════════════════════════════════════
SCAFFOLD_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .app-container { background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 12px; }
    .display { background: #0f172a; color: #38bdf8; font-size: 24px; padding: 10px; border-radius: 6px; text-align: right; min-height: 40px; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    button { padding: 15px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; background: #38bdf8; color: #0f172a; font-size: 16px; }
    button:hover { opacity: 0.8; }
</style>
</head>
<body>
    <div class="app-container">
        {INNER}
    </div>
</body>
</html>"""

'''

if "SCAFFOLD_TEMPLATE" not in code:
    # Insere antes da classe LumaCoreHandler
    code = code.replace("class LumaCoreHandler", scaffold_code + "\nclass LumaCoreHandler")

# 2. Substituir a logica de /api/generate_cloud
old_cloud = """                sys_prompt = (
                    "Voce e o LUMA. Gere HTML/CSS/JS puro. Use fundo escuro. "
                    "NAO use markdown (```). Inicie com <div>. Inclua <script> se necessario.\\n"
                    f"Pedido: {prompt}"
                )
                res, provider, _ = gerar_com_fallback(sys_prompt)
                
                if res:
                    res_text = str(res).strip()
                    res_text = re.sub(r"```(?:html|css|javascript)?\\n?|```", "", res_text).strip()
                    match = re.search(r'(<(?:div|html)[\\s\\S]*?<\\/(?:div|html)>)', res_text, re.IGNORECASE)
                    if match: res_text = match.group(1).strip()
                    
                    if res_text.startswith("<div") or res_text.startswith("<html"):
                        ok, motivo = WebCISOGate.validar_html(res_text)
                        if ok:
                            cerebro.aprender_da_nuvem(prompt, res_text)
                            self._send_json({"status": "success", "html": res_text, "fonte": f"Nuvem ({provider})", "elapsed_ms": elapsed})
                        else:
                            self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                    else:
                        self._send_json({"status": "error", "message": "O LLM respondeu com texto, nao HTML."})
                else:
                    self._send_json({"status": "error", "message": "Cascata falhou."})"""

new_cloud = """                # O Prompt pede APENAS o miolo (Scaffold Inverso)
                sys_prompt = (
                    f"Gere APENAS o codigo HTML interno e a tag <script> para: {prompt}.\\n"
                    "NAO inclua <!DOCTYPE html>, <html>, <head>, <style> ou <body>.\\n"
                    "O codigo sera injetado dentro de: <div class='app-container'>.\\n"
                    "Use botoes, inputs e o JavaScript necessario. Seja conciso.\\n"
                    "Retorne APENAS o codigo puro (sem markdown)."
                )
                
                res, provider, _ = gerar_com_fallback(sys_prompt)
                
                if res:
                    inner = str(res).strip()
                    # 1. Limpa markdown e tags html que o LLM teime em colocar
                    inner = re.sub(r'```[a-z]*\\n?', '', inner, flags=re.IGNORECASE)
                    inner = re.sub(r'<!DOCTYPE html>|<html[^>]*>|</html>|<head[^>]*>|</head>|<body[^>]*>|</body>', '', inner, flags=re.IGNORECASE)
                    inner = re.sub(r'<style[^>]*>.*?</style>', '', inner, flags=re.IGNORECASE | re.DOTALL)
                    
                    # 2. Injeta no Scaffold Nativo
                    res_text = SCAFFOLD_TEMPLATE.replace("{INNER}", inner)
                    
                    ok, motivo = WebCISOGate.validar_html(res_text)
                    if ok:
                        # Guarda na memoria local
                        cerebro.aprender_da_nuvem(prompt, res_text)
                        self._send_json({"status": "success", "html": res_text, "fonte": f"Nuvem ({provider}) + Scaffold", "elapsed_ms": elapsed})
                    else:
                        self._send_json({"status": "error", "message": f"Bloqueio CISO: {motivo}"})
                else:
                    self._send_json({"status": "error", "message": "Cascata falhou."})"""

if old_cloud in code:
    code = code.replace(old_cloud, new_cloud)
    print("[OK] /api/generate_cloud substituido pelo Scaffold v24.0.")
else:
    print("[AVISO] Padrao antigo nao encontrado. Tentando substituicao por regex...")
    # Fallback de regex caso o texto tenha pequenas variacoes
    pattern = r'sys_prompt = \(\s*"Voce e o LUMA\.[\s\S]*?self\._send_json\(\{"status": "error", "message": "Cascata falhou\."\}\)'
    if re.search(pattern, code):
        code = re.sub(pattern, new_cloud, code)
        print("[OK] Substituicao por regex bem-sucedida.")
    else:
        print("[ERRO] Nao foi possivel localizar o bloco /api/generate_cloud.")
        sys.exit(1)

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(APP_PATH, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, APP_PATH)
    sys.exit(1)