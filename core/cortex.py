# -*- coding: utf-8 -*-
from datetime import datetime

def avaliar_bioritmo():
    hora = datetime.now().hour
    
    if 5 <= hora < 12:
        return {
            "periodo": "Manhã",
            "foco": "Alto",
            "diretriz": "Pico de clareza mental. Ideal para arquitetura de código complexo e tomadas de decisão."
        }
    elif 12 <= hora < 18:
        return {
            "periodo": "Tarde",
            "foco": "Sustentação",
            "diretriz": "Energia em platô. Bom para execução de tarefas, revisões e testes de QA."
        }
    else:
        return {
            "periodo": "Noite",
            "foco": "Recuperação",
            "diretriz": "Melatonina em alta. Reduza a luz azul e foque em documentação leve ou refatoração simples."
        }