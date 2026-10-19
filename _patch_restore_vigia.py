import re, sys, shutil, time, py_compile

path = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
bak = path + ".bak_vigia_restore_" + time.strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, bak)
print(f"[OK] Backup: {bak}")

with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Garantir o import do Vigia
if "from core.vigia import Vigia" not in code:
    code = code.replace(
        "from core.cortex import avaliar_bioritmo",
        "from core.cortex import avaliar_bioritmo\nfrom core.vigia import Vigia"
    )
    print("[OK] Import do Vigia restaurado.")

# 2. Instanciar o Vigia no topo
if "vigia_instance" not in code:
    code = code.replace(
        "cerebro = VirtualONNX()",
        'cerebro = VirtualONNX()\n'
        'import os as _os\n'
        '_ledger_path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "intelligence", "zbit_ledger.jsonl")\n'
        'vigia_instance = Vigia(_ledger_path)\n'
        'vigia_instance.start(interval=2.0)'
    )
    print("[OK] Vigia instanciado e iniciado.")

# 3. Inserir as rotas no do_GET (antes do /api/cortex)
if 'elif self.path == "/api/cortex":' in code and '/api/telemetry' not in code:
    old_block = 'elif self.path == "/api/cortex":'
    new_block = '''elif self.path == "/api/telemetry":
            last = vigia_instance.last()
            if last is None:
                self._send_json({"status": "warmup", "message": "Vigia a arrancar"})
            else:
                self._send_json(last)
        elif self.path == "/api/audit":
            self._send_json({"events": vigia_instance.ledger.read_last(20)})
        elif self.path == "/api/cortex":'''
    
    code = code.replace(old_block, new_block, 1)
    print("[OK] Rotas /api/telemetry e /api/audit reinjetadas.")
else:
    if '/api/telemetry' in code:
        print("[AVISO] As rotas do VIGIA ja estavam no codigo. O 404 pode ser porque o servidor nao foi reiniciado.")
    else:
        print("[ERRO] Nao foi possivel encontrar '/api/cortex' para inserir as rotas do VIGIA.")

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

try:
    py_compile.compile(path, doraise=True)
    print("[OK] py_compile PASSOU. app.py atualizado.")
except Exception as e:
    print(f"[FALHA] {e}")
    shutil.copy2(bak, path)
    sys.exit(1)