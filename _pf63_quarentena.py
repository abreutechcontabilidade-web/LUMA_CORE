import os, shutil, time
ART = r"C:\Users\user\Desktop\LUMA_CORE\intelligence\artefacts"
TS = time.strftime("%Y%m%d_%H%M%S")
if not os.path.isdir(ART):
    print("[AVISO] pasta artefacts nao existe - nada a quarentenar."); raise SystemExit
movidos = 0
for fn in sorted(os.listdir(ART)):
    p = os.path.join(ART, fn)
    if not os.path.isfile(p) or ".bak_" in fn or ".quarentena_" in fn:
        continue
    if fn.startswith("chave_") and not fn.endswith(".html"):
        continue
    try:
        shutil.move(p, p + ".bak_pf63_" + TS)
        movidos += 1
    except Exception as e:
        print("[AVISO] nao pude recolher %s: %r" % (fn, e))
print("[OK] QUARENTENA (reversivel): %d artefacto(s) recolhido(s)." % movidos)