# -*- coding: utf-8 -*-
"""Registo universal de providers de IA."""

PROVIDERS = {
    "gemini": {
        "nome": "Google Gemini",
        "sdk": "google-genai",
        "env_var": "GEMINI_API_KEY",
        "modelos_candidatos": [
            "gemini-3.8-flash",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ],
    },
    "deepseek": {
        "nome": "DeepSeek",
        "sdk": "openai",
        "base_url": "https://api.deepseek.com/v1",
        "env_var": "DEEPSEEK_API_KEY",
        "modelos_candidatos": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"],
    },
    "zai": {
        "nome": "Z.ai (Zhipu)",
        "sdk": "openai",
        "base_url": "https://api.z.ai/api/paas/v4/",
        "env_var": "ZAI_API_KEY",
        "modelos_candidatos": ["glm-4.7", "glm-4.5-air", "glm-4-flash", "glm-5.3"],
    },
    "openai": {
        "nome": "OpenAI",
        "sdk": "openai",
        "base_url": "https://api.openai.com/v1",
        "env_var": "OPENAI_API_KEY",
        "modelos_candidatos": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "anthropic": {
        "nome": "Anthropic Claude",
        "sdk": "anthropic",
        "env_var": "ANTHROPIC_API_KEY",
        "modelos_candidatos": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
    },
    "groq": {
        "nome": "Groq (ultra-rapido)",
        "sdk": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "env_var": "GROQ_API_KEY",
        "modelos_candidatos": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
    },
    "mistral": {
        "nome": "Mistral AI",
        "sdk": "openai",
        "base_url": "https://api.mistral.ai/v1",
        "env_var": "MISTRAL_API_KEY",
        "modelos_candidatos": ["mistral-large-latest", "mistral-small-latest"],
    },
    "openrouter": {
        "nome": "OpenRouter (agregador)",
        "sdk": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "env_var": "OPENROUTER_API_KEY",
        "modelos_candidatos": [
            "deepseek/deepseek-chat",
            "google/gemini-2.0-flash-exp:free",
            "meta-llama/llama-3.3-70b-instruct:free",
        ],
    },
    "together": {
        "nome": "Together AI",
        "sdk": "openai",
        "base_url": "https://api.together.xyz/v1",
        "env_var": "TOGETHER_API_KEY",
        "modelos_candidatos": [
            "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "Qwen/Qwen2.5-72B-Instruct-Turbo",
        ],
    },
    "cerebras": {
        "nome": "Cerebras Cloud",
        "sdk": "openai",
        "base_url": "https://api.cerebras.ai/v1",
        "env_var": "CEREBRAS_API_KEY",
        "modelos_candidatos": [
            "llama-3.3-70b",
            "llama3.1-8b",
            "llama-3.1-70b",
        ],
    },
}


def listar_providers():
    return list(PROVIDERS.keys())


def obter_provider(nome):
    return PROVIDERS.get(nome.lower())


def info():
    for k, v in PROVIDERS.items():
        print(f"  {k:12} -> {v['nome']:25} ({len(v['modelos_candidatos'])} modelos)")


if __name__ == "__main__":
    info()