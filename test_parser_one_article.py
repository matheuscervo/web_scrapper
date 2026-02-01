"""Teste do parser com artigo real"""
import asyncio
from parser import run_parser

def test():
    # Artigo exemplo (pode ser qualquer um)
    url = "https://uxdesign.cc/the-state-of-ux-in-2025-78cd11488c5d" # Exemplo hipotético
    # Vou usar um url real garantido de ser acessível se não houver bloqueio
    url = "https://medium.com/design-bootcamp/ux-case-study-redesigning-the-cinema-ticket-booking-experience-5c45663708e3" 
    
    print(f"Testando parser em: {url}")
    data = run_parser(url)
    
    if data:
        print("\nSucesso! Metadados extraídos:")
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("\nFalha na extração (Bloqueio ou Erro)")

if __name__ == "__main__":
    test()
