#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""luma_patch.py - Patcher deterministico do ecossistema LUMA."""
import argparse, sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def aplicar_edits(texto, edits):
    for i, e in enumerate(edits, 1):
        find = e.get('find', '')
        replace = e.get('replace', '')
        count_esp = e.get('count', 1)
        if not find:
            print(f'[FALHA] edit #{i}: "find" vazio'); return None
        n = texto.count(find)
        if n != count_esp:
            print(f'[FALHA] edit #{i}: encontrei {n}, esperava {count_esp}')
            return None
        texto = texto.replace(find, replace, count_esp)
        print(f'[OK] edit #{i}: {count_esp} substituicao(oes)')
    return texto


def validar(texto, require=None, forbid=None):
    for s in (require or []):
        if s not in texto:
            print(f'[FALHA] require_after: {s[:80]}'); return False
    for s in (forbid or []):
        if s in texto:
            print(f'[FALHA] forbid_after: {s[:80]}'); return False
    return True


def carregar_regra(path):
    if not HAS_YAML:
        print('[FALHA] pip install pyyaml'); return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f'[FALHA] {e}'); return None


def main():
    ap = argparse.ArgumentParser(description='LUMA patch')
    ap.add_argument('--rule')
    ap.add_argument('--file')
    ap.add_argument('--find')
    ap.add_argument('--replace')
    ap.add_argument('--count', type=int, default=1)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    if args.rule:
        regra = carregar_regra(args.rule)
        if not regra: sys.exit(1)
        target = Path(regra['file'])
        edits = regra.get('edits', [])
        require = regra.get('require_after', [])
        forbid = regra.get('forbid_after', [])
    elif args.file and args.find is not None:
        target = Path(args.file)
        edits = [{'find': args.find, 'replace': args.replace, 'count': args.count}]
        require, forbid = [], []
    else:
        print('Uso: --rule <yaml> OU --file <f> --find <s> --replace <s>')
        sys.exit(1)

    if not target.exists():
        print(f'[FALHA] ficheiro nao existe: {target}'); sys.exit(1)

    raw = target.read_bytes()
    tem_bom = raw[:3] == b'\xef\xbb\xbf'
    texto = raw.decode('utf-8-sig' if tem_bom else 'utf-8')

    print(f'[INFO] alvo: {target}  ({len(texto)} bytes{"  BOM" if tem_bom else ""})')
    novo = aplicar_edits(texto, edits)
    if novo is None: sys.exit(2)
    if not validar(novo, require, forbid): sys.exit(3)

    if args.dry_run:
        print('[DRY-RUN] nada escrito')
        sys.exit(0)

    target.write_bytes(novo.encode('utf-8'))
    print(f'[OK] escrito: {target}  ({len(novo)} bytes, {len(novo)-len(texto):+d})')


if __name__ == '__main__':
    main()