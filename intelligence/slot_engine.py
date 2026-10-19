# -*- coding: utf-8 -*-
"""
LUMA Slot Engine (v52.0)
Arquitetura de Slots Fixos + Delta Estruturado + Parser Deterministico.
"""
import re, json

# SCAFFOLD IMUTAVEL (o motor local e o unico dono)
SCAFFOLD_SLOTS = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    /* === [slot-styles] === */
    body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
    .app-container { background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; gap: 12px; max-width: 500px; width: 100%; }
    button { padding: 12px 18px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; background: #38bdf8; color: #0f172a; font-size: 15px; }
    button:hover { opacity: 0.85; }
    /* === [/slot-styles] === */
</style>
</head>
<body>
    <div class="app-container">
        <header id="slot-header"></header>
        <main id="slot-main"></main>
        <div id="slot-controls"></div>
    </div>
    <script>
        // === [slot-scripts] ===
        // === [/slot-scripts] ===
    </script>
</body>
</html>"""

SLOTS_VALIDOS = ["slot-header", "slot-main", "slot-controls", "slot-styles", "slot-scripts"]

def validar_delta(delta):
    if not isinstance(delta, dict):
        return False, "Delta nao e um objeto JSON."
    if "target_slot" not in delta:
        return False, "Falta 'target_slot'."
    if delta["target_slot"] not in SLOTS_VALIDOS:
        return False, f"Slot invalido: {delta['target_slot']}."
    if "action" not in delta:
        return False, "Falta 'action'."
    if delta["action"] not in ["replace_inner", "append_inner"]:
        return False, f"Acao invalida: {delta['action']}."
    if "html" not in delta and delta["action"] != "append_inner":
        return False, "Falta 'html'."
    return True, "OK"

def _substituir_inner(html, slot_id, novo_inner):
    padrao = r'<([a-z]+)([^>]*id=["\']' + re.escape(slot_id) + r'["\'][^>]*)>([\s\S]*?)</\1>'
    match = re.search(padrao, html, re.IGNORECASE)
    if not match:
        return None
    return html[:match.start(3)] + novo_inner + html[match.end(3):]

def _adicionar_inner(html, slot_id, novo_inner):
    padrao = r'<([a-z]+)([^>]*id=["\']' + re.escape(slot_id) + r'["\'][^>]*)>([\s\S]*?)</\1>'
    match = re.search(padrao, html, re.IGNORECASE)
    if not match:
        return None
    atual = match.group(3)
    return html[:match.start(3)] + atual + novo_inner + html[match.end(3):]

def _adicionar_css(html, css_delta):
    if "/* === [/slot-styles] === */" in html:
        return html.replace("/* === [/slot-styles] === */", css_delta + "\n/* === [/slot-styles] === */")
    return html

def _adicionar_js(html, js_delta):
    if "// === [/slot-scripts] ===" in html:
        return html.replace("// === [/slot-scripts] ===", js_delta + "\n// === [/slot-scripts] ===")
    return html

def aplicar_delta(html_base, delta_json):
    if isinstance(delta_json, str):
        try:
            delta = json.loads(delta_json)
        except Exception as e:
            return None, f"JSON invalido: {e}"
    else:
        delta = delta_json

    ok, motivo = validar_delta(delta)
    if not ok:
        return None, motivo

    novo_html = html_base
    slot = delta["target_slot"]
    action = delta["action"]

    if action == "replace_inner":
        novo_html = _substituir_inner(novo_html, slot, delta.get("html", ""))
    elif action == "append_inner":
        novo_html = _adicionar_inner(novo_html, slot, delta.get("html", ""))

    if novo_html is None:
        return None, f"Slot '{slot}' nao encontrado no HTML base."

    if delta.get("css_delta"):
        novo_html = _adicionar_css(novo_html, delta["css_delta"])

    if delta.get("js_hooks"):
        js = delta["js_hooks"]
        if isinstance(js, dict):
            js = "\n".join(js.values())
        novo_html = _adicionar_js(novo_html, js)

    return novo_html, "OK"