import sys, shutil, time, py_compile, re

path = r"C:\Users\user\Desktop\aaaaaaaaaaaa\Nova pasta (6)\v7 fenix\controle_brilho_v9.py"
bak = path + ".bak_sota_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {{bak}}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Injetar o metodo _abrir_sota antes de _abrir_pasta
if "_abrir_sota" not in code:
    metodo_sota = '''    def _abrir_sota(self):
        import urllib.request, webbrowser, tempfile, json, threading
        prompt = "criar jogo da velha com placar"
        def worker():
            try:
                self.status.config(text='SOTA: A contactar o Cerebro Local...', fg='#ff8')
                req = urllib.request.Request(
                    'http://127.0.0.1:8080/api/generate_local',
                    data=json.dumps({'prompt': prompt}).encode('utf-8'),
                    headers={{'Content-Type': 'application/json'}}
                )
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = json.loads(r.read().decode('utf-8'))
                if data.get('status') == 'success' and data.get('html'):
                    path = os.path.join(tempfile.gettempdir(), 'sota_preview.html')
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(data['html'])
                    webbrowser.open('file://' + path)
                    self.status.config(text='SOTA: Preview aberto no navegador', fg='#8f8')
                else:
                    self.status.config(text=f"SOTA: {{data.get('message', 'Erro')}}", fg='#f88')
            except Exception as e:
                self.status.config(text=f'SOTA: Backend offline ({{e}})', fg='#f88')
        threading.Thread(target=worker, daemon=True).start()

'''
    code = code.replace("    def _abrir_pasta(self):", metodo_sota + "    def _abrir_pasta(self):")
    print("[OK] Metodo _abrir_sota injetado.")

# 2. Adicionar o botao SOTA na lista de botoes
if "('\\U0001F680 SOTA'" not in code and "'SOTA'" not in code:
    # Procura a lista de botoes
    if "('\\U0001F9E0 Cérebro', self._cerebro_janela)" in code:
        code = code.replace(
            "('\\U0001F9E0 Cérebro', self._cerebro_janela),",
            "('\\U0001F680 SOTA', self._abrir_sota), ('\\U0001F9E0 Cérebro', self._cerebro_janela),"
        )
        print("[OK] Botao SOTA injetado na lista.")
    elif "('🧠 Cérebro', self._cerebro_janela)" in code:
        code = code.replace(
            "('🧠 Cérebro', self._cerebro_janela),",
            "('🚀 SOTA', self._abrir_sota), ('🧠 Cérebro', self._cerebro_janela),"
        )
        print("[OK] Botao SOTA injetado na lista (unicode).")
    else:
        print("[AVISO] Lista de botoes nao encontrada. O metodo foi injetado mas o botao pode nao aparecer.")
else:
    print("[OK] Botao SOTA ja existia.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU.")
except Exception as e:
    print(f"[FALHA] {{e}}")
    shutil.copy2(bak, path)
    sys.exit(1)