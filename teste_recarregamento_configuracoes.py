#!/usr/bin/env python3
"""
Script para testar o recarregamento de configurações
"""

import requests
import json
import time
import os
from urllib.parse import urljoin

class TesteRecarregamento:
    def __init__(self):
        self.base_url = "http://localhost:8081"
        self.session = requests.Session()
        
    def testar_api_recarregar(self):
        """Testa a API de recarregamento"""
        try:
            url = urljoin(self.base_url, "/api/configuracoes/recarregar")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('sucesso'):
                    print("✅ API de recarregamento funcionando")
                    print(f"   📋 Configurações carregadas:")
                    for key, value in result['configuracoes'].items():
                        if key == 'JIRA_API_TOKEN':
                            # Mascarar token por segurança
                            masked_value = value[:10] + "..." if len(value) > 10 else value
                            print(f"      {key}: {masked_value}")
                        else:
                            print(f"      {key}: {value}")
                    return True
                else:
                    print(f"❌ API de recarregamento falhou: {result.get('erro')}")
                    return False
            else:
                print(f"❌ API de recarregamento retornou status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar API de recarregamento: {e}")
            return False
    
    def testar_modificacao_env(self):
        """Testa modificação do arquivo .env"""
        try:
            # Fazer backup do arquivo atual
            if os.path.exists('.env'):
                with open('.env', 'r', encoding='utf-8') as f:
                    conteudo_original = f.read()
                
                # Modificar o arquivo .env
                conteudo_modificado = conteudo_original.replace(
                    'https://neurotech.atlassian.net',
                    'https://teste.atlassian.net'
                )
                
                # Salvar modificação
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(conteudo_modificado)
                
                print("✅ Arquivo .env modificado temporariamente")
                
                # Aguardar um pouco
                time.sleep(1)
                
                # Testar se a API detecta a mudança
                url = urljoin(self.base_url, "/api/configuracoes/recarregar")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('sucesso'):
                        url_atual = result['configuracoes'].get('JIRA_BASE_URL', '')
                        if 'teste.atlassian.net' in url_atual:
                            print("✅ Mudança detectada pela API")
                        else:
                            print("❌ Mudança não foi detectada")
                            return False
                    else:
                        print(f"❌ Erro ao recarregar: {result.get('erro')}")
                        return False
                else:
                    print(f"❌ Erro na API: {response.status_code}")
                    return False
                
                # Restaurar arquivo original
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(conteudo_original)
                
                print("✅ Arquivo .env restaurado")
                
                # Verificar se foi restaurado corretamente
                time.sleep(1)
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('sucesso'):
                        url_atual = result['configuracoes'].get('JIRA_BASE_URL', '')
                        if 'neurotech.atlassian.net' in url_atual:
                            print("✅ Restauração confirmada")
                            return True
                        else:
                            print("❌ Restauração não funcionou")
                            return False
                    else:
                        print(f"❌ Erro ao verificar restauração: {result.get('erro')}")
                        return False
                else:
                    print(f"❌ Erro ao verificar restauração: {response.status_code}")
                    return False
                    
            else:
                print("❌ Arquivo .env não encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar modificação do .env: {e}")
            return False
    
    def testar_pagina_configuracoes(self):
        """Testa se a página carrega as configurações corretamente"""
        try:
            url = urljoin(self.base_url, "/configuracoes")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Verificar se os campos estão sendo preenchidos
                if "https://neurotech.atlassian.net" in content:
                    print("✅ Página carregando configurações corretamente")
                    return True
                else:
                    print("❌ Página não está carregando configurações")
                    return False
            else:
                print(f"❌ Página retornou status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar página: {e}")
            return False
    
    def executar_todos_testes(self):
        """Executa todos os testes"""
        print("🧪 INICIANDO TESTES DE RECARREGAMENTO DE CONFIGURAÇÕES")
        print("=" * 60)
        
        testes = [
            ("API de Recarregamento", self.testar_api_recarregar),
            ("Modificação do .env", self.testar_modificacao_env),
            ("Página de Configurações", self.testar_pagina_configuracoes)
        ]
        
        resultados = []
        
        for nome_teste, funcao_teste in testes:
            print(f"\n🔍 Testando: {nome_teste}")
            print("-" * 40)
            
            try:
                sucesso = funcao_teste()
                resultados.append((nome_teste, sucesso))
                
                if sucesso:
                    print(f"✅ {nome_teste}: PASSOU")
                else:
                    print(f"❌ {nome_teste}: FALHOU")
                    
            except Exception as e:
                print(f"❌ {nome_teste}: ERRO - {e}")
                resultados.append((nome_teste, False))
            
            time.sleep(1)  # Pausa entre testes
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        testes_passaram = sum(1 for _, sucesso in resultados if sucesso)
        total_testes = len(resultados)
        
        for nome_teste, sucesso in resultados:
            status = "✅ PASSOU" if sucesso else "❌ FALHOU"
            print(f"{status} - {nome_teste}")
        
        print(f"\n🎯 Resultado Final: {testes_passaram}/{total_testes} testes passaram")
        
        if testes_passaram == total_testes:
            print("🎉 TODOS OS TESTES PASSARAM! O recarregamento está funcionando perfeitamente.")
        else:
            print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        
        return testes_passaram == total_testes

def main():
    """Função principal"""
    print("🚀 TESTE DE RECARREGAMENTO DE CONFIGURAÇÕES")
    print("=" * 60)
    
    teste = TesteRecarregamento()
    sucesso = teste.executar_todos_testes()
    
    if sucesso:
        print("\n🎉 SUCESSO! O recarregamento de configurações está funcionando.")
        print("\n📖 COMO USAR:")
        print("1. Modifique o arquivo .env diretamente")
        print("2. Clique no botão 'Recarregar' na página de configurações")
        print("3. Ou aguarde o recarregamento automático (30 segundos)")
        print("4. As mudanças serão refletidas automaticamente na interface")
    else:
        print("\n❌ ALGUNS PROBLEMAS FORAM ENCONTRADOS.")
        print("Verifique os erros acima e corrija antes de continuar.")

if __name__ == "__main__":
    main()
