# -*- coding: utf-8 -*-
"""LUMAZBIT Multi-Fallback v3 - gera resposta real (nao apenas testa)."""
import json
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from providers import PROVIDERS


def carregar_vault():
    vault_path = Path(__file__).parent / "vault.json"
    if vault_path.exists():
        with open(vault_path, "r", encoding="utf-8") as f:
            return json.load(f)
    if Path("vault.json").exists():
        with open("vault.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


ORDEM_PRIORIDADE = ["openrouter", "gemini", "groq", "deepseek", "zai", "anthropic", "mistral"]


# Graft 9 — modelo default por provider (quando vault nao define)
MODELO_DEFAULT = {
    "gemini":     "gemini-2.0-flash",
    "zai":        "glm-4-plus",
    "groq":       "llama-3.3-70b-versatile",
    "openrouter": "google/gemini-2.0-flash-exp",
    "deepseek":   "deepseek-chat",
    "anthropic":  "claude-3-5-sonnet-20241022",
    "mistral":    "mistral-large-latest",
    "openai":     "gpt-4o-mini",
    "together":   "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "cerebras":   "llama-3.3-70b",
}


def _pendente_recente(item):
    """True = NAO tentar (pendente ha menos de 24h).
    Sem timestamp ou data ilegivel = assumir antigo = TENTAR."""
    from datetime import datetime, timezone, timedelta
    if item.get("estado") == "ok":
        return False
    add = item.get("adicionado_em") or item.get("criado_em")
    if not add:
        return False
    try:
        dt = datetime.fromisoformat(str(add).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt) < timedelta(hours=24)
    except Exception:
        return False


def _gerar_gemini(key, modelo, prompt, system=None, surface=None):
    from google import genai
    from google.genai import types
    kwargs = {"api_key": key}
    if surface == "gemini_vertex":
        kwargs["http_options"] = {"base_url": "https://aiplatform.googleapis.com/v1beta1"}
    client = genai.Client(**kwargs)

    cfg = None
    if system:
        cfg = types.GenerateContentConfig(system_instruction=system, temperature=0.2)
    call_kwargs = {"model": modelo, "contents": prompt}
    if cfg:
        call_kwargs["config"] = cfg
    r = client.models.generate_content(**call_kwargs)
    return r.text


def _gerar_openai_compat(base_url, key, modelo, prompt, system=None):
    from openai import OpenAI
    client = OpenAI(api_key=key, base_url=base_url)
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    r = client.chat.completions.create(model=modelo, messages=msgs, max_tokens=1024)
    return r.choices[0].message.content


def _gerar_anthropic(key, modelo, prompt, system=None):
    from anthropic import Anthropic
    client = Anthropic(api_key=key)
    kwargs = {"model": modelo, "max_tokens": 1024,
              "messages": [{"role": "user", "content": prompt}]}
    if system:
        kwargs["system"] = system
    r = client.messages.create(**kwargs)
    return r.content[0].text


def gerar_com_fallback(prompt, system=None):
    """Gera resposta REAL usando os providers do vault em cascata."""
    vault = carregar_vault()
    if not vault:
        return None, None, None

    tentativas = 0
    for prov in ORDEM_PRIORIDADE:
        if prov not in vault or not vault[prov]:
            continue

        for item in vault[prov]:
            # Graft 9 — ok OU pendente ha > 24h (retry)
            if _pendente_recente(item):
                continue
            key = item["key"]
            # Graft 9 — modelo default se null
            modelo = item.get("modelo") or MODELO_DEFAULT.get(prov)
            surface = item.get("surface")
            if not modelo:
                continue

            tentativas += 1
            print(f"  [->] {prov}/{modelo}")

            try:
                p = PROVIDERS[prov]
                if p["sdk"] == "google-genai":
                    resp = _gerar_gemini(key, modelo, prompt, system, surface)
                elif p["sdk"] == "anthropic":
                    resp = _gerar_anthropic(key, modelo, prompt, system)
                else:
                    resp = _gerar_openai_compat(p["base_url"], key, modelo, prompt, system)

                print(f"  [OK] Resposta via {prov}/{modelo}")
                return resp, prov, modelo
            except Exception as e:
                print(f"  [X] {prov}/{modelo}: {str(e)[:80]}")
                continue

    print(f"\n[INFO] {tentativas} tentativas falharam.")
    return None, None, None


if __name__ == "__main__":
    print("\n[$c$] LUMAZBIT MULTI-FALLBACK v3 (geracao real)\n")
    resp, prov, modelo = gerar_com_fallback("Quanto e 2+2?")
    if resp:
        print(f"\n[RESULTADO] {prov}/{modelo}:")
        print(resp[:300])
    else:
        print("\n[FALHA] Nenhum provider respondeu.")
