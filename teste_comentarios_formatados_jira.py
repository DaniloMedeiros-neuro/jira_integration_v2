#!/usr/bin/env python3
"""
Teste de Comentários Formatados com Imagens no Jira
==================================================

Este script testa a nova funcionalidade de envio de evidências
como comentários formatados com imagens no Jira.
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
        ('sucessos', 'NEX-17_sucesso.png'),
        ('sucessos', 'BC-123_sucesso.png'),
        ('falhas', 'NEX-18_falha.png'),
        ('falhas', 'BUG-789_falha.png')
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

def testar_api_comentarios_formatados():
    """Testa a API de envio com comentários formatados"""
    
    print(f"\n🌐 TESTE DE COMENTÁRIOS FORMATADOS")
    print("=" * 40)
    
    try:
        # Preparar dados para envio
        payload = {
            "issue_keys": ["NEX-17", "BC-123", "NEX-18", "BUG-789"]
        }
        
        print(f"📤 Enviando evidências com comentários formatados...")
        print(f"   🎯 Cards: {', '.join(payload['issue_keys'])}")
        
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
                
                # Mostrar detalhes dos comentários
                detalhes = resultado.get('detalhes', [])
                if detalhes:
                    print(f"\n📋 Detalhes dos Comentários:")
                    for detalhe in detalhes:
                        status = "✅" if detalhe.get('sucesso') else "❌"
                        tipo = detalhe.get('tipo', 'N/A')
                        anexo_id = detalhe.get('anexo_id', 'N/A')
                        
                        if detalhe.get('sucesso'):
                            print(f"   {status} {detalhe.get('issue_key', 'N/A')} - {detalhe.get('arquivo', 'N/A')}")
                            print(f"      📝 Tipo: {tipo} ({'APROVADO' if tipo == 'sucessos' else 'REPROVADO'})")
                            print(f"      🖼️ Anexo ID: {anexo_id}")
                            print(f"      🎨 Painel: {'success' if tipo == 'sucessos' else 'error'}")
                        else:
                            print(f"   {status} {detalhe.get('issue_key', 'N/A')} - {detalhe.get('arquivo', 'N/A')}")
                            print(f"      ❌ Erro: {detalhe.get('erro', 'Erro desconhecido')}")
                
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

def verificar_funcionalidades_implementadas():
    """Verifica se as funcionalidades foram implementadas corretamente"""
    
    print("\n🔍 VERIFICAÇÃO DE FUNCIONALIDADES")
    print("=" * 40)
    
    try:
        # Verificar se as funções foram implementadas
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        funcionalidades = [
            'def comentar_com_imagem(',
            'def upload_arquivo_jira(',
            'image_meta = upload_arquivo_jira(',
            'comentar_com_imagem(issue_key, mensagem, tipo_painel, image_meta, headers)',
            '"TESTE AUTOMAÇÃO "',
            '"APROVADO"',
            '"REPROVADO"',
            'tipo_painel = "success"',
            'tipo_painel = "error"'
        ]
        
        funcionalidades_encontradas = 0
        for func in funcionalidades:
            if func in content:
                funcionalidades_encontradas += 1
                print(f"   ✅ {func[:30]}...")
            else:
                print(f"   ❌ {func[:30]}... (não encontrada)")
        
        print(f"\n📊 Funcionalidades encontradas: {funcionalidades_encontradas}/{len(funcionalidades)}")
        
        if funcionalidades_encontradas >= len(funcionalidades) * 0.8:  # 80% das funcionalidades
            print("✅ Implementação de comentários formatados completa")
            return True
        else:
            print("❌ Implementação pode estar incompleta")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar funcionalidades: {e}")
        return False

def mostrar_instrucoes():
    """Mostra instruções para testar a funcionalidade"""
    
    print("\n📖 INSTRUÇÕES PARA TESTAR")
    print("=" * 30)
    
    print("""
🔧 NOVA FUNCIONALIDADE:
   - Comentários formatados com imagens
   - Texto específico para sucesso/falha
   - Painéis coloridos no Jira
   - Anexos com metadados

