# -*- coding: utf-8 -*-
"""reflexo.py - Motor reflexo. Avalia condicoes e aplica patches. Sem LLM."""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
REFLEXOS = BASE / "reflexos.json"
PATCHES = BASE / "patches"
LOG = BASE / "reflexo.log"


def log(msg, nivel="info"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{ts}] [{nivel.upper()}] {msg}"
    print(linha)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
    except Exception:
        pass


def avaliar_regra(regra):
    cond = regra.get("se", {})
    ficheiro = cond.get("ficheiro", "")
    path = Path(ficheiro)
    if not path.exists():
        log(f"  ficheiro nao existe: {ficheiro}", "aviso")
        return False
    try:
        conteudo = path.read_text(encoding="utf-8")
    except Exception as e:
        log(f"  erro lendo {ficheiro}: {e}", "erro")
        return False
    if "nao_contem" in cond:
        return cond["nao_contem"] not in conteudo
    if "contem" in cond:
        return cond["contem"] in conteudo
    return False


def aplicar_patch(patch_nome, dry_run=False):
    patch_path = PATCHES / patch_nome
    if not patch_path.exists():
        log(f"  patch nao existe: {patch_nome}", "erro")
        return False
    cmd = [sys.executable, str(BASE / "motor.py"), str(patch_path)]
    if not dry_run:
        cmd.append("--apply")
    log(f"  -> {patch_nome} (dry_run={dry_run})")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        log(f"  timeout: {patch_nome}", "erro")
        return False
    stdout = (r.stdout or "") + (r.stderr or "")
    # R5 SKIP = motor recusou duplicacao = SUCESSO (imunidade ativa)
    if "R5 SKIP" in stdout or "ja existe" in stdout:
        log(f"  IMUNE: {patch_nome} (R5 SKIP - ja aplicado)")
        return True
    if r.returncode == 0:
        log(f"  OK: {patch_nome}")
        return True
    log(f"  FALHA: {patch_nome} | out={r.stdout[:150]} err={r.stderr[:150]}", "erro")
    return False


def correr(dry_run=True):
    if not REFLEXOS.exists():
        log("reflexos.json nao encontrado", "erro")
        return 1
    dados = json.loads(REFLEXOS.read_text(encoding="utf-8"))
    regras = dados.get("regras", [])
    log(f"Avaliando {len(regras)} regras (dry_run={dry_run})")
    aplicados = 0
    disparadas = 0
    for regra in regras:
        rid = regra.get("id", "?")
        desc = regra.get("descricao", "")
        log(f"Regra {rid}: {desc}")
        if avaliar_regra(regra):
            disparadas += 1
            log(f"  DISPAROU -> {regra.get('entao')}")
            if aplicar_patch(regra["entao"], dry_run):
                aplicados += 1
        else:
            log(f"  condicao nao bate")
    log(f"Total: {disparadas} disparadas, {aplicados} aplicadas")
    return 0


if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    sys.exit(correr(dry_run=dry))
