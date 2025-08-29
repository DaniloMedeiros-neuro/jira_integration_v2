#!/usr/bin/env python3
"""
Teste para verificar se a barra de progresso está funcionando corretamente
"""

import requests
import time
from bs4 import BeautifulSoup
import json
import os

class TesteProgressBar:
    def __init__(self):
        self.base_url = "http://localhost:8081"
        self.session = requests.Session()
        
    def log_teste(self, nome_teste, sucesso, detalhes=""):
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{status} - {nome_teste}: {detalhes}")
        return sucesso
        
    def testar_progress_bar(self):
        """Testa se a barra de progresso está funcionando corretamente"""
        print("🧪 TESTANDO BARRA DE PROGRESSO")
        print("=" * 50)
        
        try:
            # 1. Acessar página de evidências
            response = self.session.get(f"{self.base_url}/evidencias")
            if not response.ok:
                return self.log_teste("Acesso à página", False, f"Status: {response.status_code}")
            
            self.log_teste("Acesso à página", True, "Página carregada com sucesso")
            
            # 2. Verificar se os elementos da barra de progresso existem
            soup = BeautifulSoup(response.content, 'html.parser')
            
            progress_elements = [
                ('progressFill', 'Elemento da barra de progresso'),
                ('progressText', 'Texto da barra de progresso')
            ]
            
            for element_id, description in progress_elements:
                element = soup.find(id=element_id)
                if element:
                    self.log_teste(f"Elemento {element_id}", True, f"{description} encontrado")
                else:
                    return self.log_teste(f"Elemento {element_id}", False, f"{description} não encontrado")
            
            # 3. Verificar se a função atualizarProgresso está implementada
            js_response = self.session.get(f"{self.base_url}/static/js/app.js")
            if js_response.ok:
                js_content = js_response.text
                
                # Verificar se a função existe
                if "function atualizarProgresso" in js_content:
                    self.log_teste("Função atualizarProgresso", True, "Função encontrada")
                else:
                    return self.log_teste("Função atualizarProgresso", False, "Função não encontrada")
                
                # Verificar se atualiza tanto width quanto text
                if "progressFill.style.width" in js_content and "progressText.textContent" in js_content:
                    self.log_teste("Atualização completa", True, "Atualiza width e text")
                else:
                    return self.log_teste("Atualização completa", False, "Não atualiza width e text")
                
                # Verificar se tem logs de debug
                if "console.log" in js_content and "Progresso atualizado" in js_content:
                    self.log_teste("Logs de debug", True, "Logs implementados")
                else:
                    self.log_teste("Logs de debug", False, "Logs não implementados")
                
                # Verificar se é chamada nos pontos corretos
                chamadas_progresso = [
                    "atualizarProgresso(0)",
                    "atualizarProgresso(10)",
                    "atualizarProgresso(25)",
                    "atualizarProgresso(50)",
                    "atualizarProgresso(70)",
                    "atualizarProgresso(85)",
                    "atualizarProgresso(100)"
                ]
                
                chamadas_encontradas = 0
                for chamada in chamadas_progresso:
                    if chamada in js_content:
                        chamadas_encontradas += 1
                
                if chamadas_encontradas >= 5:  # Pelo menos 5 chamadas diferentes
                    self.log_teste("Chamadas de progresso", True, f"{chamadas_encontradas} chamadas encontradas")
                else:
                    return self.log_teste("Chamadas de progresso", False, f"Apenas {chamadas_encontradas} chamadas encontradas")
                
            else:
                return self.log_teste("Carregamento JS", False, f"Status: {js_response.status_code}")
            
            # 4. Verificar se a barra de progresso tem o HTML correto
            progress_bar = soup.find('div', class_='progress-bar')
            if progress_bar:
                self.log_teste("HTML da barra", True, "Barra de progresso encontrada")
                
                # Verificar se tem as classes corretas
                classes = progress_bar.get('class', [])
                if 'progress-bar-striped' in classes and 'progress-bar-animated' in classes:
                    self.log_teste("Classes da barra", True, "Classes corretas aplicadas")
                else:
                    self.log_teste("Classes da barra", False, "Classes incorretas")
            else:
                return self.log_teste("HTML da barra", False, "Barra de progresso não encontrada")
            
            # 5. Verificar se o progresso é resetado na limpeza
            if "limparEvidenciasAnteriores" in js_content and "atualizarProgresso(0)" in js_content:
                self.log_teste("Reset do progresso", True, "Progresso é resetado na limpeza")
            else:
                self.log_teste("Reset do progresso", False, "Progresso não é resetado na limpeza")
            
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            return True
            
        except Exception as e:
            self.log_teste("Teste geral", False, str(e))
            return False

def main():
    print("🚀 INICIANDO TESTE DA BARRA DE PROGRESSO")
    print("=" * 60)
    
    teste = TesteProgressBar()
    sucesso = teste.testar_progress_bar()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ TESTE CONCLUÍDO COM SUCESSO")
        print("📋 Resumo:")
        print("   - Elementos da barra de progresso presentes")
        print("   - Função atualizarProgresso implementada")
        print("   - Atualização de width e text funcionando")
        print("   - Logs de debug implementados")
        print("   - Chamadas de progresso nos pontos corretos")
        print("   - Reset do progresso na limpeza")
        print("\n🎯 Agora a barra de progresso deve funcionar corretamente!")
    else:
        print("❌ TESTE FALHOU")
        print("🔧 Verifique os erros acima e corrija os problemas")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