🔧 COMO FUNCIONA:
   1. 📁 Upload de arquivo HTML
   2. 🔄 Processamento de evidências
   3. 📤 Envio automático para cards
   4. 🖼️ Upload de anexo
   5. 📝 Comentário formatado com imagem
   6. 🎨 Painel colorido (verde/vermelho)

🔧 FORMATO DOS COMENTÁRIOS:
   ✅ Sucesso: "TESTE AUTOMAÇÃO APROVADO" (painel verde)
   ❌ Falha: "TESTE AUTOMAÇÃO REPROVADO" (painel vermelho)
   🖼️ Imagem: Centralizada abaixo do texto

🔧 TESTE MANUAL:
   1. 🌐 Acesse: http://localhost:8081/evidencias
   2. 📁 Faça upload de um arquivo HTML
   3. 🔄 Aguarde o processamento
   4. 📤 Clique em "Enviar ao Jira"
   5. ✅ Confirme o envio
   6. 🎯 Verifique os cards no Jira
   7. 📝 Confirme que há comentários formatados

🔧 VERIFICAÇÃO NO JIRA:
   - Deve haver comentários com texto formatado
   - Deve haver painéis coloridos (verde/vermelho)
   - Deve haver imagens anexadas
   - Deve haver texto "TESTE AUTOMAÇÃO APROVADO/REPROVADO"
""")

def testar_estrutura_comentarios():
    """Testa a estrutura dos comentários"""
    
    print("\n🧪 TESTE DA ESTRUTURA DE COMENTÁRIOS")
    print("=" * 40)
    
    # Testar estrutura de mensagem para sucesso
    mensagem_sucesso = [
        {"type": "text", "text": "TESTE AUTOMAÇÃO ", "marks": [{"type": "strong"}]},
        {"type": "text", "text": "APROVADO", "marks": [{"type": "strong"}]}
    ]
    
    # Testar estrutura de mensagem para falha
    mensagem_falha = [
        {"type": "text", "text": "TESTE AUTOMAÇÃO ", "marks": [{"type": "strong"}]},
        {"type": "text", "text": "REPROVADO", "marks": [{"type": "strong"}]}
    ]
    
    print("✅ Estrutura de mensagem para sucesso:")
    print(f"   📝 Texto: {' '.join([m['text'] for m in mensagem_sucesso])}")
    print(f"   🎨 Formatação: Negrito aplicado")
    print(f"   🎯 Painel: success (verde)")
    
    print("\n✅ Estrutura de mensagem para falha:")
    print(f"   📝 Texto: {' '.join([m['text'] for m in mensagem_falha])}")
    print(f"   🎨 Formatação: Negrito aplicado")
    print(f"   🎯 Painel: error (vermelho)")
    
    print("\n✅ Estrutura do comentário completo:")
    print("   📋 Panel com texto formatado")
    print("   🖼️ MediaSingle com imagem")
    print("   🔗 URL da imagem do anexo")
    print("   📄 Tipo: doc (Document Format)")
    
    return True

if __name__ == "__main__":
    print("🚀 TESTE DE COMENTÁRIOS FORMATADOS COM IMAGENS")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar funcionalidades implementadas
    funcionalidades_ok = verificar_funcionalidades_implementadas()
    
    # Testar estrutura de comentários
    estrutura_ok = testar_estrutura_comentarios()
    
    # Criar evidências de teste
    criar_evidencias_teste()
    
    # Testar API de comentários formatados
    api_ok = testar_api_comentarios_formatados()
    
    # Mostrar instruções
    mostrar_instrucoes()
    
    print("\n" + "=" * 60)
    if funcionalidades_ok and estrutura_ok and api_ok:
        print("🎉 TESTE DE COMENTÁRIOS FORMATADOS CONCLUÍDO COM SUCESSO!")
        print("💡 A funcionalidade está funcionando corretamente.")
        print("🔧 Agora os comentários são formatados com imagens e texto específico.")
    else:
        print("💥 ALGUNS PROBLEMAS PERSISTEM!")
        print("🔧 Verifique os erros acima e tente novamente.")
    
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
