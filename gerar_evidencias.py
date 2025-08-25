#!/usr/bin/env python3
"""
Script principal para gerar e adicionar evidências de testes ao Jira
Integra a extração de prints e o envio de evidências
"""

import os
import sys
from extrair_prints import extrair_prints
from adicionar_evidencias import processar_evidencias, processar_evidencia_especifica

def main():
    """Função principal que coordena o processo de evidências."""
    
    print("🎯 SISTEMA DE EVIDÊNCIAS DE TESTES")
    print("="*50)
    
    # Verificar se o arquivo log.html existe
    if not os.path.exists("log.html"):
        print("❌ Arquivo log.html não encontrado!")
        print("💡 Certifique-se de que o arquivo log.html está no diretório atual.")
        return
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            mostrar_ajuda()
            return
        elif len(sys.argv) == 3:
            # Processar evidência específica
            issue_key = sys.argv[1]
            tipo_resultado = sys.argv[2]
            processar_evidencia_especifica(issue_key, tipo_resultado)
            return
        else:
            print("❌ Argumentos inválidos!")
            mostrar_ajuda()
            return
    
    # Processo completo
    print("📋 Iniciando processo completo de evidências...")
    
    # Passo 1: Extrair prints
    print("\n🔍 PASSO 1: Extraindo prints de evidências...")
    extrair_prints()
    
    # Verificar se os prints foram gerados
    if not os.path.exists("prints_tests"):
        print("❌ Falha na extração de prints. Processo interrompido.")
        return
    
    # Contar arquivos gerados
    falhas_dir = os.path.join("prints_tests", "falhas")
    sucessos_dir = os.path.join("prints_tests", "sucessos")
    
    falhas_count = len([f for f in os.listdir(falhas_dir) if f.endswith('.png')]) if os.path.exists(falhas_dir) else 0
    sucessos_count = len([f for f in os.listdir(sucessos_dir) if f.endswith('.png')]) if os.path.exists(sucessos_dir) else 0
    
    if falhas_count == 0 and sucessos_count == 0:
        print("⚠️ Nenhum print foi gerado. Verifique o arquivo log.html.")
        return
    
    print(f"📊 Prints gerados: {falhas_count} falhas, {sucessos_count} sucessos")
    
    # Perguntar se deve continuar
    resposta = input("\n❓ Deseja enviar as evidências para o Jira? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        print("\n📤 PASSO 2: Enviando evidências para o Jira...")
        processar_evidencias()
    else:
        print("⏹️ Processo interrompido pelo usuário.")
        print("💡 Os prints estão disponíveis na pasta 'prints_tests/'")
    
    print("\n✅ Processo concluído!")

def mostrar_ajuda():
    """Mostra a ajuda do script."""
    print("""
📖 AJUDA - SISTEMA DE EVIDÊNCIAS

USO:
  python gerar_evidencias.py                    # Processo completo
  python gerar_evidencias.py ISSUE_KEY TIPO     # Evidência específica
  python gerar_evidencias.py --help             # Esta ajuda

EXEMPLOS:
  python gerar_evidencias.py                    # Extrai todos os prints e envia ao Jira
  python gerar_evidencias.py CREDT-1343 sucessos # Envia evidência específica
  python gerar_evidencias.py CREDT-1343 falhas   # Envia evidência de falha

TIPOS DE RESULTADO:
  sucessos  - Evidências de testes que passaram
  falhas    - Evidências de testes que falharam

PRÉ-REQUISITOS:
  - Arquivo log.html no diretório atual
  - Variáveis de ambiente configuradas (.env)
  - Conexão com o Jira

ESTRUTURA GERADA:
  prints_tests/
  ├── falhas/     # Screenshots de testes que falharam
  └── sucessos/   # Screenshots de testes que passaram
    """)

if __name__ == "__main__":
    main()
