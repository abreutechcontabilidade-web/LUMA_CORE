# -*- coding: utf-8 -*-
"""Testa chaves com auto-deteção de provider pelo formato."""
import warnings
warnings.filterwarnings("ignore")
from providers import PROVIDERS
from key_detector import resolver, detetar_provider


def _classificar_erro(msg: str) -> str:
    m = msg.lower()
    if "429" in msg or "quota" in m or "exhausted" in m:
        return "QUOTA_ESGOTADA (esperar ~24h)"
    if "401" in msg or "unauthorized" in m or "invalid api key" in m:
        return "CHAVE_INVALIDA"
    if "403" in msg or "permission" in m:
        return "SEM_PERMISSAO / surface errada"
    if "404" in msg or "not found" in m:
        return "MODELO_NAO_EXISTE"
    if "503" in msg or "unavailable" in m:
        return "SERVIDOR_OCUPADO"
    return "ERRO_DESCONHECIDO"


def _testar_google_genai(api_key, modelo, base_url=None):
    """Testa Gemini AI Studio ou Vertex Express."""
    from google import genai
    try:
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["http_options"] = {"base_url": base_url}
        client = genai.Client(**kwargs)
        r = client.models.generate_content(model=modelo, contents="Diz OK")
        return True, (r.text or "")[:30], ""
    except Exception as e:
        return False, "", str(e)[:200]


def _testar_openai_compat(api_key, base_url, modelo):
    from openai import OpenAI
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        r = client.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": "Diz OK"}],
            max_tokens=10,
        )
        return True, (r.choices[0].message.content or "")[:30], ""
    except Exception as e:
        return False, "", str(e)[:200]


def _testar_anthropic(api_key, modelo):
    from anthropic import Anthropic
    try:
        client = Anthropic(api_key=api_key)
        r = client.messages.create(
            model=modelo, max_tokens=10,
            messages=[{"role": "user", "content": "Diz OK"}],
        )
        return True, (r.content[0].text or "")[:30], ""
    except Exception as e:
        return False, "", str(e)[:200]


def _testar_gemini_dual(api_key):
    """
    AQ. keys podem ser AI Studio OU Vertex Express.
    Tenta AI Studio primeiro (mais comum), depois Vertex.
    """
    resultados = []
    superficies = [
        ("gemini_studio", "AI Studio", None),
        ("gemini_vertex", "Vertex Express",
         "https://aiplatform.googleapis.com/v1beta1"),
    ]

    for nome, rotulo, base_url in superficies:
        for modelo in PROVIDERS["gemini"]["modelos_candidatos"]:
            ok, msg, err = _testar_google_genai(api_key, modelo, base_url)
            if ok:
                return {
                    "provider": "gemini",
                    "surface": nome,
                    "surface_label": rotulo,
                    "modelo": modelo,
                    "ok": True,
                    "msg": msg,
                    "erro_raw": "",
                    "tentativas": resultados,
                }
            resultados.append({
                "surface": rotulo,
                "modelo": modelo,
                "ok": False,
                "msg": _classificar_erro(err),
            })

    return {
        "provider": "gemini",
        "surface": None,
        "surface_label": None,
        "modelo": None,
        "ok": False,
        "msg": "FALHOU em ambas as superficies",
        "erro_raw": resultados[-1]["msg"] if resultados else "",
        "tentativas": resultados,
    }


def _testar_provider_direto(provider_nome, api_key):
    """Testa um provider especifico (nao Gemini)."""
    p = PROVIDERS.get(provider_nome)
    if not p:
        return {"provider": provider_nome, "modelo": None, "ok": False,
                "msg": "Provider desconhecido", "tentativas": []}

    resultados = []
    for modelo in p["modelos_candidatos"]:
        if p["sdk"] == "google-genai":
            ok, msg, err = _testar_google_genai(api_key, modelo)
        elif p["sdk"] == "anthropic":
            ok, msg, err = _testar_anthropic(api_key, modelo)
        else:
            ok, msg, err = _testar_openai_compat(api_key, p["base_url"], modelo)

        resultados.append({
            "modelo": modelo,
            "ok": ok,
            "msg": msg if ok else _classificar_erro(err),
        })

        if ok:
            return {"provider": provider_nome, "modelo": modelo, "ok": True,
                    "msg": msg, "erro_raw": "", "tentativas": resultados}

    ultimo = resultados[-1] if resultados else {"msg": "sem tentativas"}
    return {
        "provider": provider_nome,
        "modelo": None,
        "ok": False,
        "msg": ultimo["msg"],
        "erro_raw": "",
        "tentativas": resultados,
    }


def resolver_chave(api_key: str, override_provider: str = None) -> dict:
    """
    Resolve uma chave: deteta provider + testa modelos + devolve resultado unificado.
    """
    plano = resolver(api_key, override_provider)
    detetado = detetar_provider(api_key)

    resultado_final = {
        "key_alias": f"...{api_key[-6:]}" if len(api_key) > 6 else "KEY",
        "provider_detetado": detetado,
        "modo_resolucao": plano["modo"],
        "resultado": None,
    }

    for prov in plano["tentar_providers"]:
        if prov == "gemini":
            r = _testar_gemini_dual(api_key)
        else:
            r = _testar_provider_direto(prov, api_key)

        if r["ok"]:
            resultado_final["resultado"] = r
            resultado_final["provider_resolvido"] = prov
            return resultado_final

    # Nenhum funcionou - devolve o ultimo resultado para diagnostico
    ultimo = r if 'r' in dir() else {"msg": "sem tentativas"}
    resultado_final["resultado"] = ultimo
    resultado_final["provider_resolvido"] = None
    return resultado_final


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python model_discovery.py <api_key> [provider_override]")
        print("Ex: python model_discovery.py AQ.Ab8...")
        sys.exit(0)

    key = sys.argv[1]
    override = sys.argv[2] if len(sys.argv) > 2 else None
    print(f"[DETEcAO] Formato: {detetar_provider(key)}")
    r = resolver_chave(key, override)
    print(f"[MODO] {r['modo_resolucao']}")
    if r["resultado"] and r["resultado"]["ok"]:
        print(f"[OK] {r['provider_resolvido']} / {r['resultado']['modelo']}")
        if r["resultado"].get("surface"):
            print(f"     Surface: {r['resultado']['surface_label']}")
    else:
        print(f"[X] Falhou: {r['resultado'].get('msg')}")