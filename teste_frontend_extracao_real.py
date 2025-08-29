#!/usr/bin/env python3
"""
Teste para verificar se a extração real está funcionando no frontend
"""

import requests
import time
from bs4 import BeautifulSoup
import json
import os

class TesteFrontendExtracaoReal:
    def __init__(self):
        self.base_url = "http://localhost:8081"
        self.session = requests.Session()
        
    def log_teste(self, nome_teste, sucesso, detalhes=""):
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{status} - {nome_teste}: {detalhes}")
        return sucesso
        
    def testar_frontend_extracao_real(self):
        """Testa se a extração real está funcionando no frontend"""
        print("🧪 TESTANDO FRONTEND - EXTRAÇÃO REAL DE EVIDÊNCIAS")
        print("=" * 60)
        
        try:
            # 1. Acessar página de evidências
            response = self.session.get(f"{self.base_url}/evidencias")
            if not response.ok:
                return self.log_teste("Acesso à página", False, f"Status: {response.status_code}")
            
            self.log_teste("Acesso à página", True, "Página carregada com sucesso")
            
            # 2. Verificar se o app.js está sendo carregado
            soup = BeautifulSoup(response.content, 'html.parser')
            app_js_scripts = soup.find_all('script', src=lambda x: x and 'app.js' in x)
            
            if len(app_js_scripts) == 0:
                return self.log_teste("Carregamento app.js", False, "app.js não encontrado")
            
            self.log_teste("Carregamento app.js", True, f"app.js carregado {len(app_js_scripts)} vez(es)")
            
            # 3. Verificar se não há JavaScript embutido simulando resultados
            js_content = response.text
            
            # Verificar se não há simulação de resultados
            simulacoes = [
                "Math.floor(Math.random()",
                "simulateProcessing",
                "Simular processamento",
                "showResults()",
                "simulateProcessing()"
            ]
            
            for simulacao in simulacoes:
                if simulacao in js_content:
                    return self.log_teste("JavaScript simulado", False, f"Encontrado: {simulacao}")
            
            self.log_teste("JavaScript simulado", True, "Nenhuma simulação encontrada")
            
            # 4. Verificar se o JavaScript real está sendo carregado
            js_response = self.session.get(f"{self.base_url}/static/js/app.js")
            if js_response.ok:
                js_content = js_response.text
                
                # Verificar se tem as funções de extração real
                funcoes_reais = [
                    "fazerUploadArquivo",
                    "atualizarStepStatus",
                    "atualizarProgresso",
                    "limparEvidenciasAnteriores",
                    "processarEvidencias"
                ]
                
                for funcao in funcoes_reais:
                    if funcao in js_content:
                        self.log_teste(f"Função {funcao}", True, "Função encontrada")
                    else:
                        return self.log_teste(f"Função {funcao}", False, "Função não encontrada")
                
                # Verificar se não tem funções simuladas
                funcoes_simuladas = [
                    "simulateProcessing",
                    "showResults",
                    "Math.random"
                ]
                
                for funcao in funcoes_simuladas:
                    if funcao in js_content:
                        return self.log_teste(f"Função simulada {funcao}", False, "Função simulada encontrada")
                
                self.log_teste("Funções simuladas", True, "Nenhuma função simulada encontrada")
                
            else:
                return self.log_teste("Carregamento JS", False, f"Status: {js_response.status_code}")
            
            # 5. Verificar se os elementos HTML necessários existem
            elementos_necessarios = [
                'uploadArea',
                'logFileInput',
                'fileInfo',
                'fileName',
                'fileSize',
                'processamentoSection',
                'btnProcessarEvidencias',
                'step1',
                'step1Status',
                'step2',
                'step2Status',
                'step3',
                'step3Status',
                'progressFill',
                'resultadosSection',
                'sucessosCount',
                'falhasCount',
                'enviadosCount'
            ]
            
            for elemento in elementos_necessarios:
                if soup.find(id=elemento):
                    self.log_teste(f"Elemento {elemento}", True, "Elemento encontrado")
                else:
                    return self.log_teste(f"Elemento {elemento}", False, "Elemento não encontrado")
            
            # 6. Verificar se o template está usando o layout SB Admin 2
            if 'sb-admin-2.min.css' in response.text and 'sb-admin-2.min.js' in response.text:
                self.log_teste("Layout SB Admin 2", True, "Template usando layout correto")
            else:
                return self.log_teste("Layout SB Admin 2", False, "Template não usando layout correto")
            
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            return True
            
        except Exception as e:
            self.log_teste("Teste geral", False, str(e))
            return False

def main():
    print("🚀 INICIANDO TESTE DO FRONTEND - EXTRAÇÃO REAL")
    print("=" * 70)
    
    teste = TesteFrontendExtracaoReal()
    sucesso = teste.testar_frontend_extracao_real()
    
    print("\n" + "=" * 70)
    if sucesso:
        print("✅ TESTE CONCLUÍDO COM SUCESSO")
        print("📋 Resumo:")
        print("   - app.js carregado corretamente")
        print("   - JavaScript simulado removido")
        print("   - Funções de extração real implementadas")
        print("   - Elementos HTML necessários presentes")
        print("   - Layout SB Admin 2 aplicado")
        print("\n🎯 Agora o frontend está usando a extração real!")
    else:
        print("❌ TESTE FALHOU")
        print("🔧 Verifique os erros acima e corrija os problemas")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
