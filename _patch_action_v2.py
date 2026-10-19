import sys, os, shutil, time, py_compile

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = APP + ".bak_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(APP, bak)
print(f"[OK] Backup: {os.path.basename(bak)}")

with open(APP, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Localiza "if self.path == \"/api/action\":"
start = None
for i, l in enumerate(lines):
    if 'if self.path == "/api/action":' in l:
        start = i
        break

if start is None:
    print("[ERRO] Bloco /api/action nao encontrado.")
    sys.exit(1)

# Encontra o proximo "elif self.path ==" ou "def " no mesmo nivel de indentacao
indent = lines[start][:len(lines[start]) - len(lines[start].lstrip())]
end = len(lines)
for j in range(start + 1, len(lines)):
    s = lines[j]
    if s.startswith(indent) and (s.lstrip().startswith("elif self.path") or s.lstrip().startswith("def ") or s.lstrip().startswith("else:")):
        end = j
        break

novo_bloco = [
    '        if self.path == "/api/action":\n',
    '            try:\n',
    '                length = int(self.headers["Content-Length"])\n',
    '                payload = json.loads(self.rfile.read(length))\n',
    '                action = payload.get("action", "")\n',
    '                value = int(payload.get("value", 0))\n',
    '\n',
    '                if action == "set_brightness":\n',
    '                    self._send_json({"status": "success", "resultado": alterar_brilho(value)})\n',
    '                elif action == "set_temperature":\n',
    '                    from core.hardware import alterar_calor\n',
    '                    self._send_json({"status": "success", "resultado": alterar_calor(value)})\n',
    '                else:\n',
    '                    self._send_json({"status": "error", "message": f"Acao desconhecida: {action}"})\n',
    '            except Exception as e:\n',
    '                self._send_json({"status": "error", "message": str(e)})\n',
    '\n',
]

new_lines = lines[:start] + novo_bloco + lines[end:]

with open(APP, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

try:
    py_compile.compile(APP, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado com /api/action correto.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, APP)
    sys.exit(1)