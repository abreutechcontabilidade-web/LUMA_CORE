# ONDE O SEU ONNX FLUTUANTE VAI VIVER
# Esta função recebe o prompt e o miolo atual, e decide a mutação.

def inferir_mutacao(prompt, miolo):
    # Se o seu ONNX estiver instalado, ele faria:
    # import onnxruntime as ort
    # session = ort.InferenceSession("motor_vivo.onnx")
    # result = session.run(...)
    
    # Por agora, o fallback heurístico para provar o conceito:
    p = prompt.lower()
    mutacoes = []
    
    if "cor" in p and "background" not in miolo["tags"]:
        mutacoes.append({"tipo": "css", "valor": "body { background: #8b0000; color: white; }"})
    if "som" in p and "audio" not in miolo["tags"]:
        mutacoes.append({"tipo": "js", "valor": "function tocarSom() { new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=').play(); }"})
    
    return mutacoes

def aplicar_mutacoes(html, mutacoes):
    novo_html = html
    for m in mutacoes:
        if m["tipo"] == "css" and "</style>" in novo_html:
            novo_html = novo_html.replace("</style>", m["valor"] + "</style>")
        if m["tipo"] == "js" and "</script>" in novo_html:
            novo_html = novo_html.replace("</script>", m["valor"] + "</script>")
    return novo_html