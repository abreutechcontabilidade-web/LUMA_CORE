import re

APP = r"C:\Users\user\Desktop\LUMA_CORE\server\app.py"
with open(APP, "r", encoding="utf-8") as f: code = f.read()

# A função que mapeia /artefacts/ para a pasta física
translate_func = """
    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        if path.startswith("/artefacts/"):
            filename = path.replace("/artefacts/", "")
            return os.path.join(ARTEFACTOS_DIR, filename)
        return super().translate_path(path)
"""

# Injeta a função logo após o log_message
if "def translate_path" not in code:
    code = code.replace("    def log_message(self, fmt, *args): return\n", 
                        "    def log_message(self, fmt, *args): return\n" + translate_func)
    with open(APP, "w", encoding="utf-8") as f: f.write(code)
    print("[OK] translate_path injetado com sucesso.")
else:
    print("[INFO] translate_path ja existe.")
