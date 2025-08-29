#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Teste Automatizado - Fase 6: Finalização SB Admin 2
Testa todas as funcionalidades da aplicação para garantir que está pronta para produção.
"""

import requests
import time
import json
from bs4 import BeautifulSoup
import os

class TesteFinalizacao:
    def __init__(self, base_url="http://localhost:8081"):
        self.base_url = base_url
        self.session = requests.Session()
        self.resultados = {
            "sucessos": 0,
            "falhas": 0,
            "detalhes": []
        }
    
    def log_teste(self, nome, sucesso, detalhes=""):
        """Registra resultado de um teste"""
        status = "✅ SUCESSO" if sucesso else "❌ FALHA"
        print(f"{status} - {nome}")
        if detalhes:
            print(f"   📝 {detalhes}")
        
        self.resultados["sucessos" if sucesso else "falhas"] += 1
        self.resultados["detalhes"].append({
            "nome": nome,
            "sucesso": sucesso,
            "detalhes": detalhes
        })
    
    def testar_conectividade(self):
        """Testa se o servidor está respondendo"""
        try:
            response = self.session.get(self.base_url, timeout=5)
            sucesso = response.status_code == 200
            self.log_teste("Conectividade do Servidor", sucesso, 
                          f"Status: {response.status_code}")
            return sucesso
        except Exception as e:
            self.log_teste("Conectividade do Servidor", False, str(e))
            return False
    
    def testar_pagina_principal(self):
        """Testa a página principal (index.html)"""
        try:
            response = self.session.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Verificar elementos essenciais
            titulo = soup.find('title')
            sidebar = soup.find('ul', class_='navbar-nav')
            topbar = soup.find('nav', class_='navbar')
            search_input = soup.find('input', {'id': 'requisitoPai'})
            
            sucesso = all([titulo, sidebar, topbar, search_input])
            self.log_teste("Página Principal", sucesso, 
                          f"Título: {titulo.text if titulo else 'N/A'}")
            return sucesso
        except Exception as e:
            self.log_teste("Página Principal", False, str(e))
            return False
    
    def testar_assets_css(self):
        """Testa se os arquivos CSS estão carregando"""
        assets_css = [
            "/static/css/sb-admin-2.min.css",
            "/static/css/sb-admin-2-custom.css",
            "/static/css/style.css"
        ]
        
        sucessos = 0
        for asset in assets_css:
            try:
                response = self.session.get(f"{self.base_url}{asset}")
                if response.status_code == 200:
                    sucessos += 1
                else:
                    print(f"   ⚠️  Asset não encontrado: {asset}")
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar {asset}: {e}")
        
        sucesso = sucessos == len(assets_css)
        self.log_teste("Assets CSS", sucesso, 
                      f"{sucessos}/{len(assets_css)} carregados")
        return sucesso
    
    def testar_assets_js(self):
        """Testa se os arquivos JavaScript estão carregando"""
        assets_js = [
            "/static/js/sb-admin-2.min.js",
            "/static/js/sb-admin-2-custom.js",
            "/static/js/app.js"
        ]
        
        sucessos = 0
        for asset in assets_js:
            try:
                response = self.session.get(f"{self.base_url}{asset}")
                if response.status_code == 200:
                    sucessos += 1
                else:
                    print(f"   ⚠️  Asset não encontrado: {asset}")
            except Exception as e:
                print(f"   ⚠️  Erro ao carregar {asset}: {e}")
        
        sucesso = sucessos == len(assets_js)
        self.log_teste("Assets JavaScript", sucesso, 
                      f"{sucessos}/{len(assets_js)} carregados")
        return sucesso
    
    def testar_paginas_principais(self):
        """Testa todas as páginas principais"""
        paginas = [
            ("/", "Dashboard"),
            ("/evidencias", "Evidências"),
            ("/metricas", "Métricas"),
            ("/configuracoes", "Configurações"),
            ("/planilha-manual", "Planilha Manual")
        ]
        
        sucessos = 0
        for url, nome in paginas:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    sucessos += 1
                    print(f"   ✅ {nome}: OK")
                else:
                    print(f"   ❌ {nome}: Status {response.status_code}")
            except Exception as e:
                print(f"   ❌ {nome}: {e}")
        
        sucesso = sucessos == len(paginas)
        self.log_teste("Páginas Principais", sucesso, 
                      f"{sucessos}/{len(paginas)} acessíveis")
        return sucesso
    
    def testar_api_busca(self):
        """Testa a API de busca de casos de teste"""
        try:
            # Teste com um requisito válido (BC-8)
            payload = {"requisito": "BC-8"}
            response = self.session.post(f"{self.base_url}/buscar", 
                                       json=payload, timeout=10)
            
            sucesso = response.status_code in [200, 404]  # 404 é aceitável se não encontrar
            self.log_teste("API de Busca", sucesso, 
                          f"Status: {response.status_code}")
            return sucesso
        except Exception as e:
            self.log_teste("API de Busca", False, str(e))
            return False
    
    def testar_responsividade_css(self):
        """Verifica se há CSS responsivo"""
        try:
            response = self.session.get(f"{self.base_url}/static/css/sb-admin-2.min.css")
            css_content = response.text
            
            # Verificar media queries responsivas
            media_queries = [
                "@media (max-width:",
                "@media (min-width:",
                "col-lg-",
                "col-md-",
                "col-sm-"
            ]
            
            encontrados = sum(1 for query in media_queries if query in css_content)
            sucesso = encontrados >= 3  # Pelo menos 3 indicadores de responsividade
            
            self.log_teste("CSS Responsivo", sucesso, 
                          f"{encontrados} indicadores encontrados")
            return sucesso
        except Exception as e:
            self.log_teste("CSS Responsivo", False, str(e))
            return False
    
    def testar_tempo_carregamento(self):
        """Testa o tempo de carregamento da página principal"""
        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=10)
            end_time = time.time()
            
            tempo_carregamento = end_time - start_time
            sucesso = tempo_carregamento < 3.0  # Menos de 3 segundos
            
            self.log_teste("Tempo de Carregamento", sucesso, 
                          f"{tempo_carregamento:.2f}s")
            return sucesso
        except Exception as e:
            self.log_teste("Tempo de Carregamento", False, str(e))
            return False
    
    def executar_todos_testes(self):
        """Executa todos os testes"""
        print("🧪 INICIANDO TESTES DA FASE 6 - FINALIZAÇÃO")
        print("=" * 60)
        
        testes = [
            self.testar_conectividade,
            self.testar_pagina_principal,
            self.testar_assets_css,
            self.testar_assets_js,
            self.testar_paginas_principais,
            self.testar_api_busca,
            self.testar_responsividade_css,
            self.testar_tempo_carregamento
        ]
        
        for teste in testes:
            try:
                teste()
                time.sleep(0.5)  # Pequena pausa entre testes
            except Exception as e:
                print(f"❌ ERRO NO TESTE: {e}")
        
        self.mostrar_resultados()
    
    def mostrar_resultados(self):
        """Mostra resumo dos resultados"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DOS TESTES")
        print("=" * 60)
        
        total = self.resultados["sucessos"] + self.resultados["falhas"]
        percentual = (self.resultados["sucessos"] / total * 100) if total > 0 else 0
        
        print(f"✅ Sucessos: {self.resultados['sucessos']}")
        print(f"❌ Falhas: {self.resultados['falhas']}")
        print(f"📈 Percentual de Sucesso: {percentual:.1f}%")
        
        if self.resultados["falhas"] > 0:
            print("\n🔍 DETALHES DAS FALHAS:")
            for detalhe in self.resultados["detalhes"]:
                if not detalhe["sucesso"]:
                    print(f"   ❌ {detalhe['nome']}: {detalhe['detalhes']}")
        
        print("\n🎯 RECOMENDAÇÕES:")
        if percentual >= 90:
            print("   🎉 Excelente! A aplicação está pronta para produção.")
        elif percentual >= 75:
            print("   ⚠️  Bom, mas alguns ajustes são necessários.")
        else:
            print("   🚨 Problemas significativos encontrados. Revisão necessária.")
        
        print("\n" + "=" * 60)

def main():
    """Função principal"""
    print("🚀 Teste de Finalização - SB Admin 2")
    print("Verificando se a aplicação está pronta para produção...")
    
    tester = TesteFinalizacao()
    tester.executar_todos_testes()

if __name__ == "__main__":
    main()
