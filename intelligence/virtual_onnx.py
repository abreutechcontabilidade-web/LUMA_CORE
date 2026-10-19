import os
import json

class VirtualONNX:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dynamic_tools.json')
        self.dynamic_tools = {}
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.dynamic_tools = json.load(f)
            except Exception as e:
                print(f"[VirtualONNX] Erro ao ler banco: {e}")

    def processar(self, prompt):
        intent = prompt.lower().strip()
        if intent in self.dynamic_tools:
            entry = self.dynamic_tools[intent]
            return entry.get('html', '') if isinstance(entry, dict) else entry, 'APRENDIDO_LOCAL'
        return '<div>Jogo da Velha Basico (Local)</div>', 'LOCAL_BASIC'

    def aprender_da_nuvem(self, intent, html, features=None):
        if not hasattr(self, 'dynamic_tools'):
            self.dynamic_tools = {}
        self.dynamic_tools[intent] = {'html': html, 'features': features or []}
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.dynamic_tools, f, ensure_ascii=False, indent=2)
            print(f"[VirtualONNX] Memoria salva com sucesso para: {intent}")
        except Exception as e:
            print(f"[VirtualONNX] Erro ao salvar no banco: {e}")
