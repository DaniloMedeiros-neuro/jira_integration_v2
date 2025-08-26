#!/usr/bin/env python3
"""
Script de teste para demonstrar a funcionalidade de métricas de épicos
"""

import requests
import json
from datetime import datetime, timedelta
import random

# Configurações de teste
JIRA_BASE_URL = "https://neurotech.atlassian.net"
EPIC_KEY = "TLD-100"  # Substitua pelo ID do seu épico

def testar_metricas_epico():
    """Testa a rota de métricas de épico"""
    print("=== TESTANDO MÉTRICAS DE ÉPICO ===")
    
    try:
        response = requests.get(f"http://localhost:8081/api/metricas-epico/{EPIC_KEY}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Métricas obtidas com sucesso!")
            print(f"Épico: {data['epic_info']['key']} - {data['epic_info']['summary']}")
            print(f"Total de issues: {data['metricas_progresso']['total_issues']}")
            print(f"Percentual de conclusão: {data['metricas_progresso']['percentual_conclusao']}%")
            print(f"Story Points: {data['metricas_progresso']['story_points_total']}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def testar_analise_detalhada():
    """Testa a rota de análise detalhada de épico"""
    print("\n=== TESTANDO ANÁLISE DETALHADA DE ÉPICO ===")
    
    try:
        response = requests.get(f"http://localhost:8081/api/analise-epico-detalhada/{EPIC_KEY}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Análise detalhada obtida com sucesso!")
            print(f"Resumo:")
            print(f"  - Total de issues: {data['resumo']['total_issues']}")
            print(f"  - Histórias: {data['resumo']['stories_count']}")
            print(f"  - Tarefas: {data['resumo']['tasks_count']}")
            print(f"  - Bugs: {data['resumo']['bugs_count']}")
            
            print(f"\nProgresso:")
            print(f"  - Concluído: {data['progresso']['concluido']['count']} ({data['progresso']['concluido']['percentual']}%)")
            print(f"  - Em Progresso: {data['progresso']['em_progresso']['count']} ({data['progresso']['em_progresso']['percentual']}%)")
            print(f"  - Impedimento: {data['progresso']['impedimento']['count']} ({data['progresso']['impedimento']['percentual']}%)")
            
            print(f"\nStory Points:")
            print(f"  - Total: {data['story_points']['total']}")
            print(f"  - Concluído: {data['story_points']['concluido']}")
            print(f"  - Percentual: {data['story_points']['percentual_concluido']}%")
            
            print(f"\nCasos de Teste: {len(data['casos_teste'])} encontrados")
            
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def gerar_dados_mock():
    """Gera dados mock para teste"""
    print("\n=== GERANDO DADOS MOCK PARA TESTE ===")
    
    # Simular dados de épico
    epic_data = {
        "resumo": {
            "total_issues": 25,
            "stories_count": 15,
            "tasks_count": 8,
            "bugs_count": 2
        },
        "progresso": {
            "concluido": {"count": 12, "percentual": 48.0},
            "em_progresso": {"count": 8, "percentual": 32.0},
            "impedimento": {"count": 5, "percentual": 20.0}
        },
        "story_points": {
            "total": 85,
            "concluido": 42,
            "pendente": 43,
            "percentual_concluido": 49.4
        },
        "breakdown_status": {
            "Done": {"count": 12, "percentual": 48.0, "story_points": 42, "tempo_medio": 5.2},
            "In Progress": {"count": 8, "percentual": 32.0, "story_points": 28, "tempo_medio": 3.1},
            "To Do": {"count": 3, "percentual": 12.0, "story_points": 10, "tempo_medio": 0},
            "Blocked": {"count": 2, "percentual": 8.0, "story_points": 5, "tempo_medio": 7.5}
        },
        "casos_teste": [
            {
                "key": "TEST-001",
                "summary": "Teste de login",
                "status": "Done",
                "test_status": "Passed",
                "assignee": "João Silva",
                "ultima_execucao": "2024-01-15"
            },
            {
                "key": "TEST-002",
                "summary": "Teste de cadastro",
                "status": "In Progress",
                "test_status": "Failed",
                "assignee": "Maria Santos",
                "ultima_execucao": "2024-01-14"
            },
            {
                "key": "TEST-003",
                "summary": "Teste de busca",
                "status": "To Do",
                "test_status": "Not Executed",
                "assignee": "Pedro Costa",
                "ultima_execucao": "N/A"
            }
        ],
        "evolucao_escopo": {
            "labels": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"],
            "adicionados": [8, 5, 3, 2],
            "removidos": [0, 1, 0, 0]
        },
        "evolucao_velocidade": {
            "labels": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"],
            "velocidade": [12, 18, 15, 22],
            "throughput": [8, 12, 10, 15]
        },
        "distribuicao_tempo": {
            "1-3 dias": 35,
            "4-7 dias": 40,
            "8-14 dias": 20,
            "15+ dias": 5
        },
        "metricas_tempo": {
            "lead_time_medio": 6.8,
            "cycle_time_medio": 4.2,
            "velocidade_sprint": 16.8,
            "throughput_sprint": 11.3
        }
    }
    
    # Salvar dados mock em arquivo
    with open('dados_mock_epico.json', 'w', encoding='utf-8') as f:
        json.dump(epic_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Dados mock gerados e salvos em 'dados_mock_epico.json'")
    return epic_data

def main():
    """Função principal"""
    print("🚀 INICIANDO TESTES DE MÉTRICAS DE ÉPICO")
    print("=" * 50)
    
    # Gerar dados mock primeiro
    dados_mock = gerar_dados_mock()
    
    # Testar métricas básicas
    sucesso_metricas = testar_metricas_epico()
    
    # Testar análise detalhada
    sucesso_analise = testar_analise_detalhada()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print(f"Métricas básicas: {'✅ PASSOU' if sucesso_metricas else '❌ FALHOU'}")
    print(f"Análise detalhada: {'✅ PASSOU' if sucesso_analise else '❌ FALHOU'}")
    
    if sucesso_metricas and sucesso_analise:
        print("\n🎉 Todos os testes passaram! A funcionalidade está funcionando corretamente.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")
    
    print("\n💡 Para testar a interface web:")
    print("1. Acesse: http://localhost:8081/metricas")
    print("2. Digite o ID do épico: TLD-100")
    print("3. Clique em 'Analisar Épico'")
    print("4. Explore as diferentes abas de análise")

if __name__ == "__main__":
    main()
