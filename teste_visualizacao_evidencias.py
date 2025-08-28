#!/usr/bin/env python3
"""
Teste da Visualização de Evidências
===================================

Este script testa se a funcionalidade de visualização de evidências
está funcionando corretamente após as correções.
"""

import requests
import json
import time

def testar_api_evidencias():
    """Testa as APIs de evidências"""
    
    base_url = "http://localhost:8081"
    
    print("🧪 TESTE DA VISUALIZAÇÃO DE EVIDÊNCIAS")
    print("=" * 50)
    
    # Teste 1: Status das evidências
    print("\n1️⃣ Testando API de status...")
    try:
        response = requests.get(f"{base_url}/api/evidencias/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status obtido com sucesso:")
            print(f"   📊 Sucessos: {status.get('sucessos', 0)}")
            print(f"   📊 Falhas: {status.get('falhas', 0)}")
            print(f"   📊 Total: {status.get('total', 0)}")
            print(f"   📊 Processado: {status.get('processado', False)}")
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na API de status: {e}")
        return False
    
    # Teste 2: Lista de evidências
    print("\n2️⃣ Testando API de lista...")
    try:
        response = requests.get(f"{base_url}/api/evidencias/lista")
        if response.status_code == 200:
            resultado = response.json()
            if resultado.get('sucesso'):
                evidencias = resultado.get('evidencias', [])
                print(f"✅ Lista obtida com sucesso:")
                print(f"   📋 Total de evidências: {len(evidencias)}")
                
                if evidencias:
                    print(f"   📸 Primeiras 5 evidências:")
                    for i, ev in enumerate(evidencias[:5], 1):
                        status_emoji = "✅" if ev['status'] == 'sucesso' else "❌"
                        print(f"      {i}. {status_emoji} {ev['nome']} -> {ev['arquivo']}")
                    
                    if len(evidencias) > 5:
                        print(f"      ... e mais {len(evidencias) - 5} evidências")
                else:
                    print("   ⚠️ Nenhuma evidência encontrada")
            else:
                print(f"❌ Erro na lista: {resultado.get('erro', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro ao obter lista: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na API de lista: {e}")
        return False
    
    # Teste 3: Verificar se há evidências para visualizar
    print("\n3️⃣ Verificando se há evidências para visualizar...")
    try:
        response = requests.get(f"{base_url}/api/evidencias/status")
        status = response.json()
        
        if status.get('processado') and status.get('total', 0) > 0:
            print("✅ Há evidências processadas para visualizar!")
            print("   💡 Agora você pode clicar em 'Visualizar Evidências' na interface web")
            return True
        else:
            print("⚠️ Nenhuma evidência processada encontrada")
            print("   💡 Faça upload de um arquivo HTML primeiro")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def testar_interface_web():
    """Testa se a interface web está acessível"""
    
    print("\n🌐 TESTE DA INTERFACE WEB")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8081/evidencias")
        if response.status_code == 200:
            print("✅ Interface web acessível")
            print("   🌐 URL: http://localhost:8081/evidencias")
            return True
        else:
            print(f"❌ Interface web não acessível: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar interface web: {e}")
        return False

def mostrar_instrucoes():
    """Mostra instruções para testar a visualização"""
    
    print("\n📖 INSTRUÇÕES PARA TESTAR")
    print("=" * 30)
    
    print("""
1. 🌐 Acesse: http://localhost:8081/evidencias
2. 📁 Faça upload de um arquivo HTML de log
3. 🔄 Aguarde o processamento
4. 👁️ Clique em 'Visualizar Evidências'
5. ✅ Verifique se o modal aparece com as evidências

🔧 Se ainda houver problemas:
   - Verifique o console do navegador (F12)
   - Verifique os logs do servidor
   - Execute este script novamente
""")

if __name__ == "__main__":
    print("🚀 TESTE DA VISUALIZAÇÃO DE EVIDÊNCIAS")
    print("=" * 60)
    
    # Aguardar um pouco para o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(2)
    
    # Testar APIs
    sucesso_apis = testar_api_evidencias()
    
    # Testar interface web
    sucesso_interface = testar_interface_web()
    
    # Mostrar instruções
    mostrar_instrucoes()
    
    print("\n" + "=" * 60)
    if sucesso_apis and sucesso_interface:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("💡 A visualização de evidências deve estar funcionando.")
    else:
        print("💥 TESTE FALHOU!")
        print("🔧 Verifique os erros acima e tente novamente.")
    
    print("=" * 60)
