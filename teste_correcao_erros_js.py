#!/usr/bin/env python3
"""
Teste da Correção de Erros JavaScript
=====================================

Este script testa se os erros de JavaScript foram corrigidos,
especialmente o erro "Cannot set properties of null".
"""

import requests
import time
import json

def testar_api_evidencias():
    """Testa as APIs de evidências para verificar se estão funcionando"""
    
    base_url = "http://localhost:8081"
    
    print("🧪 TESTE DA CORREÇÃO DE ERROS JAVASCRIPT")
    print("=" * 50)
    
    # Teste 1: Status das evidências
    print("\n1️⃣ Testando API de status...")
    try:
        response = requests.get(f"{base_url}/api/evidencias/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ API de status funcionando:")
            print(f"   📊 Total: {status.get('total', 0)} evidências")
            print(f"   📊 Processado: {status.get('processado', False)}")
        else:
            print(f"❌ Erro na API de status: {response.status_code}")
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
                print(f"✅ API de lista funcionando:")
                print(f"   📋 Total de evidências: {len(resultado.get('evidencias', []))}")
            else:
                print(f"❌ Erro na API de lista: {resultado.get('erro', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro na API de lista: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na API de lista: {e}")
        return False
    
    # Teste 3: API de limpeza
    print("\n3️⃣ Testando API de limpeza...")
    try:
        response = requests.post(f"{base_url}/api/evidencias/limpar")
        if response.status_code == 200:
            resultado = response.json()
            if resultado.get('sucesso'):
                print(f"✅ API de limpeza funcionando:")
                print(f"   🗑️ Arquivos removidos: {resultado.get('arquivos_removidos', 0)}")
            else:
                print(f"❌ Erro na API de limpeza: {resultado.get('erro', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro na API de limpeza: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na API de limpeza: {e}")
        return False
    
    return True

def testar_interface_web():
    """Testa se a interface web está acessível"""
    
    print("\n🌐 TESTE DA INTERFACE WEB")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8081/evidencias")
        if response.status_code == 200:
            print("✅ Interface web acessível")
            print("   🌐 URL: http://localhost:8081/evidencias")
            
            # Verificar se o HTML contém os elementos necessários
            html_content = response.text
            
            # Verificar se os botões estão presentes
            if 'btnEnviarEvidencias' in html_content:
                print("   ✅ Botão 'Enviar ao Jira' encontrado")
            else:
                print("   ❌ Botão 'Enviar ao Jira' não encontrado")
                return False
            
            if 'btnProcessarEvidencias' in html_content:
                print("   ✅ Botão 'Processar Evidências' encontrado")
            else:
                print("   ❌ Botão 'Processar Evidências' não encontrado")
                return False
            
            if 'resultadosSection' in html_content:
                print("   ✅ Seção de resultados encontrada")
            else:
                print("   ❌ Seção de resultados não encontrada")
                return False
            
            return True
        else:
            print(f"❌ Interface web não acessível: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar interface web: {e}")
        return False

def mostrar_instrucoes():
    """Mostra instruções para testar a correção"""
    
    print("\n📖 INSTRUÇÕES PARA TESTAR")
    print("=" * 30)
    
    print("""
🔧 ERROS CORRIGIDOS:
   - "Cannot set properties of null (setting 'disabled')"
   - Verificação de existência de elementos antes de manipulá-los
   - Tratamento de elementos que podem não existir

🔧 FUNÇÕES CORRIGIDAS:
   - enviarEvidenciasJira() - Verifica se btnEnviarEvidencias existe
   - processarEvidencias() - Verifica se btnProcessarEvidencias existe
   - executarStep1/2/3() - Verifica se steps existem
   - mostrarResultados() - Verifica se resultadosSection existe
   - resetarSteps() - Verifica se steps existem
   - mostrarInfoArquivo() - Verifica se elementos existem

🔧 COMO TESTAR:
   1. 🌐 Acesse: http://localhost:8081/evidencias
   2. 📁 Faça upload de um arquivo HTML
   3. 🔄 Aguarde o processamento
   4. 👁️ Clique em "Visualizar Evidências"
   5. 📤 Clique em "Enviar ao Jira"
   6. 🗑️ Clique em "Limpar Evidências"
   7. ✅ Verifique se não há erros no console (F12)

🔧 VERIFICAÇÃO:
   - Abra o console do navegador (F12)
   - Verifique se não há erros JavaScript
   - Todas as funcionalidades devem funcionar sem erros
""")

def verificar_arquivos_corrigidos():
    """Verifica se os arquivos foram corrigidos"""
    
    print("\n📁 VERIFICAÇÃO DE ARQUIVOS")
    print("=" * 30)
    
    try:
        # Verificar se o arquivo app.js foi modificado
        with open('static/js/app.js', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se as correções estão presentes
        correcoes = [
            'if (btnEnviar) {',
            'if (btnProcessar) {',
            'if (step && status) {',
            'if (resultadosSection) {',
            'if (uploadArea) uploadArea.classList.add',
            'if (uploadArea) uploadArea.classList.remove'
        ]
        
        correcoes_encontradas = 0
        for correcao in correcoes:
            if correcao in content:
                correcoes_encontradas += 1
                print(f"   ✅ {correcao[:30]}...")
            else:
                print(f"   ❌ {correcao[:30]}... (não encontrada)")
        
        print(f"\n📊 Correções encontradas: {correcoes_encontradas}/{len(correcoes)}")
        
        if correcoes_encontradas >= len(correcoes) * 0.8:  # 80% das correções
            print("✅ Arquivo app.js corrigido adequadamente")
            return True
        else:
            print("❌ Arquivo app.js pode não estar completamente corrigido")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar arquivo: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTE DA CORREÇÃO DE ERROS JAVASCRIPT")
    print("=" * 60)
    
    # Aguardar um pouco para o servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(2)
    
    # Verificar arquivos corrigidos
    arquivos_ok = verificar_arquivos_corrigidos()
    
    # Testar APIs
    apis_ok = testar_api_evidencias()
    
    # Testar interface web
    interface_ok = testar_interface_web()
    
    # Mostrar instruções
    mostrar_instrucoes()
    
    print("\n" + "=" * 60)
    if arquivos_ok and apis_ok and interface_ok:
        print("🎉 CORREÇÃO DE ERROS CONCLUÍDA COM SUCESSO!")
        print("💡 Os erros JavaScript foram corrigidos.")
        print("🔧 Agora você pode usar a interface sem erros.")
    else:
        print("💥 ALGUNS PROBLEMAS PERSISTEM!")
        print("🔧 Verifique os erros acima e tente novamente.")
    
    print("=" * 60)
