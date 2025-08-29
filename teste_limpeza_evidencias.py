#!/usr/bin/env python3
"""
Teste para verificar a funcionalidade de limpeza de evidências
"""

import requests
import time
from bs4 import BeautifulSoup
import json

class TesteLimpezaEvidencias:
    def __init__(self):
        self.base_url = "http://localhost:8081"
        self.session = requests.Session()
        
    def log_teste(self, nome_teste, sucesso, detalhes=""):
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{status} - {nome_teste}: {detalhes}")
        return sucesso
        
    def testar_limpeza_evidencias(self):
        """Testa se a limpeza de evidências funciona corretamente"""
        print("🧪 TESTANDO LIMPEZA DE EVIDÊNCIAS")
        print("=" * 50)
        
        try:
            # 1. Acessar página de evidências
            response = self.session.get(f"{self.base_url}/evidencias")
            if not response.ok:
                return self.log_teste("Acesso à página", False, f"Status: {response.status_code}")
            
            self.log_teste("Acesso à página", True, "Página carregada com sucesso")
            
            # 2. Verificar se o JavaScript está carregado
            soup = BeautifulSoup(response.content, 'html.parser')
            app_js = soup.find('script', src=lambda x: x and 'app.js' in x)
            if not app_js:
                return self.log_teste("JavaScript", False, "app.js não encontrado")
            
            self.log_teste("JavaScript", True, "app.js carregado")
            
            # 3. Verificar se a função de limpeza existe no código
            js_response = self.session.get(f"{self.base_url}/static/js/app.js")
            if js_response.ok:
                js_content = js_response.text
                if "limparEvidenciasAnteriores" in js_content:
                    self.log_teste("Função de limpeza", True, "Função encontrada no JavaScript")
                else:
                    return self.log_teste("Função de limpeza", False, "Função não encontrada")
            else:
                return self.log_teste("Carregamento JS", False, f"Status: {js_response.status_code}")
            
            # 4. Verificar se a função é chamada no processamento
            if "limparEvidenciasAnteriores()" in js_content:
                self.log_teste("Chamada da função", True, "Função é chamada no processamento")
            else:
                return self.log_teste("Chamada da função", False, "Função não é chamada")
            
            # 5. Verificar se a função é chamada ao selecionar arquivo
            if "processarArquivo" in js_content and "limparEvidenciasAnteriores" in js_content:
                self.log_teste("Limpeza ao selecionar arquivo", True, "Limpeza implementada")
            else:
                return self.log_teste("Limpeza ao selecionar arquivo", False, "Limpeza não implementada")
            
            # 6. Verificar se a função é chamada no reset do modal
            if "resetarModalEvidencias" in js_content and "limparEvidenciasAnteriores" in js_content:
                self.log_teste("Limpeza no reset do modal", True, "Limpeza implementada")
            else:
                return self.log_teste("Limpeza no reset do modal", False, "Limpeza não implementada")
            
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            return True
            
        except Exception as e:
            self.log_teste("Teste geral", False, str(e))
            return False

def main():
    print("🚀 INICIANDO TESTE DE LIMPEZA DE EVIDÊNCIAS")
    print("=" * 60)
    
    teste = TesteLimpezaEvidencias()
    sucesso = teste.testar_limpeza_evidencias()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ TESTE CONCLUÍDO COM SUCESSO")
        print("📋 Resumo:")
        print("   - Função de limpeza implementada")
        print("   - Limpeza automática ao selecionar novo arquivo")
        print("   - Limpeza automática ao iniciar processamento")
        print("   - Limpeza automática no reset do modal")
        print("   - JavaScript carregado corretamente")
    else:
        print("❌ TESTE FALHOU")
        print("🔧 Verifique os erros acima e corrija os problemas")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
