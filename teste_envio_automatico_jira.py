#!/usr/bin/env python3
"""
Teste do Envio Automático de Evidências para Jira
================================================

Este script testa a nova funcionalidade de envio automático
de evidências para múltiplos cards do Jira baseado nos nomes dos arquivos.
"""

import os
import requests
import json
from datetime import datetime

def criar_evidencias_teste():
    """Cria evidências de teste com nomes de cards do Jira"""
    
    print("🧪 CRIANDO EVIDÊNCIAS DE TESTE")
    print("=" * 40)
    
    # Criar diretórios
    os.makedirs('prints_tests/sucessos', exist_ok=True)
    os.makedirs('prints_tests/falhas', exist_ok=True)
    
    # Criar arquivos de teste com nomes de cards do Jira
    evidencias_teste = [
        ('sucessos', 'NEX-18_sucesso.png'),
        ('sucessos', 'BC-123_sucesso.png'),
        ('sucessos', 'PROJ-456_sucesso.png'),
        ('falhas', 'NEX-19_falha.png'),
        ('falhas', 'BUG-789_falha.png'),
        ('sucessos', 'FEATURE-202_sucesso.png')
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

def extrair_ids_cards():
    """Extrai IDs únicos dos cards a partir dos nomes dos arquivos"""
    
    print("\n🔍 EXTRAINDO IDs DOS CARDS")
    print("=" * 30)
    
    card_ids = set()
    
    # Verificar diretórios
    for diretorio in ['sucessos', 'falhas']:
        caminho = os.path.join('prints_tests', diretorio)
        if os.path.exists(caminho):
            for arquivo in os.listdir(caminho):
                if arquivo.endswith('.png'):
                    # Extrair ID do card do nome do arquivo (ex: NEX-18_sucesso.png -> NEX-18)
                    import re
                    match = re.match(r'^([A-Z]+-\d+)', arquivo)
                    if match:
                        card_id = match.group(1)
                        card_ids.add(card_id)
                        print(f"   🎯 ID encontrado: {card_id} (arquivo: {arquivo})")
    
    print(f"\n📊 Total de IDs únicos encontrados: {len(card_ids)}")
    print(f"📋 IDs: {', '.join(sorted(card_ids))}")
    
    return list(card_ids)

def testar_api_envio(card_ids):
    """Testa a API de envio com múltiplos IDs"""
    
    print(f"\n🌐 TESTE DA API DE ENVIO")
    print("=" * 30)
    
    try:
        # Preparar dados para envio
        payload = {
            "issue_keys": card_ids
        }
        
        print(f"📤 Enviando para {len(card_ids)} card(s): {', '.join(card_ids)}")
        
        # Chamar API de envio
        response = requests.post(
            'http://localhost:8081/api/evidencias/enviar',
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        
        if response.status_code == 200:
            resultado = response.json()
            
            if resultado.get('sucesso'):
                print("✅ API de envio funcionando!")
                print(f"   📊 Enviados: {resultado.get('enviados', 0)}")
                print(f"   📊 Total processados: {resultado.get('total_processados', 0)}")
                print(f"   📋 Issues processadas: {resultado.get('issues_processadas', [])}")
                print(f"   💬 Mensagem: {resultado.get('mensagem', '')}")
                
                # Mostrar detalhes
                detalhes = resultado.get('detalhes', [])
                if detalhes:
                    print(f"\n📋 Detalhes do envio:")
                    for detalhe in detalhes:
                        status = "✅" if detalhe.get('sucesso') else "❌"
                        print(f"   {status} {detalhe.get('issue_key', 'N/A')} - {detalhe.get('arquivo', 'N/A')} ({detalhe.get('tipo', 'N/A')})")
                
                return True
            else:
                print(f"❌ Erro na API: {resultado.get('erro', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            try:
                erro = response.json()
                print(f"   Detalhes: {erro}")
            except:
                print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste da API: {e}")
        return False

def testar_interface_web():
    """Testa se a interface web está funcionando corretamente"""
    
    print("\n🌐 TESTE DA INTERFACE WEB")
    print("=" * 30)
    
    try:
        # Testar página de evidências
        response = requests.get("http://localhost:8081/evidencias")
        if response.status_code == 200:
            print("✅ Página de evidências acessível")
            
            # Verificar se contém elementos necessários
            html_content = response.text
            
            elementos_necessarios = [
                'btnEnviarEvidencias',
                'enviarEvidenciasJira',
                'resultadosSection'
            ]
            
            for elemento in elementos_necessarios:
                if elemento in html_content:
                    print(f"   ✅ Elemento '{elemento}' encontrado")
                else:
                    print(f"   ❌ Elemento '{elemento}' não encontrado")
                    return False
            
            return True
        else:
            print(f"❌ Página não acessível: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar interface: {e}")
        return False

def mostrar_instrucoes():
    """Mostra instruções para testar a funcionalidade"""
    
    print("\n📖 INSTRUÇÕES PARA TESTAR")
    print("=" * 30)
    
    print("""
🔧 NOVA FUNCIONALIDADE:
   - Envio automático baseado nos nomes dos arquivos
   - Extração automática de IDs dos cards do Jira
   - Envio para múltiplos cards simultaneamente
   - Confirmação antes do envio

🔧 COMO FUNCIONA:
   1. 📁 Upload de arquivo HTML
   2. 🔄 Processamento de evidências
   3. 📋 Extração automática de IDs dos cards
   4. ✅ Confirmação com lista de cards
   5. 📤 Envio automático para todos os cards

🔧 EXEMPLO:
   Arquivo: NEX-18_sucesso.png
   ID extraído: NEX-18
   Envio automático para o card NEX-18

🔧 TESTE MANUAL:
   1. 🌐 Acesse: http://localhost:8081/evidencias
   2. 📁 Faça upload de um arquivo HTML
   3. 🔄 Aguarde o processamento
   4. 📤 Clique em "Enviar ao Jira"
   5. ✅ Confirme o envio na janela de confirmação
   6. 🎯 Verifique se os cards receberam as evidências

🔧 VERIFICAÇÃO:
   - Não deve aparecer prompt para digitar ID
   - Deve mostrar lista de cards encontrados
   - Deve enviar automaticamente para todos os cards
   - Deve mostrar confirmação de sucesso
""")

def verificar_arquivos_evidencias():
    """Verifica se há arquivos de evidência para teste"""
    
    print("\n📁 VERIFICAÇÃO DE ARQUIVOS")
    print("=" * 30)
    
    total_arquivos = 0
    card_ids = set()
    
    for diretorio in ['sucessos', 'falhas']:
        caminho = os.path.join('prints_tests', diretorio)
        if os.path.exists(caminho):
            arquivos = [f for f in os.listdir(caminho) if f.endswith('.png')]
            total_arquivos += len(arquivos)
            
            print(f"📂 {diretorio}: {len(arquivos)} arquivo(s)")
            
            for arquivo in arquivos:
                import re
                match = re.match(r'^([A-Z]+-\d+)', arquivo)
                if match:
                    card_ids.add(match.group(1))
    
    print(f"\n📊 Total de arquivos: {total_arquivos}")
    print(f"🎯 IDs de cards encontrados: {len(card_ids)}")
    
    if card_ids:
        print(f"📋 Cards: {', '.join(sorted(card_ids))}")
    
    return total_arquivos > 0

if __name__ == "__main__":
    print("🚀 TESTE DO ENVIO AUTOMÁTICO DE EVIDÊNCIAS")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Criar evidências de teste
    criar_evidencias_teste()
    
    # Verificar arquivos existentes
    arquivos_ok = verificar_arquivos_evidencias()
    
    if not arquivos_ok:
        print("❌ Nenhum arquivo de evidência encontrado")
        exit(1)
    
    # Extrair IDs dos cards
    card_ids = extrair_ids_cards()
    
    if not card_ids:
        print("❌ Nenhum ID de card válido encontrado")
        exit(1)
    
    # Testar interface web
    interface_ok = testar_interface_web()
    
    # Testar API de envio
    api_ok = testar_api_envio(card_ids)
    
    # Mostrar instruções
    mostrar_instrucoes()
    
    print("\n" + "=" * 60)
    if arquivos_ok and interface_ok and api_ok:
        print("🎉 TESTE DO ENVIO AUTOMÁTICO CONCLUÍDO COM SUCESSO!")
        print("💡 A funcionalidade está funcionando corretamente.")
        print("🔧 Agora você pode enviar evidências automaticamente para múltiplos cards.")
    else:
        print("💥 ALGUNS PROBLEMAS PERSISTEM!")
        print("🔧 Verifique os erros acima e tente novamente.")
    
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
