import json
import os
import time

class KeyRing:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.keys = []
        self.current_index = 0
        self.dead_keys = {}
        self.load_keys()

    def load_keys(self):
        if not os.path.exists(self.vault_path):
            print(f"[KeyRing] ERRO: Arquivo não encontrado em {self.vault_path}")
            return
            
        try:
            with open(self.vault_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            collected = []
            if isinstance(data, dict):
                for provider, key_list in data.items():
                    if isinstance(key_list, list):
                        for item in key_list:
                            if isinstance(item, dict) and "key" in item:
                                collected.append(item["key"])
                            elif isinstance(item, str):
                                collected.append(item)
            
            self.keys = list(dict.fromkeys(collected))
            print(f"[KeyRing] Carregadas {len(self.keys)} chaves únicas do vault.")
            
        except Exception as e:
            print(f"[KeyRing] Erro ao carregar: {e}")

    def get_key(self):
        if not self.keys: return None
        now = time.time()
        for _ in range(len(self.keys)):
            key = self.keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.keys)
            if key in self.dead_keys:
                if now < self.dead_keys[key]: continue
                else: del self.dead_keys[key]
            return key
        return None

    def mark_dead(self, key, cooldown_hours=1):
        if not key: return
        self.dead_keys[key] = time.time() + (cooldown_hours * 3600)
        print(f"[KeyRing] Chave {key[:8]}... queimada (402/429). Cooldown de {cooldown_hours}h.")
