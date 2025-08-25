#!/usr/bin/env python3
"""
Script para adicionar evidências de testes aos casos de teste no Jira
Baseado no projeto de referência, adaptado para nosso projeto
"""

import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import glob

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Jira
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_URL_BASE = os.getenv("JIRA_URL")
PROJECT_KEY = os.getenv("PROJECT_KEY")

# Verificar variáveis de ambiente
required_vars = ["JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_URL", "PROJECT_KEY"]
for var in required_vars:
    if not os.getenv(var):
        print(f"[ERRO] Variável de ambiente '{var}' não encontrada.")

# Configurações de diretórios
PRINTS_DIR = os.path.abspath("prints_tests")
SUBDIRS = {
    "falhas": {
        "mensagem": [
            {"type": "text", "text": "TESTE AUTOMAÇÃO ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "REPROVADO", "marks": [{"type": "strong"}]}
        ],
        "tipo": "error"
    },
    "sucessos": {
        "mensagem": [
            {"type": "text", "text": "TESTE AUTOMAÇÃO ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": "APROVADO", "marks": [{"type": "strong"}]}
        ],
        "tipo": "success"
    }
}

def anexar_arquivo(issue_key, file_path):
    """Anexa um arquivo PNG ao card do Jira."""
    url = f"{JIRA_URL_BASE}/rest/api/3/issue/{issue_key}/attachments"
    headers = {"X-Atlassian-Token": "no-check"}

    try:
        with open(file_path, "rb") as file_data:
            files = {"file": (os.path.basename(file_path), file_data, "image/png")}
            response = requests.post(
                url, headers=headers, files=files, auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
            )

        if response.status_code in [200, 201]:
            result = response.json()[0]
            print(f"[ANEXO] 📎 Enviado para {issue_key}: {os.path.basename(file_path)}")
            return {
                "filename": result["filename"],
                "id": result["id"],
            }
        else:
            print(f"[ERRO] ❌ Erro ao anexar em {issue_key}: {response.status_code}")
            print(f"[RESPOSTA] {response.text}")
            return None
    except Exception as e:
        print(f"[ERRO] ❌ Exceção ao anexar arquivo: {e}")
        return None

def comentar_com_imagem(issue_key, mensagem, tipo_painel, image_meta):
    """Adiciona comentário no Jira com imagem."""
    url = f"{JIRA_URL_BASE}/rest/api/3/issue/{issue_key}/comment"
    headers = {"Content-Type": "application/json"}

    image_url = f"{JIRA_URL_BASE}/rest/api/3/attachment/content/{image_meta['id']}"

    body = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "panel",
                "attrs": {"panelType": tipo_painel},
                "content": [
                    {"type": "paragraph", "content": mensagem}
                ]
            },
            {
                "type": "mediaSingle",
                "attrs": {"layout": "center"},
                "content": [
                    {
                        "type": "media",
                        "attrs": {
                            "type": "external",
                            "url": image_url
                        }
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            url, json={"body": body}, headers=headers, auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        )

        if response.status_code == 201:
            print(f"[COMENTÁRIO] 💬 Adicionado em {issue_key}")
            return True
        else:
            print(f"[ERRO] ❌ Erro ao comentar em {issue_key}: {response.status_code}")
            print(f"[RESPOSTA] {response.text}")
            return False
    except Exception as e:
        print(f"[ERRO] ❌ Exceção ao comentar: {e}")
        return False

def processar_evidencias():
    """Processa todas as evidências e adiciona aos casos de teste correspondentes."""
    
    print("🚀 Iniciando processamento de evidências...")
    
    if not os.path.exists(PRINTS_DIR):
        print(f"❌ Diretório de prints não encontrado: {PRINTS_DIR}")
        print("💡 Execute primeiro o script extrair_prints.py")
        return
    
    total_processados = 0
    total_sucessos = 0
    total_erros = 0
    
    for subdir, config in SUBDIRS.items():
        subdir_path = os.path.join(PRINTS_DIR, subdir)
        
        if not os.path.exists(subdir_path):
            print(f"⚠️ Diretório {subdir} não encontrado, pulando...")
            continue
        
        print(f"\n📁 Processando {subdir}...")
        
        # Buscar todos os arquivos PNG no diretório
        png_files = glob.glob(os.path.join(subdir_path, "*.png"))
        
        if not png_files:
            print(f"⚠️ Nenhum arquivo PNG encontrado em {subdir}")
            continue
        
        for png_file in png_files:
            try:
                # Extrair o código do teste do nome do arquivo
                filename = os.path.basename(png_file)
                test_code = os.path.splitext(filename)[0]  # Remove extensão .png
                
                print(f"🔍 Processando: {test_code}")
                
                # Anexar arquivo ao Jira
                anexo_result = anexar_arquivo(test_code, png_file)
                
                if anexo_result:
                    # Adicionar comentário com a imagem
                    comentario_sucesso = comentar_com_imagem(
                        test_code, 
                        config["mensagem"], 
                        config["tipo"], 
                        anexo_result
                    )
                    
                    if comentario_sucesso:
                        total_sucessos += 1
                        print(f"✅ Evidência adicionada com sucesso para {test_code}")
                    else:
                        total_erros += 1
                        print(f"❌ Erro ao adicionar comentário para {test_code}")
                else:
                    total_erros += 1
                    print(f"❌ Erro ao anexar arquivo para {test_code}")
                
                total_processados += 1
                
            except Exception as e:
                total_erros += 1
                print(f"❌ Erro ao processar {png_file}: {e}")
    
    # Resumo final
    print("\n" + "="*50)
    print("📊 RESUMO DO PROCESSAMENTO")
    print("="*50)
    print(f"📁 Total de evidências processadas: {total_processados}")
    print(f"✅ Sucessos: {total_sucessos}")
    print(f"❌ Erros: {total_erros}")
    print("="*50)
    
    if total_sucessos > 0:
        print("🎉 Processamento concluído com sucesso!")
    else:
        print("⚠️ Nenhuma evidência foi processada com sucesso.")

def processar_evidencia_especifica(issue_key, tipo_resultado="sucessos"):
    """Processa evidência para um caso de teste específico."""
    
    print(f"🎯 Processando evidência específica para {issue_key}...")
    
    if tipo_resultado not in SUBDIRS:
        print(f"❌ Tipo de resultado inválido: {tipo_resultado}")
        print(f"💡 Tipos válidos: {list(SUBDIRS.keys())}")
        return
    
    subdir_path = os.path.join(PRINTS_DIR, tipo_resultado)
    png_file = os.path.join(subdir_path, f"{issue_key}.png")
    
    if not os.path.exists(png_file):
        print(f"❌ Arquivo de evidência não encontrado: {png_file}")
        return
    
    config = SUBDIRS[tipo_resultado]
    
    # Anexar arquivo
    anexo_result = anexar_arquivo(issue_key, png_file)
    
    if anexo_result:
        # Adicionar comentário
        comentario_sucesso = comentar_com_imagem(
            issue_key, 
            config["mensagem"], 
            config["tipo"], 
            anexo_result
        )
        
        if comentario_sucesso:
            print(f"✅ Evidência adicionada com sucesso para {issue_key}")
        else:
            print(f"❌ Erro ao adicionar comentário para {issue_key}")
    else:
        print(f"❌ Erro ao anexar arquivo para {issue_key}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if len(sys.argv) == 3:
            # Processar evidência específica
            issue_key = sys.argv[1]
            tipo_resultado = sys.argv[2]
            processar_evidencia_especifica(issue_key, tipo_resultado)
        else:
            print("💡 Uso: python adicionar_evidencias.py [ISSUE_KEY] [TIPO_RESULTADO]")
            print("💡 Tipos de resultado: sucessos, falhas")
            print("💡 Exemplo: python adicionar_evidencias.py CREDT-1343 sucessos")
    else:
        # Processar todas as evidências
        processar_evidencias()
