#!/usr/bin/env python3
"""
Script para extrair prints de evidências de testes do arquivo log.html
Baseado no projeto de referência, adaptado para nosso projeto
"""

import re
import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

def extrair_prints():
    """Extrai prints de evidências do arquivo log.html"""
    
    print("🚀 Iniciando extração de prints de evidências...")
    
    # Configuração do Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,3000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Configurar o driver do Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Caminho para o arquivo log.html
        log_path = os.path.abspath("log.html")
        
        if not os.path.exists(log_path):
            print(f"❌ Arquivo log.html não encontrado em: {log_path}")
            return
        
        print(f"📄 Carregando arquivo: {log_path}")
        driver.get(f"file://{log_path}")
        time.sleep(2)
        
        # Diretório base para os prints
        base_dir = os.path.abspath("prints_tests")
        
        # Limpar diretório anterior se existir
        if os.path.exists(base_dir):
            print("🧹 Removendo pasta antiga de prints...")
            try:
                shutil.rmtree(base_dir)
                print("✅ Pasta removida com sucesso.")
            except Exception as e:
                print(f"❌ Erro ao remover pasta: {e}")
        
        # Criar diretórios
        falhas_dir = os.path.join(base_dir, "falhas")
        sucessos_dir = os.path.join(base_dir, "sucessos")
        os.makedirs(falhas_dir, exist_ok=True)
        os.makedirs(sucessos_dir, exist_ok=True)
        
        print(f"📁 Diretórios criados:")
        print(f"   - Falhas: {falhas_dir}")
        print(f"   - Sucessos: {sucessos_dir}")
        
        # Buscar todos os elementos de teste
        test_divs = driver.find_elements(By.CSS_SELECTOR, ".children.populated > div.test")
        print(f"🧪 Total de testes encontrados: {len(test_divs)}")
        
        if len(test_divs) == 0:
            print("⚠️ Nenhum teste encontrado. Verifique se o arquivo log.html contém dados de teste.")
            return
        
        processados = {}
        falhas_count = 0
        sucessos_count = 0
        
        for i, test_div in enumerate(test_divs, start=1):
            try:
                test_id = test_div.get_attribute("id")
                
                # Buscar o label para determinar se é falha ou sucesso
                try:
                    label = test_div.find_element(By.CSS_SELECTOR, ".element-header-left .label")
                    is_fail = "fail" in label.get_attribute("class").lower()
                except:
                    # Se não encontrar label, tentar outras formas de identificar
                    is_fail = "fail" in test_div.get_attribute("class").lower()
                
                # Buscar o nome do teste
                try:
                    name_span = test_div.find_element(By.CSS_SELECTOR, ".element-header-left .name")
                    test_name = name_span.text.strip()
                except:
                    test_name = f"teste_{i}"
                
                # Extrair código do teste (padrão: CREDT-XXXX ou similar)
                match = re.search(r'[A-Z]+-\d+', test_name)
                if match:
                    test_code = match.group(0)
                else:
                    # Se não encontrar padrão, criar código baseado no nome
                    test_code = test_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                    if len(test_code) > 20:
                        test_code = test_code[:20]
                
                # Verificar duplicidade com prioridade para falha
                if test_code in processados:
                    if processados[test_code] == "fail":
                        print(f"⚠️ Teste {test_code} já processado como falha, pulando...")
                        continue
                    elif processados[test_code] == "pass" and is_fail:
                        print(f"⚠️ Atualizando status de {test_code} de sucesso para falha")
                        sucesso_path = os.path.join(sucessos_dir, f"{test_code}.png")
                        if os.path.exists(sucesso_path):
                            os.remove(sucesso_path)
                            sucessos_count -= 1
                    else:
                        print(f"⚠️ Teste {test_code} já processado, pulando...")
                        continue
                
                processados[test_code] = "fail" if is_fail else "pass"
                
                # Expandir apenas testes de sucesso para mostrar mais detalhes
                if not is_fail:
                    try:
                        header = test_div.find_element(By.CLASS_NAME, "element-header")
                        ActionChains(driver).move_to_element(header).click().perform()
                        time.sleep(0.4)
                    except Exception as e:
                        print(f"⚠️ Não foi possível expandir o card de {test_code}: {e}")
                
                # Scroll para o elemento
                driver.execute_script("arguments[0].scrollIntoView(true);", test_div)
                time.sleep(0.2)
                
                # Determinar diretório de destino
                target_dir = falhas_dir if is_fail else sucessos_dir
                screenshot_path = os.path.join(target_dir, f"{test_code}.png")
                
                # Capturar screenshot
                test_div.screenshot(screenshot_path)
                
                # Contar estatísticas
                if is_fail:
                    falhas_count += 1
                    print(f"❌ Screenshot falha salvo: {test_code}.png")
                else:
                    sucessos_count += 1
                    print(f"✅ Screenshot sucesso salvo: {test_code}.png")
                
            except Exception as e:
                print(f"❌ Erro ao capturar screenshot do teste {i} ({test_id}): {e}")
        
        # Resumo final
        print("\n" + "="*50)
        print("📊 RESUMO DA EXTRAÇÃO")
        print("="*50)
        print(f"🧪 Total de testes processados: {len(processados)}")
        print(f"❌ Falhas capturadas: {falhas_count}")
        print(f"✅ Sucessos capturados: {sucessos_count}")
        print(f"📁 Diretório de falhas: {falhas_dir}")
        print(f"📁 Diretório de sucessos: {sucessos_dir}")
        print("="*50)
        
        if falhas_count > 0 or sucessos_count > 0:
            print("🎉 Extração concluída com sucesso!")
        else:
            print("⚠️ Nenhum screenshot foi capturado. Verifique o arquivo log.html.")
            
    except Exception as e:
        print(f"❌ Erro durante a extração: {e}")
        
    finally:
        driver.quit()
        print("🔧 Driver do Chrome fechado.")

if __name__ == "__main__":
    extrair_prints()
