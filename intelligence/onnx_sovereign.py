
def extrair_chave(prompt):
    p = prompt.lower()
    if "cobr" in p or "snake" in p: return "jogo da cobra"
    if "velha" in p or "tic" in p: return "jogo da velha"
    if "calculadora" in p or "calculator" in p: return "calculadora"
    if "cronometro" in p or "timer" in p: return "cronometro"
    if "tarefa" in p or "todo" in p: return "lista de tarefas"
    return " ".join(p.split()[:3])

def buscar_no_genoma(prompt, memoria):
    if not memoria:
        return None, 0.0
        
    chave_pedida = extrair_chave(prompt)
    
    # 1. Procura exata
    if chave_pedida in memoria:
        return chave_pedida, 1.0
    if chave_pedida.replace(" ", "_") in memoria:
        return chave_pedida.replace(" ", "_"), 1.0
        
    # 2. Procura por substring estrita (sem difflib)
    if "cobra" in chave_pedida:
        for k in memoria.keys():
            if "cobra" in k.lower() or "snake" in k.lower():
                return k, 1.0
    if "velha" in chave_pedida:
        for k in memoria.keys():
            if "velha" in k.lower() or "tic" in k.lower():
                return k, 1.0
    if "calculadora" in chave_pedida:
        for k in memoria.keys():
            if "calculadora" in k.lower():
                return k, 1.0
                
    return None, 0.0
