#!/usr/bin/env python3
"""
Teste do Método Híbrido de Captura de Evidências
================================================

Este script demonstra como usar o novo método híbrido que combina
a precisão do método do usuário com a flexibilidade do método atual.
"""

import os
import sys
import time
from datetime import datetime

def testar_metodo_hibrido():
    """Testa o método híbrido de processamento de evidências"""
    
    print("🧪 TESTE DO MÉTODO HÍBRIDO DE EVIDÊNCIAS")
    print("=" * 50)
    
    # Verificar se o arquivo log.html existe
    log_path = os.path.join(os.getcwd(), 'log.html')
    if not os.path.exists(log_path):
        print("❌ Arquivo log.html não encontrado!")
        print("📝 Por favor, faça upload de um arquivo HTML de log primeiro.")
        return False
    
    print(f"📁 Arquivo encontrado: {log_path}")
    print(f"📊 Tamanho: {os.path.getsize(log_path)} bytes")
    
    # Importar a função do app.py
    try:
        # Adicionar o diretório atual ao path para importar app
        sys.path.insert(0, os.getcwd())
        from app import processar_evidencias_hibrido
        
        print("\n🔄 Iniciando processamento híbrido...")
        start_time = time.time()
        
        # Executar o método híbrido
        resultado = processar_evidencias_hibrido(log_path)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if resultado and resultado.get('sucesso'):
            print("✅ Processamento concluído com sucesso!")
            print(f"⏱️  Tempo de processamento: {processing_time:.2f} segundos")
            print(f"🔧 Método utilizado: {resultado.get('metodo', 'desconhecido')}")
            
            # Mostrar estatísticas
            estatisticas = resultado.get('estatisticas', {})
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"   ✅ Sucessos: {estatisticas.get('sucessos', 0)}")
            print(f"   ❌ Falhas: {estatisticas.get('falhas', 0)}")
            print(f"   📋 Total: {estatisticas.get('total', 0)}")
            print(f"   🔍 Elementos processados: {estatisticas.get('elementos_processados', 0)}")
            
            # Mostrar evidências geradas
            nomes_evidencias = resultado.get('nomes_evidencias', [])
            if nomes_evidencias:
                print(f"\n📸 EVIDÊNCIAS GERADAS ({len(nomes_evidencias)}):")
                for i, evidencia in enumerate(nomes_evidencias[:10], 1):  # Mostrar apenas as primeiras 10
                    status_emoji = "✅" if evidencia['status'] == 'sucesso' else "❌"
                    print(f"   {i:2d}. {status_emoji} {evidencia['nome']} -> {evidencia['arquivo']}")
                
                if len(nomes_evidencias) > 10:
                    print(f"   ... e mais {len(nomes_evidencias) - 10} evidências")
            
            # Verificar arquivos gerados
            print(f"\n📁 VERIFICAÇÃO DE ARQUIVOS:")
            sucessos_dir = "prints_tests/sucessos"
            falhas_dir = "prints_tests/falhas"
            
            if os.path.exists(sucessos_dir):
                sucessos_files = len([f for f in os.listdir(sucessos_dir) if f.endswith('.png')])
                print(f"   📂 {sucessos_dir}: {sucessos_files} arquivos")
            
            if os.path.exists(falhas_dir):
                falhas_files = len([f for f in os.listdir(falhas_dir) if f.endswith('.png')])
                print(f"   📂 {falhas_dir}: {falhas_files} arquivos")
            
            return True
            
        else:
            print("❌ Erro no processamento!")
            if resultado:
                print(f"   Erro: {resultado.get('erro', 'Erro desconhecido')}")
            return False
            
    except ImportError as e:
        print(f"❌ Erro ao importar função: {e}")
        print("💡 Certifique-se de que o app.py está no diretório atual")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def comparar_metodos():
    """Compara os diferentes métodos de processamento"""
    
    print("\n🔍 COMPARAÇÃO DE MÉTODOS")
    print("=" * 30)
    
    print("""
📋 MÉTODO HÍBRIDO (NOVO):
   ✅ Tenta primeiro seletores específicos (Selenium)
   ✅ Fallback para método genérico (BeautifulSoup)
   ✅ Expande elementos de sucesso
   ✅ Captura screenshots reais quando possível
   ✅ Detecção precisa de status
   ✅ Extração confiável de nomes

📋 MÉTODO ATUAL:
   ✅ Flexível para diferentes formatos
   ✅ Múltiplas estratégias de detecção
   ✅ Configurável (screenshot real ou simulado)
   ✅ Mais rápido (parsing HTML)
   ❌ Menos preciso na detecção
   ❌ Screenshots simulados por padrão
   ❌ Não expande elementos

📋 MÉTODO DO USUÁRIO:
   ✅ Conhece exatamente a estrutura do HTML
   ✅ Captura screenshots reais dos elementos
   ✅ Expande elementos para capturar mais detalhes
   ✅ Detecção precisa de status
   ❌ Dependente de estrutura específica
   ❌ Mais lento (usa Selenium)
   ❌ Menos flexível para diferentes formatos
""")

def mostrar_instrucoes():
    """Mostra instruções de uso"""
    
    print("\n📖 INSTRUÇÕES DE USO")
    print("=" * 25)
    
    print("""
1. 📁 Certifique-se de ter um arquivo log.html no diretório atual
2. 🐍 Execute este script: python teste_metodo_hibrido.py
3. 🔄 O método híbrido será executado automaticamente
4. 📸 Screenshots serão gerados em prints_tests/
5. 📊 Estatísticas serão exibidas no console

🔧 CONFIGURAÇÕES:
   - Para habilitar screenshots reais: export CAPTURE_REAL_SCREENSHOTS=true
   - Para modo debug: export DEBUG_MODE=true
   - Para logs detalhados: export LOG_LEVEL=DEBUG

📁 ESTRUTURA GERADA:
   prints_tests/
   ├── sucessos/
   │   ├── TLD-123_sucesso.png
   │   └── PROJ-456_sucesso.png
   └── falhas/
       ├── TEST-789_falha.png
       └── BUG-101_falha.png
""")

if __name__ == "__main__":
    print("🚀 TESTE DO MÉTODO HÍBRIDO DE CAPTURA DE EVIDÊNCIAS")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Mostrar instruções
    mostrar_instrucoes()
    
    # Mostrar comparação
    comparar_metodos()
    
    # Executar teste
    print("\n" + "=" * 60)
    sucesso = testar_metodo_hibrido()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("💡 O método híbrido está funcionando corretamente.")
    else:
        print("💥 TESTE FALHOU!")
        print("🔧 Verifique os erros acima e tente novamente.")
    
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
