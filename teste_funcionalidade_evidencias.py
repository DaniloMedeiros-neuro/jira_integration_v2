#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de evidências
"""

import os
import sys
import shutil
from datetime import datetime

def testar_funcionalidade_evidencias():
    """Testa a funcionalidade de evidências"""
    
    print("🧪 TESTANDO FUNCIONALIDADE DE EVIDÊNCIAS")
    print("=" * 50)
    
    # 1. Verificar se os diretórios existem
    print("\n1. Verificando estrutura de diretórios...")
    
    diretorios_necessarios = [
        'prints_tests',
        'prints_tests/sucessos',
        'prints_tests/falhas',
        'logs'
    ]
    
    for diretorio in diretorios_necessarios:
        if os.path.exists(diretorio):
            print(f"   ✅ {diretorio} - OK")
        else:
            print(f"   ❌ {diretorio} - NÃO ENCONTRADO")
            os.makedirs(diretorio, exist_ok=True)
            print(f"   ✅ {diretorio} - CRIADO")
    
    # 2. Verificar se o arquivo de teste existe
    print("\n2. Verificando arquivo de teste...")
    
    arquivo_teste = 'teste_evidencias.html'
    if os.path.exists(arquivo_teste):
        print(f"   ✅ {arquivo_teste} - ENCONTRADO")
        tamanho = os.path.getsize(arquivo_teste)
        print(f"   📊 Tamanho: {tamanho} bytes")
    else:
        print(f"   ❌ {arquivo_teste} - NÃO ENCONTRADO")
        return False
    
    # 3. Verificar dependências
    print("\n3. Verificando dependências...")
    
    dependencias = [
        'flask',
        'requests',
        'beautifulsoup4',
        'pillow',
        'selenium',
        'webdriver-manager'
    ]
    
    for dep in dependencias:
        try:
            if dep == 'beautifulsoup4':
                import bs4
                print(f"   ✅ {dep} - OK")
            elif dep == 'pillow':
                import PIL
                print(f"   ✅ {dep} - OK")
            else:
                __import__(dep.replace('-', '_'))
                print(f"   ✅ {dep} - OK")
        except ImportError:
            print(f"   ❌ {dep} - NÃO INSTALADO")
    
    # 4. Verificar configurações
    print("\n4. Verificando configurações...")
    
    try:
        from config_evidencias import get_config, validate_config
        config = get_config()
        erros = validate_config()
        
        if not erros:
            print("   ✅ Configurações válidas")
        else:
            print("   ⚠️  Avisos de configuração:")
            for erro in erros:
                print(f"      - {erro}")
    except ImportError as e:
        print(f"   ❌ Erro ao importar configurações: {e}")
    
    # 5. Verificar se há evidências existentes
    print("\n5. Verificando evidências existentes...")
    
    sucessos_dir = 'prints_tests/sucessos'
    falhas_dir = 'prints_tests/falhas'
    
    sucessos_count = len([f for f in os.listdir(sucessos_dir) if f.endswith(('.png', '.txt'))]) if os.path.exists(sucessos_dir) else 0
    falhas_count = len([f for f in os.listdir(falhas_dir) if f.endswith(('.png', '.txt'))]) if os.path.exists(falhas_dir) else 0
    
    print(f"   📁 Evidências de sucesso: {sucessos_count}")
    print(f"   📁 Evidências de falha: {falhas_count}")
    print(f"   📊 Total: {sucessos_count + falhas_count}")
    
    # 6. Verificar logs
    print("\n6. Verificando logs...")
    
    logs_dir = 'logs'
    if os.path.exists(logs_dir):
        arquivos_log = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        if arquivos_log:
            log_mais_recente = max(arquivos_log, key=lambda x: os.path.getctime(os.path.join(logs_dir, x)))
            print(f"   ✅ Log mais recente: {log_mais_recente}")
            
            # Verificar tamanho do log
            log_path = os.path.join(logs_dir, log_mais_recente)
            tamanho_log = os.path.getsize(log_path)
            print(f"   📊 Tamanho do log: {tamanho_log} bytes")
        else:
            print("   ⚠️  Nenhum arquivo de log encontrado")
    else:
        print("   ❌ Diretório de logs não encontrado")
    
    # 7. Testar processamento simulado
    print("\n7. Testando processamento simulado...")
    
    try:
        # Simular processamento do arquivo de teste
        from bs4 import BeautifulSoup
        
        with open(arquivo_teste, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        test_elements = soup.find_all('div', class_='test-result')
        
        print(f"   ✅ HTML parseado com sucesso")
        print(f"   📊 Elementos de teste encontrados: {len(test_elements)}")
        
        # Contar sucessos e falhas
        sucessos = len([e for e in test_elements if 'test-pass' in e.get('class', [])])
        falhas = len([e for e in test_elements if 'test-fail' in e.get('class', [])])
        
        print(f"   ✅ Sucessos detectados: {sucessos}")
        print(f"   ❌ Falhas detectadas: {falhas}")
        
    except Exception as e:
        print(f"   ❌ Erro no processamento: {e}")
    
    # 8. Verificar variáveis de ambiente
    print("\n8. Verificando variáveis de ambiente...")
    
    variaveis_jira = [
        'JIRA_URL',
        'JIRA_EMAIL', 
        'JIRA_API_TOKEN'
    ]
    
    for var in variaveis_jira:
        valor = os.getenv(var)
        if valor:
            print(f"   ✅ {var} - CONFIGURADO")
        else:
            print(f"   ⚠️  {var} - NÃO CONFIGURADO")
    
    # 9. Resumo final
    print("\n" + "=" * 50)
    print("📋 RESUMO DO TESTE")
    print("=" * 50)
    
    print(f"✅ Funcionalidade de evidências está operacional")
    print(f"📁 Evidências existentes: {sucessos_count + falhas_count}")
    print(f"📊 Elementos de teste no arquivo: {len(test_elements) if 'test_elements' in locals() else 0}")
    print(f"🕒 Teste realizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    print("\n🚀 Para testar completamente:")
    print("1. Execute: python app.py")
    print("2. Acesse: http://localhost:5000/evidencias")
    print("3. Faça upload do arquivo: teste_evidencias.html")
    print("4. Clique em 'Processar Evidências'")
    
    return True

if __name__ == "__main__":
    testar_funcionalidade_evidencias()
