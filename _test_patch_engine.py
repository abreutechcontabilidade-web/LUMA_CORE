# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\user\Desktop\LUMA_CORE\intelligence")
from patch_engine import (
    compute_sha256, validate_patch, apply_patch,
    parse_llm_patch_response, MANIFEST,
)
from slot_engine import SCAFFOLD_SLOTS

PASS = "✅ PASS"
FAIL = "❌ FAIL"
resultados = []

def check(nome, condicao, detalhe=""):
    status = PASS if condicao else FAIL
    resultados.append((nome, condicao))
    print(f"  {status}  {nome}" + (f"  ({detalhe})" if detalhe else ""))

# ============================================================
print("\n" + "=" * 65)
print("TESTE 1 — PATCH VÁLIDO (adicionar placar ao header)")
print("=" * 65)
base = SCAFFOLD_SLOTS
hash_base = compute_sha256(base)
patch_valido = {
    "schema_version": "1.0",
    "base_sha256": hash_base,
    "intent_key": "jogo_da_velha",
    "mutations": [{
        "target_slot": "slot-header",
        "op": "replace_inner",
        "html": '<div><span data-role="score-x">0</span><span> - </span><span data-role="score-o">0</span></div>'
    }]
}
ok, motivo = validate_patch(patch_valido, base)
check("validate_patch aceita patch válido", ok, motivo)
novo_html, motivo_apply = apply_patch(base, patch_valido)
check("apply_patch aplica o patch", novo_html is not None, motivo_apply or "")
check("HTML final contém data-role=score-x", "score-x" in (novo_html or ""))

# ============================================================
print("\n" + "=" * 65)
print("TESTE 2 — HASH DIVERGENTE (deve REJEITAR)")
print("=" * 65)
patch_hash_errado = dict(patch_valido)
patch_hash_errado["base_sha256"] = "0" * 64
ok, motivo = validate_patch(patch_hash_errado, base)
check("validate_patch rejeita hash divergente", not ok, motivo)

# ============================================================
print("\n" + "=" * 65)
print("TESTE 3 — TAG PROIBIDA <script> (deve REJEITAR)")
print("=" * 65)
patch_script = dict(patch_valido)
patch_script["mutations"] = [{
    "target_slot": "slot-header",
    "op": "replace_inner",
    "html": "<script>alert(1)</script>"
}]
ok, motivo = validate_patch(patch_script, base)
check("validate_patch rejeita <script>", not ok, motivo)

# ============================================================
print("\n" + "=" * 65)
print("TESTE 4 — ATRIBUTO onclick (deve REJEITAR)")
print("=" * 65)
patch_onclick = dict(patch_valido)
patch_onclick["mutations"] = [{
    "target_slot": "slot-controls",
    "op": "replace_inner",
    "html": '<button onclick="reset()">Reset</button>'
}]
ok, motivo = validate_patch(patch_onclick, base)
check("validate_patch rejeita onclick", not ok, motivo)

# ============================================================
print("\n" + "=" * 65)
print("TESTE 5 — PARSER DE RESPOSTA LLM (com markdown)")
print("=" * 65)
resposta_com_markdown = '```json\n{"schema_version":"1.0","base_sha256":"abc","intent_key":"x","mutations":[]}\n```'
obj, motivo = parse_llm_patch_response(resposta_com_markdown)
check("parse_llm_patch_response extrai JSON com markdown", obj is not None, motivo)

# ============================================================
print("\n" + "=" * 65)
print("TESTE 6 — SLOT INEXISTENTE (deve REJEITAR)")
print("=" * 65)
patch_slot_errado = dict(patch_valido)
patch_slot_errado["mutations"] = [{
    "target_slot": "slot-fantasma",
    "op": "replace_inner",
    "html": "<div>teste</div>"
}]
ok, motivo = validate_patch(patch_slot_errado, base)
check("validate_patch rejeita slot inexistente", not ok, motivo)

# ============================================================
print("\n" + "=" * 65)
print("TESTE 7 — DATA-ROLE NÃO AUTORIZADO (deve REJEITAR)")
print("=" * 65)
patch_data_role = dict(patch_valido)
patch_data_role["mutations"] = [{
    "target_slot": "slot-header",
    "op": "replace_inner",
    "html": '<div data-role="hack-admin">lixo</div>'
}]
ok, motivo = validate_patch(patch_data_role, base)
check("validate_patch rejeita data-role nao autorizado", not ok, motivo)

# ============================================================
print("\n" + "=" * 65)
print("TESTE 8 — ROLLBACK (patch válido aplica, patch inválido não destrói)")
print("=" * 65)
html_apos_patch_valido, _ = apply_patch(base, patch_valido)
hash_apos_patch = compute_sha256(html_apos_patch_valido)

# Tenta aplicar um patch com hash antigo (do base original)
ok, motivo = validate_patch(patch_valido, html_apos_patch_valido)
check("patch antigo é rejeitado após alteração", not ok, motivo)

# Confirma que o HTML pós-patch válido permanece intacto
check("HTML válido pós-patch preservado",
      "score-x" in html_apos_patch_valido and compute_sha256(html_apos_patch_valido) == hash_apos_patch)

# ============================================================
print("\n" + "=" * 65)
print("RESUMO")
print("=" * 65)
total = len(resultados)
passou = sum(1 for _, ok in resultados if ok)
falhou = total - passou
print(f"  Total de testes: {total}")
print(f"  Passou:          {passou}")
print(f"  Falhou:          {falhou}")

if falhou == 0:
    print("\n  🏆 BATERIA COMPLETA: TODOS OS TESTES PASSARAM.")
    sys.exit(0)
else:
    print("\n  ⚠️  Existem testes a falhar. Corrigir antes de avançar.")
    sys.exit(1)