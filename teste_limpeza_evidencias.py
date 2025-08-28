#!/usr/bin/env python3
"""
Teste da Limpeza Automática de Evidências
=========================================

Este script testa se a funcionalidade de limpeza automática
de evidências anteriores está funcionando corretamente.
"""

import os
import sys
import time
import shutil
from datetime import datetime

def criar_evidencias_teste():
    """Cria evidências de teste para simular processamento anterior"""
    
    print("🧪 CRIANDO EVIDÊNCIAS DE TESTE")
    print("=" * 40)
    
    # Criar diretórios
    os.makedirs('prints_tests/sucessos', exist_ok=True)
    os.makedirs('prints_tests/falhas', exist_ok=True)
    
    # Criar arquivos de teste
    evidencias_teste = [
        ('sucessos', 'TESTE_001_sucesso.png'),
        ('sucessos', 'TESTE_002_sucesso.png'),
        ('sucessos', 'BC-123_sucesso.png'),
        ('falhas', 'TESTE_003_falha.png'),
        ('falhas', 'BUG-456_falha.png'),
        ('sucessos', 'PROJ-789_sucesso.png')
    ]
    
    arquivos_criados = 0
    
    for diretorio, arquivo in evidencias_teste:
        caminho = os.path.join('prints_tests', diretorio, arquivo)
        
        # Criar arquivo vazio (simulando screenshot)
        with open(caminho, 'w') as f:
            f.write(f"Evidência de teste: {arquivo}")
        
        arquivos_criados += 1
        print(f"   📄 Criado: {caminho}")
    
    print(f"✅ {arquivos_criados} evidências de teste criadas")
    return arquivos_criados

def verificar_evidencias():
    """Verifica quantas evidências existem"""
    
    sucessos_dir = 'prints_tests/sucessos'
    falhas_dir = 'prints_tests/falhas'
    
    sucessos_count = 0
    falhas_count = 0
    
    if os.path.exists(sucessos_dir):
        sucessos_count = len([f for f in os.listdir(sucessos_dir) if f.endswith('.png')])
    
    if os.path.exists(falhas_dir):
        falhas_count = len([f for f in os.listdir(falhas_dir) if f.endswith('.png')])
    
    total = sucessos_count + falhas_count
    
    print(f"📊 Evidências encontradas: {total} ({sucessos_count} sucessos, {falhas_count} falhas)")
    return total

def testar_limpeza_automatica():
    """Testa a limpeza automática durante o processamento"""
    
    print("\n🧪 TESTE DA LIMPEZA AUTOMÁTICA")
    print("=" * 40)
    
    # Importar a função de limpeza
    try:
        sys.path.insert(0, os.getcwd())
        from app import limpar_evidencias_anteriores
        
        print("1️⃣ Verificando evidências antes da limpeza...")
        total_antes = verificar_evidencias()
        
        if total_antes == 0:
            print("⚠️ Nenhuma evidência encontrada para limpar")
            return False
        
        print("\n2️⃣ Executando limpeza automática...")
        start_time = time.time()
        
        arquivos_removidos = limpar_evidencias_anteriores()
        
        end_time = time.time()
        tempo_limpeza = end_time - start_time
        
        print(f"\n3️⃣ Verificando evidências após a limpeza...")
        total_depois = verificar_evidencias()
        
        print(f"\n📊 RESULTADOS:")
        print(f"   📄 Evidências antes: {total_antes}")
        print(f"   🗑️ Arquivos removidos: {arquivos_removidos}")
        print(f"   📄 Evidências depois: {total_depois}")
        print(f"   ⏱️ Tempo de limpeza: {tempo_limpeza:.2f} segundos")
        
        if total_depois == 0:
            print("✅ Limpeza automática funcionando corretamente!")
            return True
        else:
            print("❌ Limpeza automática falhou - ainda há evidências")
            return False
            
    except ImportError as e:
        print(f"❌ Erro ao importar função: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

def testar_limpeza_api():
    """Testa a API de limpeza manual"""
    
    print("\n🌐 TESTE DA API DE LIMPEZA")
    print("=" * 30)
    
    try:
        import requests
        
        # Criar algumas evidências de teste
        criar_evidencias_teste()
        
        print("1️⃣ Verificando evidências antes da limpeza via API...")
        total_antes = verificar_evidencias()
        
        if total_antes == 0:
            print("⚠️ Nenhuma evidência encontrada para limpar")
            return False
        
        print("\n2️⃣ Chamando API de limpeza...")
        response = requests.post('http://localhost:8081/api/evidencias/limpar')
        
        if response.status_code == 200:
            resultado = response.json()
            
            if resultado.get('sucesso'):
                print(f"✅ API de limpeza funcionando!")
                print(f"   📄 Arquivos removidos: {resultado.get('arquivos_removidos', 0)}")
                
                print("\n3️⃣ Verificando evidências após limpeza via API...")
                total_depois = verificar_evidencias()
                
                if total_depois == 0:
                    print("✅ Limpeza via API funcionando corretamente!")
                    return True
                else:
                    print("❌ Limpeza via API falhou - ainda há evidências")
                    return False
            else:
                print(f"❌ Erro na API: {resultado.get('erro', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except ImportError:
        print("❌ Requests não disponível")
        return False
    except Exception as e:
        print(f"❌ Erro durante teste da API: {e}")
        return False

def mostrar_instrucoes():
    """Mostra instruções de uso"""
    
    print("\n📖 INSTRUÇÕES DE USO")
    print("=" * 25)
    
    print("""
🔧 LIMPEZA AUTOMÁTICA:
   - Acontece automaticamente antes de cada processamento
   - Remove todas as evidências anteriores
   - Garante que não há conflitos ou duplicatas

🔧 LIMPEZA MANUAL:
   - Acesse: http://localhost:8081/evidencias
   - Clique em "Limpar Evidências" na seção de resultados
   - Confirme a ação no popup

🔧 CONFIGURAÇÕES:
   - Limpeza automática: Habilitada por padrão
   - Tipos de arquivo removidos: .png, .jpg, .jpeg, .gif
   - Diretórios limpos: prints_tests/sucessos e prints_tests/falhas

📁 ESTRUTURA:
   prints_tests/
   ├── sucessos/     # Limpo automaticamente
   └── falhas/       # Limpo automaticamente
""")

if __name__ == "__main__":
    print("🚀 TESTE DA LIMPEZA AUTOMÁTICA DE EVIDÊNCIAS")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Mostrar instruções
    mostrar_instrucoes()
    
    # Teste 1: Limpeza automática
    sucesso_limpeza = testar_limpeza_automatica()
    
    # Teste 2: API de limpeza (se servidor estiver rodando)
    sucesso_api = testar_limpeza_api()
    
    print("\n" + "=" * 60)
    if sucesso_limpeza:
        print("🎉 TESTE DE LIMPEZA AUTOMÁTICA CONCLUÍDO COM SUCESSO!")
        print("💡 A limpeza automática está funcionando corretamente.")
    else:
        print("💥 TESTE DE LIMPEZA AUTOMÁTICA FALHOU!")
        print("🔧 Verifique os erros acima e tente novamente.")
    
    if sucesso_api:
        print("🌐 API DE LIMPEZA FUNCIONANDO!")
    else:
        print("⚠️ API DE LIMPEZA NÃO TESTADA (servidor pode não estar rodando)")
    
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
