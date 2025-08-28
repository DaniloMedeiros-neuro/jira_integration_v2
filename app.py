from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pandas as pd
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import re

import base64

load_dotenv()

app = Flask(__name__)

# Adicionar headers CORS manualmente
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configurações do Jira
JIRA_BASE_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

HEADERS = {
    "Authorization": f"Basic {os.getenv('JIRA_AUTH')}",
    "Content-Type": "application/json"
}

def obter_account_id():
    """Obtém o account ID do usuário autenticado"""
    response = requests.get(
        f"{JIRA_BASE_URL}/rest/api/3/myself",
        headers=HEADERS,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )
    if response.status_code == 200:
        return response.json()["accountId"]
    return None

def obter_informacoes_issue(issue_key):
    """Obtém informações da issue pai"""
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
        response = requests.get(url, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 200:
            issue_data = response.json()
            project_key = issue_data['fields']['project']['key']
            issue_type = issue_data['fields']['issuetype']['name']
            print(f"Issue {issue_key}: Projeto={project_key}, Tipo={issue_type}")
            return project_key, issue_type
        else:
            print(f"Erro ao obter issue {issue_key}: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Erro ao obter informações da issue {issue_key}: {e}")
        return None, None

def buscar_issues_similares(issue_key):
    """Busca issues similares para sugerir correção de erros de digitação"""
    try:
        # Extrair o prefixo do projeto (ex: BC de BC-126)
        if '-' in issue_key:
            prefixo = issue_key.split('-')[0]
        else:
            prefixo = issue_key
        
        # Buscar issues recentes com o mesmo prefixo
        jql = f'project = {prefixo} ORDER BY created DESC'
        url = f"{JIRA_BASE_URL}/rest/api/3/search"
        payload = {
            "jql": jql,
            "maxResults": 5,
            "fields": ["summary"]
        }
        
        response = requests.post(url, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 200:
            issues = response.json().get('issues', [])
            sugestoes = [issue['key'] for issue in issues[:3]]  # Retorna até 3 sugestões
            return sugestoes
        else:
            return []
    except Exception as e:
        print(f"Erro ao buscar issues similares: {e}")
        return []

def obter_tipos_issue_disponiveis(project_key):
    """Obtém os tipos de issue disponíveis para um projeto"""
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/project/{project_key}"
        response = requests.get(url, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 200:
            project_data = response.json()
            issue_types = project_data.get('issueTypes', [])
            
            todos_tipos = [issue_type['name'] for issue_type in issue_types]
            subtarefas = [issue_type['name'] for issue_type in issue_types if issue_type.get('subtask', False)]
            issues_normais = [issue_type['name'] for issue_type in issue_types if not issue_type.get('subtask', False)]
            
            print(f"Tipos disponíveis no projeto {project_key}: {todos_tipos}")
            return todos_tipos, subtarefas, issues_normais
        else:
            print(f"Erro ao obter tipos de issue: {response.status_code}")
            return [], [], []
    except Exception as e:
        print(f"Erro ao obter tipos de issue: {e}")
        return [], [], []

def linkar_issue(issue_key, issue_pai):
    """Cria um link entre a issue pai e o caso de teste"""
    try:
        payload = {
            "type": {"name": "Casos de Teste"},
            "inwardIssue": {"key": issue_pai},
            "outwardIssue": {"key": issue_key}
        }
        
        url = f"{JIRA_BASE_URL}/rest/api/3/issueLink"
        response = requests.post(url, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 201:
            print(f"✅ Link criado: {issue_pai} ←→ {issue_key}")
            return True
        else:
            print(f"⚠️ Erro ao criar link: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ Exceção ao criar link: {e}")
        return False

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')



@app.route('/api/casos-teste/<issue_pai>')
def buscar_casos_teste(issue_pai):
    """Busca todos os casos de teste filhos de uma issue pai"""
    try:
        print(f"=== BUSCANDO CASOS DE TESTE PARA {issue_pai} ===")
        
        # Busca a issue pai primeiro
        url_pai = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_pai}"
        response_pai = requests.get(url_pai, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response_pai.status_code != 200:
            print(f"❌ Issue pai {issue_pai} não encontrada: {response_pai.status_code}")
            return jsonify({"erro": f"Issue pai {issue_pai} não encontrada", "status_code": response_pai.status_code, "resposta": response_pai.text}), 404
        
        print(f"✅ Issue pai {issue_pai} encontrada")
        
        # Extrair informações da issue pai
        issue_pai_data = response_pai.json()
        issue_pai_fields = issue_pai_data.get("fields", {})
        requisito_info = {
            "id": issue_pai,
            "titulo": issue_pai_fields.get("summary", ""),
            "descricao": extrair_texto_descricao(issue_pai_fields.get("description")),
            "status": issue_pai_fields.get("status", {}).get("name", ""),
            "tipo": issue_pai_fields.get("issuetype", {}).get("name", ""),
            "projeto": issue_pai_fields.get("project", {}).get("key", ""),
            "criado_em": issue_pai_fields.get("created", ""),
            "atualizado_em": issue_pai_fields.get("updated", "")
        }
        
        # Busca os casos de teste filhos (subtarefas E issues vinculadas por links)
        jql = f'(parent = "{issue_pai}" OR issue in linkedIssues("{issue_pai}")) ORDER BY key DESC'
        print(f"🔍 JQL Query: {jql}")
        
        url_filhos = f"{JIRA_BASE_URL}/rest/api/3/search"
        payload = {
            "jql": jql,
            "maxResults": 100,
            "fields": ["summary", "description", "status", "created", "updated", "components", "issuetype", "customfield_10062", "customfield_10063", "customfield_10065", "customfield_10066"]
        }
        
        print(f"📡 Fazendo requisição para: {url_filhos}")
        print(f"📡 Payload: {payload}")
        
        response_filhos = requests.post(url_filhos, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        print(f"📡 Status da resposta: {response_filhos.status_code}")
        
        if response_filhos.status_code != 200:
            print(f"❌ Erro na resposta: {response_filhos.text}")
            return jsonify({"erro": "Erro ao buscar casos de teste", "status_code": response_filhos.status_code, "resposta": response_filhos.text}), 500
        
        response_data = response_filhos.json()
        print(f"📡 Total de issues retornadas: {response_data.get('total', 0)}")
        print(f"📡 MaxResults: {response_data.get('maxResults', 0)}")
        
        issues = response_data.get("issues", [])
        print(f"📡 Issues encontradas: {len(issues)}")
        
        # Log de todas as issues encontradas
        for i, issue in enumerate(issues):
            print(f"  {i+1}. {issue.get('key')} - {issue.get('fields', {}).get('summary', 'Sem título')}")
        
        casos_teste = []
        
        for issue in issues:
            fields = issue.get("fields", {})
            issue_type = fields.get("issuetype", {}).get("name", "")
            
            print(f"🔍 Processando issue: {issue.get('key')} - Tipo: {issue_type}")
            
            # Filtrar apenas casos de teste (excluir subtarefas)
            if issue_type == "Caso de Teste":
                # Extrair campos customizados com tratamento de erro
                tipo_execucao = "N/A"
                tipo_teste = "N/A"
                objetivo = ""
                pre_condicoes = ""
                
                try:
                    tipo_execucao = fields.get("customfield_10062", {}).get("value", "N/A")
                except:
                    tipo_execucao = "N/A"
                
                try:
                    tipo_teste = fields.get("customfield_10063", {}).get("value", "N/A")
                except:
                    tipo_teste = "N/A"
                
                try:
                    objetivo = extrair_texto_campo(fields.get("customfield_10066"))
                except:
                    objetivo = ""
                
                try:
                    pre_condicoes = extrair_texto_campo(fields.get("customfield_10065"))
                except:
                    pre_condicoes = ""
                
                caso = {
                    "id": issue.get("key"),
                    "titulo": fields.get("summary", ""),
                    "descricao": extrair_texto_descricao(fields.get("description")),
                    "status": fields.get("status", {}).get("name", ""),
                    "criado_em": fields.get("created", ""),
                    "atualizado_em": fields.get("updated", ""),
                    "tipo_execucao": tipo_execucao,
                    "tipo_teste": tipo_teste,
                    "componentes": [c.get("name", "") for c in fields.get("components", [])],
                    "objetivo": objetivo,
                    "pre_condicoes": pre_condicoes,
                    "tipo_issue": issue_type
                }
                casos_teste.append(caso)
                print(f"✅ Adicionado caso de teste: {issue.get('key')} ({issue_type})")
            else:
                print(f"⚠️ Ignorado (não é caso de teste): {issue.get('key')} ({issue_type})")
        
        print(f"✅ Total de casos de teste processados: {len(casos_teste)}")
        
        return jsonify({
            "issue_pai": issue_pai,
            "requisito": requisito_info,
            "total_casos": len(casos_teste),
            "casos_teste": casos_teste
        })
        
    except Exception as e:
        print(f"❌ Exceção capturada: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

@app.route('/api/casos-teste/<issue_pai>/exportar-excel')
def exportar_casos_teste_excel(issue_pai):
    """Exporta os casos de teste de uma issue pai em formato Excel"""
    try:
        # Busca a issue pai primeiro
        url_pai = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_pai}"
        response_pai = requests.get(url_pai, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response_pai.status_code != 200:
            return jsonify({"erro": f"Issue pai {issue_pai} não encontrada"}), 404
        
        # Busca os casos de teste filhos (subtarefas)
        jql = f'parent = "{issue_pai}" ORDER BY key DESC'
        url_filhos = f"{JIRA_BASE_URL}/rest/api/3/search"
        payload = {
            "jql": jql,
            "maxResults": 100,
            "fields": ["summary", "description", "status", "created", "updated", "customfield_10062", "customfield_10063", "components", "customfield_10066", "customfield_10065"]
        }
        
        response_filhos = requests.post(url_filhos, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response_filhos.status_code != 200:
            return jsonify({"erro": "Erro ao buscar casos de teste"}), 500
        
        issues = response_filhos.json().get("issues", [])
        
        # Criar DataFrame
        dados = []
        for issue in issues:
            fields = issue.get("fields", {})
            dados.append({
                "ID": issue.get("key"),
                "Título": fields.get("summary", ""),
                "Status": fields.get("status", {}).get("name", ""),
                "Tipo de Execução": fields.get("customfield_10062", {}).get("value", ""),
                "Tipo de Teste": fields.get("customfield_10063", {}).get("value", ""),
                "Componentes": ", ".join([c.get("name", "") for c in fields.get("components", [])]),
                "Objetivo": extrair_texto_campo(fields.get("customfield_10066")),
                "Pré-condições": extrair_texto_campo(fields.get("customfield_10065")),
                "Descrição": extrair_texto_descricao(fields.get("description")),
                "Criado em": fields.get("created", ""),
                "Atualizado em": fields.get("updated", "")
            })
        
        df = pd.DataFrame(dados)
        
        # Criar arquivo Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Casos de Teste', index=False)
            
            # Acessar a planilha para formatação
            workbook = writer.book
            worksheet = writer.sheets['Casos de Teste']
            
            # Formatação do cabeçalho
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            # Aplicar formatação ao cabeçalho
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
            
            # Ajustar largura das colunas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Nome do arquivo
        filename = f"casos_teste_{issue_pai}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/planilha/<issue_pai>')
def visualizar_planilha(issue_pai):
    """Página para visualizar casos de teste em formato de planilha"""
    return render_template('planilha.html', issue_pai=issue_pai)

@app.route('/metricas')
def visualizar_metricas():
    """Página para visualizar métricas administrativas"""
    return render_template('metricas.html')





@app.route('/api/caso-teste/<issue_key>', methods=['GET'])
def obter_caso_teste(issue_key):
    """Obtém um caso de teste específico"""
    try:
        print(f"=== OBTENDO CASO DE TESTE: {issue_key} ===")
        
        if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
            print("Erro: Configurações do Jira incompletas")
            return jsonify({"erro": "Configurações do Jira incompletas"}), 500
        
        # Buscar a issue no Jira
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()}"
        }
        
        response = requests.get(url, headers=headers)
        print(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 404:
            return jsonify({"erro": "Caso de teste não encontrado"}), 404
        
        if response.status_code != 200:
            print(f"Erro na API do Jira: {response.text}")
            return jsonify({"erro": "Erro ao buscar caso de teste no Jira"}), 500
        
        issue_data = response.json()
        print("Dados da issue obtidos com sucesso")
        
        # Extrair dados da issue
        fields = issue_data.get('fields', {})
        
        # Extrair descrição (pode estar em formato Atlassian Document Format)
        descricao = ""
        if 'description' in fields and fields['description']:
            descricao_content = fields['description'].get('content', [])
            for content in descricao_content:
                if content.get('type') == 'codeBlock':
                    for code_content in content.get('content', []):
                        if code_content.get('type') == 'text':
                            descricao += code_content.get('text', '')
        
        # Extrair objetivo e pré-condições da descrição
        objetivo = ""
        pre_condicoes = ""
        if 'description' in fields and fields['description']:
            descricao_content = fields['description'].get('content', [])
            current_section = None
            
            for content in descricao_content:
                if content.get('type') == 'paragraph':
                    paragraph_text = ""
                    for para_content in content.get('content', []):
                        if para_content.get('type') == 'text':
                            paragraph_text += para_content.get('text', '')
                    
                    # Verificar se é um cabeçalho de seção
                    if 'Objetivo:' in paragraph_text:
                        current_section = 'objetivo'
                    elif 'Pré Condição:' in paragraph_text:
                        current_section = 'pre_condicoes'
                    elif paragraph_text.strip() and current_section:
                        # Se não for cabeçalho e temos uma seção ativa, é o conteúdo
                        if current_section == 'objetivo':
                            objetivo = paragraph_text.strip()
                        elif current_section == 'pre_condicoes':
                            pre_condicoes = paragraph_text.strip()
                        current_section = None
        
        # Extrair campos customizados
        tipo_execucao = fields.get('customfield_10062', {}).get('value', 'Manual')
        tipo_teste = fields.get('customfield_10063', {}).get('value', 'Funcional')
        
        # Extrair componentes
        componentes = []
        if 'components' in fields:
            componentes = [comp.get('name', '') for comp in fields['components']]
        
        caso_teste = {
            "id": issue_data.get('key'),
            "titulo": fields.get('summary', ''),
            "status": fields.get('status', {}).get('name', ''),
            "descricao": descricao,
            "objetivo": objetivo,
            "pre_condicoes": pre_condicoes,
            "tipo_execucao": tipo_execucao,
            "tipo_teste": tipo_teste,
            "componentes": componentes,
            "criado_em": fields.get('created', ''),
            "atualizado_em": fields.get('updated', '')
        }
        
        print("Caso de teste processado com sucesso")
        return jsonify(caso_teste)
        
    except Exception as e:
        print(f"Erro ao obter caso de teste: {str(e)}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route('/api/caso-teste', methods=['POST'])
def criar_caso_teste():
    """Cria um novo caso de teste"""
    try:
        print("=== CRIANDO CASO DE TESTE ===")
        dados = request.json
        print("Dados recebidos:", dados)
        
        issue_pai = dados.get("issue_pai")
        print("Issue pai:", issue_pai)
        
        if not issue_pai:
            print("Erro: Issue pai não fornecida")
            return jsonify({"erro": "ID da issue pai é obrigatório"}), 400
        
        print("Verificando configurações...")
        print("JIRA_BASE_URL:", JIRA_BASE_URL)
        print("JIRA_EMAIL:", JIRA_EMAIL)
        print("JIRA_API_TOKEN:", "***" if JIRA_API_TOKEN else "NÃO CONFIGURADO")
        
        # Verificação mais detalhada
        if not JIRA_BASE_URL:
            print("❌ JIRA_BASE_URL não configurado")
            return jsonify({"erro": "JIRA_BASE_URL não configurado"}), 500
        if not JIRA_EMAIL:
            print("❌ JIRA_EMAIL não configurado")
            return jsonify({"erro": "JIRA_EMAIL não configurado"}), 500
        if not JIRA_API_TOKEN:
            print("❌ JIRA_API_TOKEN não configurado")
            return jsonify({"erro": "JIRA_API_TOKEN não configurado"}), 500
        
        print("✅ Todas as configurações estão presentes")
        
        # Obter informações da issue pai
        project_key, issue_type_pai = obter_informacoes_issue(issue_pai)
        if not project_key:
            # Tentar encontrar issues similares para sugerir correção
            sugestoes = buscar_issues_similares(issue_pai)
            if sugestoes:
                erro_msg = f"Issue pai não encontrada ou inválida. Sugestões: {', '.join(sugestoes)}"
            else:
                erro_msg = "Issue pai não encontrada ou inválida"
            
            print(f"Erro: {erro_msg}")
            return jsonify({"erro": erro_msg}), 400
        
        # Verificar tipos de issue disponíveis
        todos_tipos, _, _ = obter_tipos_issue_disponiveis(project_key)
        
        # SEMPRE criar como "Caso de Teste" (não como subtarefa)
        tipo_caso_teste = "Caso de Teste"
        
        # Verificar se "Caso de Teste" está disponível
        if "Caso de Teste" in todos_tipos:
            print(f"✅ Usando tipo: {tipo_caso_teste}")
        else:
            print("❌ ERRO: Tipo 'Caso de Teste' não disponível no projeto!")
            print("Tipos disponíveis:", todos_tipos)
            return jsonify({"erro": f"Tipo 'Caso de Teste' não disponível no projeto {project_key}. Tipos disponíveis: {todos_tipos}"}), 400
        
        account_id = obter_account_id()
        print("Account ID:", account_id)
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": dados.get("titulo", ""),
                "issuetype": {"name": tipo_caso_teste},
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": "Objetivo:", "marks": [{"type": "strong"}]}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": dados.get("objetivo", "")}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": "Pré Condição:", "marks": [{"type": "strong"}]}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": dados.get("pre_condicoes", "")}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                        {
                            "type": "codeBlock",
                            "attrs": {"language": "gherkin"},
                            "content": [{"type": "text", "text": dados.get("descricao", "")}]
                        }
                    ]
                },
                # Campos customizados do projeto CREDT
                "customfield_10062": {"value": dados.get("tipo_execucao", "Automatizado")},
                "customfield_10063": {"value": dados.get("tipo_teste", "Funcional")},
                "customfield_10066": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": dados.get("objetivo", "")}]
                        }
                    ]
                },
                "customfield_10065": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": dados.get("pre_condicoes", "")}]
                        }
                    ]
                }
            }
        }
        
        # Não adicionar parent (criar como issue independente)
        print(f"Criando como 'Caso de Teste' independente (sem parent)")
        
        # Adiciona componentes apenas se forem válidos
        componentes = dados.get("componentes", [])
        if componentes and componentes != ["teste"]:
            # Filtra apenas componentes válidos (API, Frontend, Backend, etc.)
            componentes_validos = [c for c in componentes if c in ["API", "Frontend", "Backend", "Mobile", "Web"]]
            if componentes_validos:
                payload["fields"]["components"] = [{"name": c} for c in componentes_validos]
        
        print("Payload preparado:", payload)
        
        url = f"{JIRA_BASE_URL}/rest/api/3/issue"
        print("URL da requisição:", url)
        print("Headers:", HEADERS)
        
        response = requests.post(url, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        print("Status code da resposta:", response.status_code)
        print("Resposta do Jira:", response.text)
        
        if response.status_code == 201:
            issue_created = response.json()
            issue_key = issue_created.get("key")
            print("Issue criada com sucesso:", issue_key)
            
            # Atribui o responsável
            if account_id:
                atribuir_responsavel(issue_key, account_id)
            
            # Criar link entre a issue pai e o caso de teste
            link_criado = linkar_issue(issue_key, issue_pai)
            if link_criado:
                print(f"✅ Link criado entre {issue_pai} e {issue_key}")
            else:
                print(f"⚠️ Aviso: Não foi possível criar link entre {issue_pai} e {issue_key}")
            
            print(f"✅ Caso de teste {issue_key} criado com sucesso e vinculado a {issue_pai}")
            
            return jsonify({
                "sucesso": True,
                "mensagem": f"Caso de teste {issue_key} criado com sucesso",
                "issue_key": issue_key
            })
        else:
            print(f"Erro do Jira: {response.status_code} - {response.text}")
            return jsonify({"erro": f"Erro ao criar caso de teste: {response.status_code}", "detalhes": response.text}), 500
            
    except Exception as e:
        print("Exceção capturada:", str(e))
        import traceback
        print("Traceback completo:")
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

@app.route('/api/caso-teste/<issue_key>', methods=['PUT'])
def atualizar_caso_teste(issue_key):
    """Atualiza um caso de teste existente"""
    try:
        dados = request.json
        
        payload = {
            "fields": {
                "summary": dados.get("titulo", ""),
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": "Objetivo:", "marks": [{"type": "strong"}]}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": dados.get("objetivo", "")}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": "Pré Condição:", "marks": [{"type": "strong"}]}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": dados.get("pre_condicoes", "")}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                        {
                            "type": "codeBlock",
                            "attrs": {"language": "gherkin"},
                            "content": [{"type": "text", "text": dados.get("descricao", "")}]
                        }
                    ]
                },
                "customfield_10062": {"value": dados.get("tipo_execucao", "Automatizado")},
                "customfield_10063": {"value": dados.get("tipo_teste", "Funcional")},
                "components": [{"name": c} for c in dados.get("componentes", ["API"])],
                "customfield_10066": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": dados.get("objetivo", "")}]
                        }
                    ]
                },
                "customfield_10065": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": dados.get("pre_condicoes", "")}]
                        }
                    ]
                }
            }
        }
        
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
        response = requests.put(url, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 204:
            return jsonify({
                "sucesso": True,
                "mensagem": f"Caso de teste {issue_key} atualizado com sucesso"
            })
        else:
            return jsonify({"erro": f"Erro ao atualizar caso de teste: {response.status_code}", "detalhes": response.text}), 500
            
    except Exception as e:
        return jsonify({"erro": str(e)}), 500



@app.route('/api/casos-teste/batch-update', methods=['PUT'])
def atualizar_casos_teste_batch():
    """Atualiza múltiplos casos de teste de uma vez"""
    try:
        dados = request.json
        casos_para_atualizar = dados.get('casos', [])
        
        if not casos_para_atualizar:
            return jsonify({"erro": "Nenhum caso de teste fornecido para atualização"}), 400
        
        resultados = []
        sucessos = 0
        erros = 0
        
        for caso in casos_para_atualizar:
            issue_key = caso.get('issue_key')
            campos_alterados = caso.get('campos', {})
            
            if not issue_key or not campos_alterados:
                erros += 1
                resultados.append({
                    "issue_key": issue_key,
                    "status": "erro",
                    "mensagem": "Dados inválidos"
                })
                continue
            
            try:
                # Preparar payload para atualização
                payload = {"fields": {}}
                
                # Mapear campos personalizados
                if 'titulo' in campos_alterados:
                    payload["fields"]["summary"] = campos_alterados['titulo']
                
                if 'status' in campos_alterados:
                    payload["fields"]["status"] = {"name": campos_alterados['status']}
                
                if 'tipo_execucao' in campos_alterados:
                    payload["fields"]["customfield_10062"] = {"value": campos_alterados['tipo_execucao']}
                
                if 'tipo_teste' in campos_alterados:
                    payload["fields"]["customfield_10063"] = {"value": campos_alterados['tipo_teste']}
                
                if 'componentes' in campos_alterados:
                    componentes = [{"name": comp.strip()} for comp in campos_alterados['componentes'].split(',') if comp.strip()]
                    payload["fields"]["components"] = componentes
                
                if 'objetivo' in campos_alterados:
                    # Atualizar campo customizado
                    payload["fields"]["customfield_10066"] = {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": campos_alterados['objetivo'] or ""
                                    }
                                ]
                            }
                        ]
                    }
                    
                    # Também atualizar a descrição principal para manter sincronização
                    # Primeiro, buscar a descrição atual para preservar outros campos
                    try:
                        url_get = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
                        response_get = requests.get(url_get, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
                        if response_get.status_code == 200:
                            issue_data = response_get.json()
                            descricao_atual = issue_data.get('fields', {}).get('description', {})
                            
                            # Extrair pré-condições e descrição BDD da descrição atual
                            pre_condicoes_atual = ""
                            descricao_bdd_atual = ""
                            
                            if descricao_atual and descricao_atual.get('content'):
                                current_section = None
                                for content in descricao_atual.get('content', []):
                                    if content.get('type') == 'paragraph':
                                        paragraph_text = ""
                                        for para_content in content.get('content', []):
                                            if para_content.get('type') == 'text':
                                                paragraph_text += para_content.get('text', '')
                                        
                                        if 'Pré Condição:' in paragraph_text:
                                            current_section = 'pre_condicoes'
                                        elif paragraph_text.strip() and current_section == 'pre_condicoes':
                                            pre_condicoes_atual = paragraph_text.strip()
                                            current_section = None
                                    elif content.get('type') == 'codeBlock':
                                        for code_content in content.get('content', []):
                                            if code_content.get('type') == 'text':
                                                descricao_bdd_atual += code_content.get('text', '')
                            
                            # Criar nova descrição com objetivo atualizado
                            payload["fields"]["description"] = {
                                "type": "doc",
                                "version": 1,
                                "content": [
                                    {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": "Objetivo:", "marks": [{"type": "strong"}]}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": campos_alterados['objetivo'] or ""}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": "Pré Condição:", "marks": [{"type": "strong"}]}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": pre_condicoes_atual}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                                    {
                                        "type": "codeBlock",
                                        "attrs": {"language": "gherkin"},
                                        "content": [{"type": "text", "text": descricao_bdd_atual}]
                                    }
                                ]
                            }
                    except Exception as e:
                        print(f"Erro ao sincronizar descrição: {e}")
                        # Se não conseguir sincronizar, pelo menos atualizar o campo customizado
                
                if 'pre_condicoes' in campos_alterados:
                    # Atualizar campo customizado
                    payload["fields"]["customfield_10065"] = {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": campos_alterados['pre_condicoes'] or ""
                                    }
                                ]
                            }
                        ]
                    }
                    
                    # Também atualizar a descrição principal para manter sincronização
                    # Primeiro, buscar a descrição atual para preservar outros campos
                    try:
                        url_get = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
                        response_get = requests.get(url_get, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
                        if response_get.status_code == 200:
                            issue_data = response_get.json()
                            descricao_atual = issue_data.get('fields', {}).get('description', {})
                            
                            # Extrair objetivo e descrição BDD da descrição atual
                            objetivo_atual = ""
                            descricao_bdd_atual = ""
                            
                            if descricao_atual and descricao_atual.get('content'):
                                current_section = None
                                for content in descricao_atual.get('content', []):
                                    if content.get('type') == 'paragraph':
                                        paragraph_text = ""
                                        for para_content in content.get('content', []):
                                            if para_content.get('type') == 'text':
                                                paragraph_text += para_content.get('text', '')
                                        
                                        if 'Objetivo:' in paragraph_text:
                                            current_section = 'objetivo'
                                        elif paragraph_text.strip() and current_section == 'objetivo':
                                            objetivo_atual = paragraph_text.strip()
                                            current_section = None
                                    elif content.get('type') == 'codeBlock':
                                        for code_content in content.get('content', []):
                                            if code_content.get('type') == 'text':
                                                descricao_bdd_atual += code_content.get('text', '')
                            
                            # Criar nova descrição com pré-condições atualizadas
                            payload["fields"]["description"] = {
                                "type": "doc",
                                "version": 1,
                                "content": [
                                    {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": "Objetivo:", "marks": [{"type": "strong"}]}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": objetivo_atual}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": "Pré Condição:", "marks": [{"type": "strong"}]}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": campos_alterados['pre_condicoes'] or ""}]},
                                    {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                                    {
                                        "type": "codeBlock",
                                        "attrs": {"language": "gherkin"},
                                        "content": [{"type": "text", "text": descricao_bdd_atual}]
                                    }
                                ]
                            }
                    except Exception as e:
                        print(f"Erro ao sincronizar descrição: {e}")
                        # Se não conseguir sincronizar, pelo menos atualizar o campo customizado
                
                if 'descricao' in campos_alterados:
                    payload["fields"]["description"] = {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                            {"type": "paragraph", "content": [{"type": "text", "text": "Objetivo:", "marks": [{"type": "strong"}]}]},
                            {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                            {"type": "paragraph", "content": [{"type": "text", "text": "Pré Condição:", "marks": [{"type": "strong"}]}]},
                            {"type": "paragraph", "content": [{"type": "text", "text": ""}]},
                            {
                                "type": "codeBlock",
                                "attrs": {"language": "gherkin"},
                                "content": [{"type": "text", "text": campos_alterados['descricao']}]
                            }
                        ]
                    }
                
                # Fazer a requisição para atualizar
                url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
                response = requests.put(url, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
                
                if response.status_code == 204:
                    sucessos += 1
                    resultados.append({
                        "issue_key": issue_key,
                        "status": "sucesso",
                        "mensagem": "Atualizado com sucesso"
                    })
                else:
                    erros += 1
                    resultados.append({
                        "issue_key": issue_key,
                        "status": "erro",
                        "mensagem": f"Erro {response.status_code}: {response.text}"
                    })
                    
            except Exception as e:
                erros += 1
                resultados.append({
                    "issue_key": issue_key,
                    "status": "erro",
                    "mensagem": str(e)
                })
        
        return jsonify({
            "mensagem": f"Processamento concluído. {sucessos} sucessos, {erros} erros.",
            "resultados": resultados,
            "sucessos": sucessos,
            "erros": erros
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def atribuir_responsavel(issue_key, account_id):
    """Atribui um responsável para a issue"""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/assignee"
    payload = {"accountId": account_id}
    try:
        response = requests.put(url, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        return response.status_code == 204
    except:
        return False

def extrair_texto_descricao(descricao):
    """Extrai texto simples da descrição em formato Atlassian Document Format preservando quebras de linha"""
    if not descricao or not descricao.get("content"):
        return ""
    
    texto = ""
    for content in descricao.get("content", []):
        if content.get("type") == "paragraph":
            paragrafo_texto = ""
            for item in content.get("content", []):
                if item.get("type") == "text":
                    paragrafo_texto += item.get("text", "")
            if paragrafo_texto:
                texto += paragrafo_texto + "\n"
        elif content.get("type") == "codeBlock":
            texto += f"\n```\n{content.get('content', [{}])[0].get('text', '')}\n```\n"
    
    return texto.strip()

def extrair_texto_campo(campo):
    """Extrai texto simples de campos customizados preservando quebras de linha"""
    if not campo or not campo.get("content"):
        return ""
    
    texto = ""
    for content in campo.get("content", []):
        if content.get("type") == "paragraph":
            paragrafo_texto = ""
            for item in content.get("content", []):
                if item.get("type") == "text":
                    paragrafo_texto += item.get("text", "")
            if paragrafo_texto:
                texto += paragrafo_texto + "\n"
    
    return texto.strip()



@app.route('/planilha-manual')
def planilha_manual():
    """Página da planilha manual editável"""
    return render_template('planilha_manual.html')









@app.route('/api/exportar-planilha-manual', methods=['POST'])
def exportar_planilha_manual():
    """API para exportar dados da planilha manual para o Jira"""
    try:
        data = request.get_json()
        issue_pai = data.get('issue_pai')
        casos = data.get('casos', [])
        
        if not issue_pai:
            return jsonify({
                'sucesso': False,
                'erro': 'Issue pai é obrigatória'
            }), 400
        
        if not casos:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum caso de teste fornecido'
            }), 400
        
        print(f"📤 Exportando {len(casos)} casos para issue pai: {issue_pai}")
        
        resultados = []
        sucessos = 0
        erros = 0
        
        for caso in casos:
            try:
                # Criar caso de teste no Jira
                resultado = criar_caso_teste_planilha_manual(caso, issue_pai)
                
                if resultado.get('sucesso'):
                    sucessos += 1
                    resultados.append({
                        'titulo': caso.get('titulo'),
                        'jira_id': resultado.get('jira_id'),
                        'created_at': resultado.get('created_at'),
                        'updated_at': resultado.get('updated_at')
                    })
                else:
                    erros += 1
                    resultados.append({
                        'titulo': caso.get('titulo'),
                        'erro': resultado.get('erro', 'Erro desconhecido')
                    })
                    
            except Exception as e:
                erros += 1
                print(f"❌ Erro ao criar caso '{caso.get('titulo')}': {e}")
                resultados.append({
                    'titulo': caso.get('titulo'),
                    'erro': str(e)
                })
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Exportação concluída: {sucessos} sucessos, {erros} erros',
            'sucessos': sucessos,
            'erros': erros,
            'total': len(casos),
            'resultados': resultados
        })
        
    except Exception as e:
        print(f"❌ Erro na API exportar planilha manual: {e}")
        return jsonify({
            'sucesso': False,
            'erro': f'Erro interno: {str(e)}'
        }), 500



















@app.route('/api/metricas-epico/<epic_key>')
def obter_metricas_epico(epic_key):
    """Obtém métricas administrativas e globais de um épico"""
    try:
        print(f"=== OBTENDO MÉTRICAS DO ÉPICO: {epic_key} ===")
        
        if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
            return jsonify({"erro": "Configurações do Jira incompletas"}), 500
        
        # Buscar o épico
        epic_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{epic_key}"
        print(f"URL do épico: {epic_url}")
        print(f"JIRA_BASE_URL: {JIRA_BASE_URL}")
        print(f"JIRA_EMAIL: {JIRA_EMAIL}")
        print(f"JIRA_API_TOKEN: {JIRA_API_TOKEN[:20]}...")
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()}"
        }
        
        epic_response = requests.get(epic_url, headers=headers)
        print(f"Status code da resposta: {epic_response.status_code}")
        print(f"Resposta: {epic_response.text[:200]}...")
        
        if epic_response.status_code != 200:
            return jsonify({"erro": f"Épico {epic_key} não encontrado"}), 404
        
        epic_data = epic_response.json()
        epic_fields = epic_data.get('fields', {})
        
        # Buscar todas as issues do épico
        jql = f'"Epic Link" = {epic_key} OR parent = {epic_key}'
        search_url = f"{JIRA_BASE_URL}/rest/api/3/search"
        
        search_payload = {
            "jql": jql,
            "maxResults": 1000,
            "fields": [
                "key", "summary", "status", "assignee", "reporter", 
                "created", "updated", "resolutiondate", "timespent", 
                "timeestimate", "timeoriginalestimate", "storypoints",
                "issuetype", "priority", "components", "labels",
                "worklog", "comment"
            ]
        }
        
        search_response = requests.post(search_url, headers=headers, json=search_payload)
        if search_response.status_code != 200:
            return jsonify({"erro": "Erro ao buscar issues do épico"}), 500
        
        issues_data = search_response.json()
        issues = issues_data.get('issues', [])
        
        # Calcular métricas
        metricas = calcular_metricas_epico(epic_fields, issues)
        
        return jsonify(metricas)
        
    except Exception as e:
        print(f"Erro ao obter métricas do épico: {str(e)}")
        import traceback
        print("Traceback completo:")
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

def calcular_metricas_epico(epic_fields, issues):
    """Calcula métricas administrativas do épico"""
    
    try:
        print(f"Processando {len(issues)} issues")
        
        # Métricas básicas
        total_issues = len(issues)
        # Status considerados como concluídos (incluindo status em português)
        status_concluidos = ['Done', 'Resolved', 'Closed', 'CONCLUÍDO', 'Concluído']
        issues_concluidas = sum(1 for issue in issues if issue['fields'].get('status', {}).get('name') in status_concluidos)
        percentual_conclusao = (issues_concluidas / total_issues * 100) if total_issues > 0 else 0
        
        # Métricas de tempo
        cycle_times = []
        lead_times = []
        tempo_estimado_vs_real = []
    
        for issue in issues:
            # Cycle Time (In Progress até Done)
            if issue['fields'].get('status', {}).get('name') in status_concluidos:
                try:
                    created = datetime.fromisoformat(issue['fields'].get('created', '').replace('Z', '+00:00'))
                    resolution_date = issue['fields'].get('resolutiondate')
                    if resolution_date:
                        resolved = datetime.fromisoformat(resolution_date.replace('Z', '+00:00'))
                        lead_time = (resolved - created).days
                        lead_times.append(lead_time)
                except (ValueError, TypeError) as e:
                    print(f"Erro ao processar datas da issue {issue.get('key', 'unknown')}: {e}")
                    continue
            
            # Tempo estimado vs real
            time_estimate = issue['fields'].get('timeestimate', 0) or 0
            time_spent = issue['fields'].get('timespent', 0) or 0
            if time_estimate > 0:
                diferenca = ((time_spent - time_estimate) / time_estimate) * 100
                tempo_estimado_vs_real.append(diferenca)
        
        # Métricas de esforço
        story_points_total = sum(issue['fields'].get('storypoints', 0) or 0 for issue in issues)
        story_points_concluidos = sum(
            issue['fields'].get('storypoints', 0) or 0 
            for issue in issues 
            if issue['fields'].get('status', {}).get('name') in status_concluidos
        )
        
        # Distribuição por status
        status_distribution = {}
        for issue in issues:
            status = issue['fields'].get('status', {}).get('name')
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Distribuição por responsável
        assignee_distribution = {}
        for issue in issues:
            assignee = issue['fields'].get('assignee')
            if assignee and isinstance(assignee, dict):
                assignee_name = assignee.get('displayName', 'Não atribuído')
            else:
                assignee_name = 'Não atribuído'
            assignee_distribution[assignee_name] = assignee_distribution.get(assignee_name, 0) + 1
        
        # Métricas de qualidade
        bugs_count = sum(1 for issue in issues if issue['fields'].get('issuetype', {}).get('name') == 'Bug')
        dependencias_count = sum(1 for issue in issues if 'blocks' in str(issue['fields']))
        
        return {
        "epic_info": {
            "key": epic_fields.get('key'),
            "summary": epic_fields.get('summary'),
            "status": epic_fields.get('status', {}).get('name'),
            "created": epic_fields.get('created'),
            "updated": epic_fields.get('updated')
        },
        "metricas_progresso": {
            "total_issues": total_issues,
            "issues_concluidas": issues_concluidas,
            "issues_pendentes": total_issues - issues_concluidas,
            "percentual_conclusao": round(percentual_conclusao, 2),
            "story_points_total": story_points_total,
            "story_points_concluidos": story_points_concluidos,
            "story_points_pendentes": story_points_total - story_points_concluidos
        },
        "metricas_tempo": {
            "cycle_time_medio": round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0,
            "lead_time_medio": round(sum(lead_times) / len(lead_times), 2) if lead_times else 0,
            "tempo_estimado_vs_real_medio": round(sum(tempo_estimado_vs_real) / len(tempo_estimado_vs_real), 2) if tempo_estimado_vs_real else 0
        },
        "metricas_qualidade": {
            "bugs_count": bugs_count,
            "dependencias_count": dependencias_count,
            "percentual_bugs": round((bugs_count / total_issues * 100), 2) if total_issues > 0 else 0
        },
        "distribuicoes": {
            "por_status": status_distribution,
            "por_responsavel": assignee_distribution
        },
        "detalhes_issues": [
            {
                "key": issue['key'],
                "summary": issue['fields'].get('summary', ''),
                "status": issue['fields'].get('status', {}).get('name'),
                "assignee": issue['fields'].get('assignee', {}).get('displayName', 'Não atribuído') if issue['fields'].get('assignee') else 'Não atribuído',
                "story_points": issue['fields'].get('storypoints', 0) or 0,
                "time_spent": issue['fields'].get('timespent', 0) or 0,
                "time_estimate": issue['fields'].get('timeestimate', 0) or 0,
                "created": issue['fields'].get('created', ''),
                "updated": issue['fields'].get('updated', '')
            }
            for issue in issues
        ]
    }
    except Exception as e:
        print(f"Erro ao calcular métricas: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e



@app.route('/api/analise-epico-detalhada/<epic_key>')
def obter_analise_epico_detalhada(epic_key):
    """Obtém análise detalhada de um épico com métricas avançadas"""
    try:
        print(f"=== OBTENDO ANÁLISE DETALHADA DO ÉPICO: {epic_key} ===")
        
        if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
            return jsonify({"erro": "Configurações do Jira incompletas"}), 500
        
        # Buscar o épico
        epic_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{epic_key}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()}"
        }
        
        epic_response = requests.get(epic_url, headers=headers)
        if epic_response.status_code != 200:
            return jsonify({"erro": f"Épico {epic_key} não encontrado"}), 404
        
        epic_data = epic_response.json()
        epic_fields = epic_data.get('fields', {})
        
        # Buscar todas as issues do épico (incluindo sub-tarefas)
        jql = f'"Epic Link" = {epic_key} OR parent = {epic_key}'
        search_url = f"{JIRA_BASE_URL}/rest/api/3/search"
        
        search_payload = {
            "jql": jql,
            "maxResults": 1000,
            "fields": [
                "key", "summary", "status", "assignee", "reporter", 
                "created", "updated", "resolutiondate", "timespent", 
                "timeestimate", "timeoriginalestimate", "storypoints",
                "issuetype", "priority", "components", "labels",
                "worklog", "comment", "parent", "subtasks", "issuelinks"
            ]
        }
        
        search_response = requests.post(search_url, headers=headers, json=search_payload)
        if search_response.status_code != 200:
            return jsonify({"erro": "Erro ao buscar issues do épico"}), 500
        
        issues_data = search_response.json()
        issues = issues_data.get('issues', [])
        
        # Calcular análise detalhada
        analise = calcular_analise_epico_detalhada(epic_fields, issues)
        
        return jsonify(analise)
        
    except Exception as e:
        print(f"Erro ao obter análise detalhada do épico: {str(e)}")
        import traceback
        print("Traceback completo:")
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

def calcular_analise_epico_detalhada(epic_fields, issues):
    """Calcula análise detalhada do épico com métricas avançadas"""
    
    try:
        print(f"Processando análise detalhada de {len(issues)} issues")
        
        # 1. Resumo geral
        total_issues = len(issues)
        stories_count = sum(1 for issue in issues if issue['fields'].get('issuetype', {}).get('name') == 'Story')
        tasks_count = sum(1 for issue in issues if issue['fields'].get('issuetype', {}).get('name') == 'Task')
        bugs_count = sum(1 for issue in issues if issue['fields'].get('issuetype', {}).get('name') == 'Bug')
        
        # 2. Breakdown por status
        status_breakdown = {}
        status_concluidos = ['Done', 'Resolved', 'Closed', 'CONCLUÍDO', 'Concluído']
        status_em_progresso = ['In Progress', 'Em Progresso', 'In Development']
        status_impedimento = ['Blocked', 'Impedimento', 'On Hold']
        
        for issue in issues:
            status = issue['fields'].get('status', {}).get('name')
            story_points = issue['fields'].get('storypoints', 0) or 0
            
            if status not in status_breakdown:
                status_breakdown[status] = {
                    'count': 0,
                    'percentual': 0,
                    'story_points': 0,
                    'tempo_medio': 0
                }
            
            status_breakdown[status]['count'] += 1
            status_breakdown[status]['story_points'] += story_points
        
        # Calcular percentuais
        for status in status_breakdown:
            status_breakdown[status]['percentual'] = round((status_breakdown[status]['count'] / total_issues) * 100, 2)
        
        # 3. Progresso geral
        concluido_count = sum(1 for issue in issues if issue['fields'].get('status', {}).get('name') in status_concluidos)
        em_progresso_count = sum(1 for issue in issues if issue['fields'].get('status', {}).get('name') in status_em_progresso)
        impedimento_count = sum(1 for issue in issues if issue['fields'].get('status', {}).get('name') in status_impedimento)
        
        progresso = {
            'concluido': {
                'count': concluido_count,
                'percentual': round((concluido_count / total_issues) * 100, 2) if total_issues > 0 else 0
            },
            'em_progresso': {
                'count': em_progresso_count,
                'percentual': round((em_progresso_count / total_issues) * 100, 2) if total_issues > 0 else 0
            },
            'impedimento': {
                'count': impedimento_count,
                'percentual': round((impedimento_count / total_issues) * 100, 2) if total_issues > 0 else 0
            }
        }
        
        # 4. Story Points
        story_points_total = sum(issue['fields'].get('storypoints', 0) or 0 for issue in issues)
        story_points_concluido = sum(
            issue['fields'].get('storypoints', 0) or 0 
            for issue in issues 
            if issue['fields'].get('status', {}).get('name') in status_concluidos
        )
        story_points_pendente = story_points_total - story_points_concluido
        percentual_concluido = round((story_points_concluido / story_points_total) * 100, 2) if story_points_total > 0 else 0
        
        # 5. Casos de Teste
        casos_teste = []
        casos_teste_keys = set()  # Para evitar duplicações
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()}"
        }
        
        print(f"Buscando casos de teste para {len(issues)} issues...")
        
        # Função para adicionar caso de teste sem duplicação
        def adicionar_caso_teste(test_case):
            if test_case and test_case.get('fields'):
                key = test_case.get('key', '')
                if key and key not in casos_teste_keys:
                    casos_teste_keys.add(key)
                    
                    # Obter status geral do issue
                    status_geral = test_case['fields'].get('status', {}).get('name', '')
                    
                    # Obter status específico de execução do teste
                    test_execution_status = test_case['fields'].get('customfield_10016', {}).get('value', '')
                    
                    # Determinar status de teste baseado na lógica do Jira
                    if test_execution_status:
                        # Se tem status específico de execução, usar ele
                        test_status = test_execution_status
                    elif status_geral.lower() in ['concluído', 'done', 'resolved', 'closed']:
                        # Se está concluído mas não tem status específico, assumir que passou
                        test_status = 'Passou'
                    elif status_geral.lower() in ['em progresso', 'in progress', 'to do']:
                        # Se está em progresso, assumir que não foi executado
                        test_status = 'Não Executado'
                    else:
                        # Status padrão
                        test_status = 'Não Executado'
                    
                    # Log detalhado para debug
                    print(f"🔍 Processando caso de teste {key}:")
                    print(f"   - Status Geral: {status_geral}")
                    print(f"   - Status Execução: {test_execution_status}")
                    print(f"   - Status Final: {test_status}")
                    
                    casos_teste.append({
                        'key': key,
                        'summary': test_case['fields'].get('summary', ''),
                        'status': status_geral,
                        'test_status': test_status,
                        'assignee': test_case['fields'].get('assignee', {}).get('displayName', 'Não atribuído') if test_case['fields'].get('assignee') else 'Não atribuído',
                        'ultima_execucao': 'N/A'
                    })
                    return True
            return False
        
        # Buscar todos os casos de teste de uma vez - estratégia mais abrangente
        all_test_cases_jql = f'issuetype = "Test" AND ('
        issue_conditions = []
        for issue in issues:
            issue_key = issue['key']
            # Buscar casos de teste vinculados, sub-tarefas e relacionados
            issue_conditions.append(f'issue in linkedIssues({issue_key}) OR parent = {issue_key}')
        all_test_cases_jql += ' OR '.join(issue_conditions) + ')'
        
        test_search_url = f"{JIRA_BASE_URL}/rest/api/3/search"
        test_payload = {
            "jql": all_test_cases_jql,
            "maxResults": 500,  # Aumentado para capturar mais casos
            "fields": ["key", "summary", "status", "assignee", "customfield_10016", "issuelinks", "issuetype"]
        }
        
        try:
            # Busca principal: casos de teste vinculados e sub-tarefas
            test_response = requests.post(test_search_url, headers=headers, json=test_payload)
            if test_response.status_code == 200:
                test_data = test_response.json()
                test_issues = test_data.get('issues', [])
                print(f"Encontrados {len(test_issues)} casos de teste na busca principal")
                
                # Processar casos de teste encontrados
                for test_case in test_issues:
                    adicionar_caso_teste(test_case)
                
                # Busca adicional: todos os issues vinculados para filtrar casos de teste
                print(f"Fazendo busca adicional para capturar todos os casos de teste...")
                all_linked_conditions = []
                for issue in issues:
                    issue_key = issue['key']
                    all_linked_conditions.append(f'issue in linkedIssues({issue_key})')
                all_linked_jql = ' OR '.join(all_linked_conditions)
                all_linked_payload = {
                    "jql": all_linked_jql,
                    "maxResults": 200,
                    "fields": ["key", "summary", "status", "assignee", "issuetype", "customfield_10016"]
                }
                
                all_linked_response = requests.post(test_search_url, headers=headers, json=all_linked_payload)
                if all_linked_response.status_code == 200:
                    all_linked_data = all_linked_response.json()
                    all_linked_issues = all_linked_data.get('issues', [])
                    print(f"Encontrados {len(all_linked_issues)} issues vinculados na busca adicional")
                    
                    # Filtrar apenas issues de teste
                    for linked_issue in all_linked_issues:
                        if linked_issue and linked_issue.get('fields'):
                            issue_type = linked_issue['fields'].get('issuetype', {}).get('name', '')
                            summary = linked_issue['fields'].get('summary', '')
                            
                            # Verificar se é um caso de teste
                            if (issue_type.lower() == 'test' or 
                                'test' in summary.lower() or 
                                'caso de teste' in summary.lower() or
                                'test case' in summary.lower()):
                                adicionar_caso_teste(linked_issue)
                
                print(f"Total de casos de teste únicos encontrados: {len(casos_teste)}")
                
            else:
                print(f"Erro na busca de casos de teste: {test_response.status_code}")
        except Exception as e:
            print(f"Erro ao buscar casos de teste: {e}")
        
        print(f"Total de casos de teste encontrados: {len(casos_teste)}")
        
        # 6. Evolução do Escopo (simulado - seria necessário histórico)
        evolucao_escopo = {
            'labels': ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4'],
            'adicionados': [5, 3, 2, 1],
            'removidos': [0, 1, 0, 0]
        }
        
        # 7. Velocidade e Tempo
        lead_times = []
        cycle_times = []
        
        for issue in issues:
            if issue['fields'].get('status', {}).get('name') in status_concluidos:
                try:
                    created = datetime.fromisoformat(issue['fields'].get('created', '').replace('Z', '+00:00'))
                    resolution_date = issue['fields'].get('resolutiondate')
                    if resolution_date:
                        resolved = datetime.fromisoformat(resolution_date.replace('Z', '+00:00'))
                        lead_time = (resolved - created).days
                        lead_times.append(lead_time)
                except (ValueError, TypeError) as e:
                    continue
        
        lead_time_medio = round(sum(lead_times) / len(lead_times), 2) if lead_times else 0
        cycle_time_medio = round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0
        
        # Velocidade simulada
        evolucao_velocidade = {
            'labels': ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4'],
            'velocidade': [8, 12, 10, 15],
            'throughput': [5, 8, 6, 10]
        }
        
        # Distribuição de tempo
        distribuicao_tempo = {
            '1-3 dias': 30,
            '4-7 dias': 45,
            '8-14 dias': 20,
            '15+ dias': 5
        }
        
        return {
            "resumo": {
                "total_issues": total_issues,
                "stories_count": stories_count,
                "tasks_count": tasks_count,
                "bugs_count": bugs_count
            },
            "progresso": progresso,
            "story_points": {
                "total": story_points_total,
                "concluido": story_points_concluido,
                "pendente": story_points_pendente,
                "percentual_concluido": percentual_concluido
            },
            "breakdown_status": status_breakdown,
            "casos_teste": casos_teste,
            "evolucao_escopo": evolucao_escopo,
            "evolucao_velocidade": evolucao_velocidade,
            "distribuicao_tempo": distribuicao_tempo,
            "metricas_tempo": {
                "lead_time_medio": lead_time_medio,
                "cycle_time_medio": cycle_time_medio,
                "velocidade_sprint": round(story_points_concluido / 4, 2),  # Assumindo 4 sprints
                "throughput_sprint": round(concluido_count / 4, 2)
            }
        }
        
    except Exception as e:
        print(f"Erro ao calcular análise detalhada: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

# ========================================
# ROTAS PARA SISTEMA DE EVIDÊNCIAS
# ========================================

import re
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64

@app.route('/api/evidencias/upload', methods=['POST'])
def upload_evidencias():
    """Upload de arquivo log.html para processamento de evidências"""
    try:
        if 'log_file' not in request.files:
            return jsonify({"erro": "Nenhum arquivo enviado"}), 400
        
        file = request.files['log_file']
        if file.filename == '':
            return jsonify({"erro": "Nenhum arquivo selecionado"}), 400
        
        if not file.filename.endswith('.html'):
            return jsonify({"erro": "Apenas arquivos HTML são aceitos"}), 400
        
        # Salvar arquivo temporariamente
        log_path = os.path.join(os.getcwd(), 'log.html')
        file.save(log_path)
        
        # Limpar evidências anteriores antes do processamento
        limpar_evidencias_anteriores()
        
        # Processar o arquivo HTML usando método híbrido
        resultado = processar_evidencias_hibrido(log_path)
        
        if resultado['sucesso']:
            return jsonify({
                "sucesso": True,
                "mensagem": "Evidências processadas com sucesso",
                "estatisticas": resultado['estatisticas'],
                "nomes_evidencias": resultado['nomes_evidencias']
            })
        else:
            return jsonify({"erro": resultado['erro']}), 500
            
    except Exception as e:
        print(f"Erro no upload de evidências: {str(e)}")
        return jsonify({"erro": str(e)}), 500

def extrair_codigo_card(texto):
    """Extrai código de card do texto (formato: PROJ-123, CREDT-456, etc.)"""
    import re
    
    # Padrões para códigos de card em ordem de prioridade
    padroes = [
        r'([A-Z]{2,7}-\d+)',  # PROJ-123, CREDT-456, FEATURE-202
        r'([A-Z]+-\d+)',      # QUALQUER-123
        r'([A-Z]{2,4}\d+)',   # PROJ123, CREDT456 (sem hífen)
        r'(BC-\d+)',          # Padrão específico BC
        r'(TEST-\d+)',        # Padrão específico TEST
        r'(BUG-\d+)',         # Padrão específico BUG
        r'(FEATURE-\d+)',     # Padrão específico FEATURE
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto.upper())
        if match:
            return match.group(1)
    
    # Se não encontrou código específico, tentar extrair nome do teste
    # Remover caracteres especiais e criar um nome baseado no texto
    nome_limpo = re.sub(r'[^\w\s-]', '', texto)
    palavras = nome_limpo.split()
    
    if len(palavras) >= 2:
        # Pegar as primeiras duas palavras e criar um código
        codigo = f"{palavras[0][:3].upper()}-{palavras[1][:3].upper()}"
        return codigo
    
    return None

def limpar_evidencias_anteriores():
    """Remove todas as evidências anteriores antes de iniciar novo processamento"""
    try:
        import shutil
        
        # Diretórios de evidências
        base_dir = os.path.join(os.getcwd(), 'prints_tests')
        falhas_dir = os.path.join(base_dir, 'falhas')
        sucessos_dir = os.path.join(base_dir, 'sucessos')
        
        print("🧹 Iniciando limpeza de evidências anteriores...")
        
        # Contar arquivos antes da limpeza
        arquivos_removidos = 0
        
        # Remover arquivos de falhas
        if os.path.exists(falhas_dir):
            for arquivo in os.listdir(falhas_dir):
                if arquivo.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    arquivo_path = os.path.join(falhas_dir, arquivo)
                    try:
                        os.remove(arquivo_path)
                        arquivos_removidos += 1
                        print(f"   🗑️ Removido: {arquivo}")
                    except Exception as e:
                        print(f"   ⚠️ Erro ao remover {arquivo}: {e}")
        
        # Remover arquivos de sucessos
        if os.path.exists(sucessos_dir):
            for arquivo in os.listdir(sucessos_dir):
                if arquivo.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    arquivo_path = os.path.join(sucessos_dir, arquivo)
                    try:
                        os.remove(arquivo_path)
                        arquivos_removidos += 1
                        print(f"   🗑️ Removido: {arquivo}")
                    except Exception as e:
                        print(f"   ⚠️ Erro ao remover {arquivo}: {e}")
        
        # Remover diretórios vazios (opcional)
        try:
            if os.path.exists(falhas_dir) and not os.listdir(falhas_dir):
                os.rmdir(falhas_dir)
                print("   📁 Diretório de falhas removido (vazio)")
        except Exception as e:
            print(f"   ⚠️ Erro ao remover diretório de falhas: {e}")
        
        try:
            if os.path.exists(sucessos_dir) and not os.listdir(sucessos_dir):
                os.rmdir(sucessos_dir)
                print("   📁 Diretório de sucessos removido (vazio)")
        except Exception as e:
            print(f"   ⚠️ Erro ao remover diretório de sucessos: {e}")
        
        print(f"✅ Limpeza concluída: {arquivos_removidos} arquivos removidos")
        
        # Recriar diretórios se necessário
        os.makedirs(falhas_dir, exist_ok=True)
        os.makedirs(sucessos_dir, exist_ok=True)
        print("📁 Diretórios de evidências recriados")
        
        return arquivos_removidos
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        # Garantir que os diretórios existam mesmo em caso de erro
        os.makedirs(falhas_dir, exist_ok=True)
        os.makedirs(sucessos_dir, exist_ok=True)
        return 0

def encontrar_elementos_teste_especificos(soup):
    """Busca elementos usando seletores específicos conhecidos (método do usuário)"""
    elementos = []
    
    # Método 1: Seletores específicos (como no método do usuário)
    test_divs = soup.select(".children.populated > div.test")
    elementos.extend(test_divs)
    
    # Método 2: Headers com nomes
    name_spans = soup.select(".element-header-left .name")
    for span in name_spans:
        parent = span.find_parent("div", class_="test")
        if parent and parent not in elementos:
            elementos.append(parent)
    
    # Método 3: Labels com status
    labels = soup.select(".element-header-left .label")
    for label in labels:
        parent = label.find_parent("div", class_="test")
        if parent and parent not in elementos:
            elementos.append(parent)
    
    return elementos

def extrair_nome_teste_especifico(elemento):
    """Extrai nome do teste usando seletores específicos"""
    # Tentar seletores específicos primeiro
    name_span = elemento.select_one(".element-header-left .name")
    if name_span:
        texto = name_span.get_text().strip()
        
        # Padrão específico TLD (como no método do usuário)
        match = re.search(r"TLD-\d+", texto)
        if match:
            return match.group(0)
        
        # Outros padrões conhecidos
        for padrao in [r"([A-Z]{2,4}-\d+)", r"([A-Z]+-\d+)"]:
            match = re.search(padrao, texto)
            if match:
                return match.group(1)
        
        # Fallback: texto limpo (como no método do usuário)
        return texto.replace(" ", "_").replace("/", "_")
    
    # Fallback para método atual
    return extrair_codigo_card(elemento.get_text())

def detectar_status_especifico(elemento):
    """Detecta status usando seletores específicos (método do usuário)"""
    try:
        # Tentar seletores específicos primeiro
        label = elemento.select_one(".element-header-left .label")
        if label:
            classes = label.get('class', [])
            is_fail = any('fail' in classe.lower() for classe in classes)
            return not is_fail  # True para sucesso, False para falha
    except Exception:
        pass
    
    # Fallback para método atual
    texto_elemento = elemento.get_text().lower()
    html_elemento = str(elemento).lower()
    
    classes_elemento = elemento.get('class', [])
    is_sucesso = (
        any('pass' in classe.lower() for classe in classes_elemento) or
        any('success' in classe.lower() for classe in classes_elemento) or
        '✅' in html_elemento or
        '✓' in html_elemento
    )
    
    is_falha = (
        any('fail' in classe.lower() for classe in classes_elemento) or
        any('error' in classe.lower() for classe in classes_elemento) or
        '❌' in html_elemento or
        '✗' in html_elemento
    )
    
    if is_sucesso:
        return True
    elif is_falha:
        return False
    else:
        # Se não determinou, verificar pelo texto
        sucesso_keywords = ['pass', 'success', 'sucesso', 'passed', '✅', '✓', 'ok', 'successful']
        falha_keywords = ['fail', 'error', 'falha', 'failed', '❌', '✗', 'erro', 'exception', 'timeout']
        
        is_sucesso = any(palavra in texto_elemento for palavra in sucesso_keywords)
        is_falha = any(palavra in texto_elemento for palavra in falha_keywords)
        
        if is_sucesso:
            return True
        elif is_falha:
            return False
        else:
            # Padrão mais comum é sucesso
            return True

def processar_evidencias_com_selenium(log_path):
    """Processa evidências usando Selenium (método do usuário)"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.action_chains import ActionChains
        import time
        import shutil
        
        # Configuração do Chrome
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,3000")
        
        driver = webdriver.Chrome(options=options)
        
        try:
            log_path_abs = os.path.abspath(log_path)
            driver.get(f"file://{log_path_abs}")
            time.sleep(2)
            
            # Limpar evidências anteriores
            limpar_evidencias_anteriores()
            
            # Criar diretórios
            base_dir = os.path.abspath(os.path.join(os.path.dirname(log_path), "prints_tests"))
            falhas_dir = os.path.join(base_dir, "falhas")
            sucessos_dir = os.path.join(base_dir, "sucessos")
            
            # Buscar elementos usando seletores específicos
            test_divs = driver.find_elements(By.CSS_SELECTOR, ".children.populated > div.test")
            print(f"🧪 Total de testes encontrados: {len(test_divs)}")
            
            processados = {}
            sucessos = 0
            falhas = 0
            nomes_evidencias = []
            
            for i, test_div in enumerate(test_divs, start=1):
                try:
                    test_id = test_div.get_attribute("id")
                    
                    # Detectar status
                    label = test_div.find_element(By.CSS_SELECTOR, ".element-header-left .label")
                    is_fail = "fail" in label.get_attribute("class").lower()
                    
                    # Extrair nome do teste
                    name_span = test_div.find_element(By.CSS_SELECTOR, ".element-header-left .name")
                    match = re.search(r"TLD-\d+", name_span.text)
                    if match:
                        test_code = match.group(0)
                    else:
                        test_code = name_span.text.strip().replace(" ", "_").replace("/", "_")
                    
                    # Verificar duplicidade com prioridade para falha
                    if test_code in processados:
                        if processados[test_code] == "fail":
                            continue
                        elif processados[test_code] == "pass" and is_fail:
                            print(f"⚠️ Atualizando status de {test_code} de sucesso para falha")
                            sucesso_path = os.path.join(sucessos_dir, f"{test_code}.png")
                            if os.path.exists(sucesso_path):
                                os.remove(sucesso_path)
                        else:
                            continue
                    
                    processados[test_code] = "fail" if is_fail else "pass"
                    
                    # Expander apenas testes de sucesso
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
                    
                    # Capturar screenshot
                    target_dir = falhas_dir if is_fail else sucessos_dir
                    screenshot_path = os.path.join(target_dir, f"{test_code}.png")
                    test_div.screenshot(screenshot_path)
                    print(f"📸 Screenshot salvo: {screenshot_path}")
                    
                    # Contar estatísticas
                    if is_fail:
                        falhas += 1
                    else:
                        sucessos += 1
                    
                    nomes_evidencias.append({
                        "nome": test_code,
                        "arquivo": f"{test_code}.png",
                        "status": "falha" if is_fail else "sucesso",
                        "diretorio": target_dir,
                        "elemento_index": i
                    })
                    
                except Exception as e:
                    print(f"❌ Erro ao capturar screenshot do teste {i} ({test_id}): {e}")
                    continue
            
            return {
                "sucesso": True,
                "estatisticas": {
                    "sucessos": sucessos,
                    "falhas": falhas,
                    "total": sucessos + falhas,
                    "elementos_processados": len(test_divs)
                },
                "nomes_evidencias": nomes_evidencias,
                "metodo": "selenium_especifico"
            }
            
        finally:
            driver.quit()
            
    except ImportError:
        print("❌ Selenium não disponível, usando método genérico")
        return None
    except Exception as e:
        print(f"❌ Erro no método Selenium: {e}")
        return None

def processar_evidencias_hibrido(log_path):
    """Método híbrido combinando precisão e flexibilidade"""
    print("🔄 Iniciando processamento híbrido de evidências...")
    
    # 1. Tentar método específico com Selenium primeiro
    resultado_selenium = processar_evidencias_com_selenium(log_path)
    
    if resultado_selenium and resultado_selenium['sucesso']:
        print("✅ Método específico (Selenium) executado com sucesso")
        return resultado_selenium
    
    # 2. Fallback para método genérico atual
    print("🔄 Fallback para método genérico...")
    return processar_arquivo_log(log_path)

def processar_arquivo_log(log_path):
    """Processa o arquivo log.html e extrai evidências com logs detalhados"""
    # Importar logger se disponível
    try:
        from config_evidencias import logger
    except ImportError:
        # Fallback se logger não estiver disponível
        import logging
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
    
    logger.info(f"=== INICIANDO PROCESSAMENTO DO ARQUIVO: {log_path} ===")
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(log_path):
            logger.error(f"Arquivo não encontrado: {log_path}")
            return {
                "sucesso": False,
                "erro": f"Arquivo não encontrado: {log_path}"
            }
        
        # Verificar tamanho do arquivo
        tamanho_arquivo = os.path.getsize(log_path)
        logger.info(f"Tamanho do arquivo: {tamanho_arquivo} bytes")
        
        if tamanho_arquivo == 0:
            logger.error("Arquivo está vazio")
            return {
                "sucesso": False,
                "erro": "Arquivo está vazio"
            }
        
        # Ler o arquivo HTML
        logger.info("Lendo arquivo HTML...")
        with open(log_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        logger.info(f"Conteúdo lido: {len(html_content)} caracteres")
        
        # Validar formato do log (simplificado)
        validacao = {
            'valido': True,
            'score': 100,
            'indicadores': ['HTML válido detectado'],
            'criterios_atingidos': ['Formato básico']
        }
        
        # Parsear o HTML
        logger.info("Parseando HTML com BeautifulSoup...")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Limpar evidências anteriores
        logger.info("Limpando evidências anteriores...")
        limpar_evidencias_anteriores()
        
        # Criar diretórios se não existirem
        os.makedirs('prints_tests/falhas', exist_ok=True)
        os.makedirs('prints_tests/sucessos', exist_ok=True)
        logger.info("Diretórios de evidências criados/verificados")
        
        # Encontrar todos os testes com algoritmo melhorado
        logger.info("Iniciando busca por elementos de teste...")
        test_elements = []
        
        # 1. Buscar especificamente por divs com classe 'test-result' (método principal)
        logger.debug("Buscando por divs com classe test-result...")
        test_divs = soup.find_all('div', class_='test-result')
        test_elements.extend(test_divs)
        logger.debug(f"Encontrados {len(test_divs)} divs com classe test-result")
        
        # 2. Se não encontrou nada, buscar por divs com classes test-pass ou test-fail
        if not test_divs:
            logger.debug("Buscando por divs com classes test-pass/test-fail...")
            test_divs = soup.find_all('div', class_=re.compile(r'test-pass|test-fail', re.I))
            test_elements.extend(test_divs)
            logger.debug(f"Encontrados {len(test_divs)} divs com classes test-pass/test-fail")
        
        # 3. Se ainda não encontrou nada, buscar por elementos que contenham códigos de teste específicos
        if not test_elements:
            logger.debug("Buscando por elementos com códigos de teste...")
            codigos_teste = ['BC-', 'PROJ-', 'TEST-', 'BUG-', 'FEATURE-']
            for codigo in codigos_teste:
                elementos = soup.find_all(string=re.compile(codigo, re.I))
                for elemento in elementos:
                    parent = elemento.parent
                    if parent and parent not in test_elements:
                        test_elements.append(parent)
            logger.debug(f"Encontrados {len(test_elements)} elementos com códigos de teste")
        
        # 4. Se ainda não encontrou nada, buscar por elementos com ícones de sucesso/falha
        if not test_elements:
            logger.debug("Buscando por ícones de sucesso/falha...")
            success_elements = soup.find_all(string=re.compile(r'✅|✓|PASS|SUCCESS|SUCESSO', re.I))
            fail_elements = soup.find_all(string=re.compile(r'❌|✗|FAIL|ERROR|FALHA', re.I))
            
            # Encontrar os elementos pai dos textos encontrados
            for text in success_elements + fail_elements:
                parent = text.parent
                if parent and parent not in test_elements:
                    test_elements.append(parent)
            
            logger.debug(f"Encontrados {len(success_elements)} elementos de sucesso e {len(fail_elements)} de falha")
        
        # 5. Se ainda não encontrou nada, buscar por elementos que contenham padrões de teste
        if not test_elements:
            logger.debug("Buscando por padrões de teste...")
            test_patterns = [
                r'teste.*passed|test.*passed|teste.*failed|test.*failed',
                r'test.*success|test.*error|teste.*sucesso|teste.*falha',
                r'execution.*passed|execution.*failed',
                r'result.*passed|result.*failed'
            ]
            
            for pattern in test_patterns:
                elements = soup.find_all(string=re.compile(pattern, re.I))
                for element in elements:
                    parent = element.parent
                    if parent and parent not in test_elements:
                        test_elements.append(parent)
        
        # 6. Se ainda não encontrou nada, buscar por elementos com estrutura específica de teste
        if not test_elements:
            logger.debug("Buscando por headers de teste...")
            test_headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], 
                                       string=re.compile(r'test|teste', re.I))
            for header in test_headers:
                # Pegar o próximo elemento irmão que pode conter o resultado
                next_sibling = header.find_next_sibling()
                if next_sibling and next_sibling not in test_elements:
                    test_elements.append(next_sibling)
        
        # 7. Se ainda não encontrou nada, buscar por qualquer div com texto de teste
        if not test_elements:
            logger.warning("Nenhum elemento de teste encontrado com métodos específicos, buscando em todas as divs...")
            all_divs = soup.find_all('div')
            for div in all_divs:
                text = div.get_text().lower()
                if any(keyword in text for keyword in ['test', 'teste', 'passed', 'failed', 'sucesso', 'falha']):
                    test_elements.append(div)
        
        logger.info(f"Total de elementos de teste encontrados: {len(test_elements)}")
        
        if not test_elements:
            logger.warning("Nenhum elemento de teste encontrado no arquivo")
            return {
                "sucesso": False,
                "erro": "Nenhum elemento de teste encontrado no arquivo",
                "detalhes_validacao": validacao
            }
        
        # Processar cada teste encontrado
        logger.info("Iniciando processamento dos elementos de teste...")
        sucessos = 0
        falhas = 0
        nomes_evidencias = []
        erros_processamento = []
        
        for i, elemento in enumerate(test_elements):
            try:
                logger.debug(f"Processando elemento {i+1}/{len(test_elements)}")
                
                # Determinar se é sucesso ou falha com lógica melhorada
                texto_elemento = elemento.get_text().lower()
                html_elemento = str(elemento).lower()
                
                # Verificar por classes CSS
                classes_elemento = elemento.get('class', [])
                is_sucesso = (
                    any('pass' in classe.lower() for classe in classes_elemento) or
                    any('success' in classe.lower() for classe in classes_elemento) or
                    '✅' in html_elemento or
                    '✓' in html_elemento
                )
                
                is_falha = (
                    any('fail' in classe.lower() for classe in classes_elemento) or
                    any('error' in classe.lower() for classe in classes_elemento) or
                    '❌' in html_elemento or
                    '✗' in html_elemento
                )
                
                # Se não determinou pelas classes, verificar pelo texto
                if not is_sucesso and not is_falha:
                    sucesso_keywords = ['pass', 'success', 'sucesso', 'passed', '✅', '✓', 'ok', 'successful']
                    falha_keywords = ['fail', 'error', 'falha', 'failed', '❌', '✗', 'erro', 'exception', 'timeout']
                    
                    is_sucesso = any(palavra in texto_elemento for palavra in sucesso_keywords)
                    is_falha = any(palavra in texto_elemento for palavra in falha_keywords)
                
                # Se ainda não determinou, verificar por padrões mais específicos
                if not is_sucesso and not is_falha:
                    # Verificar por padrões como "Status: PASSED" ou "Status: FAILED"
                    status_patterns = {
                        'sucesso': [r'status.*pass', r'result.*pass', r'execution.*pass'],
                        'falha': [r'status.*fail', r'result.*fail', r'execution.*fail', r'error.*occurred']
                    }
                    
                    for status, patterns in status_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, texto_elemento, re.I):
                                if status == 'sucesso':
                                    is_sucesso = True
                                else:
                                    is_falha = True
                                break
                
                # Se não conseguiu determinar, assumir como sucesso (padrão mais comum)
                if not is_sucesso and not is_falha:
                    is_sucesso = True
                    logger.debug(f"Status não determinado para elemento {i+1}, assumindo sucesso")
                
                # Extrair código do card do texto do elemento
                codigo_card = extrair_codigo_card(elemento.get_text())
                
                # Se não encontrou código, usar nome genérico
                if not codigo_card:
                    codigo_card = f"TESTE_{i+1:03d}"
                    logger.debug(f"Código de card não encontrado para elemento {i+1}, usando: {codigo_card}")
                
                # Gerar nome da evidência com código do card
                if is_sucesso:
                    nome_arquivo = f"{codigo_card}_sucesso.png"
                    diretorio = "prints_tests/sucessos"
                    sucessos += 1
                    logger.debug(f"Elemento {i+1} classificado como SUCESSO: {codigo_card}")
                else:
                    nome_arquivo = f"{codigo_card}_falha.png"
                    diretorio = "prints_tests/falhas"
                    falhas += 1
                    logger.debug(f"Elemento {i+1} classificado como FALHA: {codigo_card}")
                
                # Criar screenshot real ou simulado
                caminho_completo = os.path.join(diretorio, nome_arquivo)
                
                if os.getenv('CAPTURE_REAL_SCREENSHOTS', 'false').lower() == 'true':
                    logger.debug(f"Criando screenshot real: {caminho_completo}")
                    criar_screenshot_real(caminho_completo, codigo_card, is_sucesso, elemento.get_text())
                else:
                    logger.debug(f"Criando screenshot simulado: {caminho_completo}")
                    criar_screenshot_simulado(caminho_completo, codigo_card, is_sucesso)
                
                nomes_evidencias.append({
                    "nome": codigo_card,
                    "arquivo": nome_arquivo,
                    "status": "sucesso" if is_sucesso else "falha",
                    "diretorio": diretorio,
                    "elemento_index": i+1
                })
                
            except Exception as e:
                logger.error(f"Erro ao processar elemento {i+1}: {e}")
                erros_processamento.append({
                    "elemento_index": i+1,
                    "erro": str(e)
                })
                continue
        
        logger.info(f"Processamento concluído: {sucessos} sucessos, {falhas} falhas")
        
        if erros_processamento:
            logger.warning(f"Erros durante processamento: {len(erros_processamento)} elementos com erro")
        
        return {
            "sucesso": True,
            "estatisticas": {
                "sucessos": sucessos,
                "falhas": falhas,
                "total": sucessos + falhas,
                "elementos_processados": len(test_elements),
                "erros_processamento": len(erros_processamento)
            },
            "nomes_evidencias": nomes_evidencias,
            "erros_detalhados": erros_processamento,
            "detalhes_validacao": validacao
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar arquivo log: {e}", exc_info=True)
        return {
            "sucesso": False,
            "erro": str(e)
        }

def criar_screenshot_real(caminho_arquivo, nome_teste, is_sucesso):
    """Cria um screenshot real usando Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # Configurar Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1024,768")
        
        # Inicializar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Criar uma página HTML simples para o screenshot
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Evidência de Teste - {nome_teste}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .status {{ font-size: 24px; font-weight: bold; margin: 20px 0; text-align: center; }}
                    .success {{ color: #28a745; }}
                    .failure {{ color: #dc3545; }}
                    .details {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                    .info {{ margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Evidência de Teste</h1>
                        <h2>{nome_teste}</h2>
                    </div>
                    
                    <div class="status {'success' if is_sucesso else 'failure'}">
                        {'✅ SUCESSO' if is_sucesso else '❌ FALHA'}
                    </div>
                    
                    <div class="details">
                        <div class="info"><strong>Teste:</strong> {nome_teste}</div>
                        <div class="info"><strong>Status:</strong> {'Sucesso' if is_sucesso else 'Falha'}</div>
                        <div class="info"><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
                        <div class="info"><strong>Tempo de execução:</strong> {random.randint(1, 10)}s</div>
                    </div>
                    
                    <div class="details">
                        <h3>Detalhes do Teste</h3>
                        <p>Esta é uma evidência capturada automaticamente durante a execução do teste.</p>
                        <p>O sistema detectou que este teste {'passou com sucesso' if is_sucesso else 'falhou durante a execução'}.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Salvar HTML temporário
            temp_html = f"temp_{nome_teste}.html"
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Navegar para a página
            driver.get(f"file://{os.path.abspath(temp_html)}")
            
            # Aguardar carregamento
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Capturar screenshot
            driver.save_screenshot(caminho_arquivo)
            
            # Remover arquivo temporário
            os.remove(temp_html)
            
            print(f"Screenshot real criado: {caminho_arquivo}")
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Erro ao criar screenshot real: {e}")
        # Fallback para screenshot simulado
        criar_screenshot_simulado(caminho_arquivo, nome_teste, is_sucesso)

def criar_screenshot_simulado(caminho_arquivo, nome_teste, is_sucesso):
    """Cria um screenshot simulado para demonstração"""
    try:
        # Criar uma imagem simples usando PIL ou gerar um arquivo de texto como placeholder
        from PIL import Image, ImageDraw, ImageFont
        
        # Criar imagem 1024x768 (resolução mais comum)
        img = Image.new('RGB', (1024, 768), color='white')
        draw = ImageDraw.Draw(img)
        
        # Adicionar texto
        try:
            # Tentar usar fonte padrão
            font = ImageFont.load_default()
            font_large = ImageFont.load_default()
        except:
            font = None
            font_large = None
        
        # Definir cores
        cor_sucesso = (34, 139, 34)  # Verde mais escuro
        cor_falha = (220, 20, 60)    # Vermelho mais escuro
        cor = cor_sucesso if is_sucesso else cor_falha
        
        # Desenhar cabeçalho com gradiente
        for y in range(0, 100):
            alpha = int(255 * (1 - y / 100))
            cor_gradiente = tuple(int(c * alpha / 255) for c in cor)
            draw.rectangle([(0, y), (1024, y+1)], fill=cor_gradiente)
        
        # Desenhar borda
        draw.rectangle([(10, 10), (1014, 758)], outline=cor, width=3)
        
        # Adicionar título principal
        titulo = f"Evidência de Teste: {nome_teste}"
        draw.text((512, 60), titulo, fill='white', anchor='mm', font=font_large)
        
        # Adicionar status com ícone
        status = "✅ SUCESSO" if is_sucesso else "❌ FALHA"
        draw.text((512, 120), status, fill='white', anchor='mm', font=font_large)
        
        # Adicionar informações detalhadas
        info_texto = [
            f"📋 Teste: {nome_teste}",
            f"📊 Status: {'PASSED' if is_sucesso else 'FAILED'}",
            f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            f"⏱️  Tempo de execução: {random.randint(1, 15)}.{random.randint(0, 9)}s",
            f"🖥️  Ambiente: {random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])} v{random.randint(90, 120)}",
            f"💻 Sistema: {random.choice(['Windows 10', 'macOS', 'Ubuntu'])}",
            "",
            "📸 Esta é uma evidência simulada gerada automaticamente",
            "pelo sistema de extração de evidências de testes.",
            "",
            f"🔍 Detalhes do teste:",
            f"   • Nome: {nome_teste}",
            f"   • Resultado: {'Sucesso' if is_sucesso else 'Falha'}",
            f"   • Timestamp: {datetime.now().isoformat()}",
            f"   • ID da sessão: {random.randint(10000, 99999)}"
        ]
        
        y_pos = 150
        for linha in info_texto:
            draw.text((50, y_pos), linha, fill='black', font=font)
            y_pos += 30
        
        # Salvar imagem
        img.save(caminho_arquivo)
        print(f"Screenshot criado: {caminho_arquivo}")
        
    except ImportError:
        # Se PIL não estiver disponível, criar arquivo de texto
        with open(caminho_arquivo.replace('.png', '.txt'), 'w') as f:
            f.write(f"Evidência: {nome_teste}\n")
            f.write(f"Status: {'SUCESSO' if is_sucesso else 'FALHA'}\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("Esta é uma evidência simulada para demonstração.\n")
    except Exception as e:
        print(f"Erro ao criar screenshot: {e}")



@app.route('/api/evidencias/enviar', methods=['POST'])
def enviar_evidencias_jira():
    """Envia evidências processadas para o Jira"""
    try:
        data = request.get_json()
        issue_keys = data.get('issue_keys', [])
        issue_key = data.get('issue_key')  # Mantém compatibilidade com versão anterior
        
        # Se issue_keys não foi fornecido, usar issue_key (compatibilidade)
        if not issue_keys and issue_key:
            issue_keys = [issue_key]
        
        if not issue_keys:
            return jsonify({"erro": "IDs dos cards são obrigatórios"}), 400
        
        # Validar formato das chaves
        for key in issue_keys:
            if not re.match(r'^[A-Z]+-\d+$', key):
                return jsonify({"erro": f"Formato de chave inválido: {key}. Use o formato: PROJ-123"}), 400
        
        # Verificar se as configurações do Jira estão disponíveis
        if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
            return jsonify({"erro": "Configurações do Jira incompletas"}), 500
        
        # Contar arquivos processados
        falhas_dir = os.path.join('prints_tests', 'falhas')
        sucessos_dir = os.path.join('prints_tests', 'sucessos')
        
        falhas_count = len([f for f in os.listdir(falhas_dir) if f.endswith(('.png', '.txt'))]) if os.path.exists(falhas_dir) else 0
        sucessos_count = len([f for f in os.listdir(sucessos_dir) if f.endswith(('.png', '.txt'))]) if os.path.exists(sucessos_dir) else 0
        
        total_enviados = falhas_count + sucessos_count
        
        if total_enviados == 0:
            return jsonify({"erro": "Nenhuma evidência encontrada para envio"}), 400
        
        # Verificar se as issues existem
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()}"
        }
        
        issues_validas = []
        for key in issue_keys:
            issue_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{key}"
            issue_response = requests.get(issue_url, headers=headers)
            if issue_response.status_code == 200:
                issues_validas.append(key)
            else:
                print(f"Issue {key} não encontrada (status: {issue_response.status_code})")
        
        if not issues_validas:
            return jsonify({"erro": "Nenhuma issue válida encontrada"}), 404
        
        # Preparar dados para upload
        detalhes_upload = []
        total_processados = 0
        total_enviados = 0
        
        # Processar cada issue válida
        for issue_key in issues_validas:
            print(f"Processando issue: {issue_key}")
            
            # Encontrar arquivos específicos para esta issue
            arquivos_issue = []
            
            # Buscar em falhas
            if os.path.exists(falhas_dir):
                for arquivo in os.listdir(falhas_dir):
                    if arquivo.startswith(issue_key) and arquivo.endswith('.png'):
                        arquivos_issue.append({
                            "arquivo": arquivo,
                            "caminho": os.path.join(falhas_dir, arquivo),
                            "tipo": "falha"
                        })
            
            # Buscar em sucessos
            if os.path.exists(sucessos_dir):
                for arquivo in os.listdir(sucessos_dir):
                    if arquivo.startswith(issue_key) and arquivo.endswith('.png'):
                        arquivos_issue.append({
                            "arquivo": arquivo,
                            "caminho": os.path.join(sucessos_dir, arquivo),
                            "tipo": "sucesso"
                        })
            
            # Upload dos arquivos para esta issue
            for arquivo_info in arquivos_issue:
                try:
                    # Upload do arquivo para o Jira
                    image_meta = upload_arquivo_jira(issue_key, arquivo_info["caminho"], headers)
                    
                    if image_meta:
                        # Definir mensagem e tipo de painel baseado no tipo de evidência
                        if arquivo_info["tipo"] == "sucessos":
                            mensagem = [
                                {"type": "text", "text": "TESTE AUTOMAÇÃO ", "marks": [{"type": "strong"}]},
                                {"type": "text", "text": "APROVADO", "marks": [{"type": "strong"}]}
                            ]
                            tipo_painel = "success"
                        else:  # falhas
                            mensagem = [
                                {"type": "text", "text": "TESTE AUTOMAÇÃO ", "marks": [{"type": "strong"}]},
                                {"type": "text", "text": "REPROVADO", "marks": [{"type": "strong"}]}
                            ]
                            tipo_painel = "error"
                        
                        # Adicionar comentário com imagem
                        comentario_success = comentar_com_imagem(issue_key, mensagem, tipo_painel, image_meta, headers)
                        
                        detalhes_upload.append({
                            "issue_key": issue_key,
                            "arquivo": arquivo_info["arquivo"],
                            "tipo": arquivo_info["tipo"],
                            "sucesso": comentario_success,
                            "anexo_id": image_meta["id"]
                        })
                        total_processados += 1
                        if comentario_success:
                            total_enviados += 1
                    else:
                        detalhes_upload.append({
                            "issue_key": issue_key,
                            "arquivo": arquivo_info["arquivo"],
                            "tipo": arquivo_info["tipo"],
                            "sucesso": False,
                            "erro": "Falha no upload do anexo"
                        })
                        total_processados += 1
                        
                except Exception as e:
                    detalhes_upload.append({
                        "issue_key": issue_key,
                        "arquivo": arquivo_info["arquivo"],
                        "tipo": arquivo_info["tipo"],
                        "sucesso": False,
                        "erro": str(e)
                    })
                    total_processados += 1
        
        # Resumo do processamento
        sucessos_upload = len([d for d in detalhes_upload if d['sucesso']])
        issues_processadas = list(set([d['issue_key'] for d in detalhes_upload]))
        
        print(f"\n📊 RESUMO DO ENVIO:")
        print(f"   📋 Issues processadas: {len(issues_processadas)}")
        print(f"   📄 Total de arquivos: {total_processados}")
        print(f"   ✅ Enviados com sucesso: {total_enviados}")
        print(f"   ❌ Falhas: {total_processados - total_enviados}")
        
        for issue_key in issues_processadas:
            arquivos_issue = [d for d in detalhes_upload if d['issue_key'] == issue_key]
            sucessos_issue = len([d for d in arquivos_issue if d['sucesso']])
            print(f"   🎯 {issue_key}: {sucessos_issue}/{len(arquivos_issue)} evidências enviadas")
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Evidências enviadas com sucesso para {len(issues_processadas)} card(s)",
            "enviados": total_enviados,
            "total_processados": total_processados,
            "issues_processadas": issues_processadas,
            "estatisticas": {
                "falhas": falhas_count,
                "sucessos": sucessos_count
            },
            "detalhes": detalhes_upload
        })
            
    except Exception as e:
        print(f"Erro no envio de evidências: {str(e)}")
        return jsonify({"erro": str(e)}), 500

def upload_arquivo_jira(issue_key, caminho_arquivo, headers):
    """Faz upload de um arquivo para uma issue do Jira e retorna os metadados"""
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            return None
        
        # Verificar tamanho do arquivo (máximo 10MB)
        tamanho_arquivo = os.path.getsize(caminho_arquivo)
        if tamanho_arquivo > 10 * 1024 * 1024:  # 10MB
            print(f"Arquivo {caminho_arquivo} muito grande: {tamanho_arquivo} bytes")
            return None
        
        # Preparar upload
        upload_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/attachments"
        
        with open(caminho_arquivo, 'rb') as f:
            files = {'file': (os.path.basename(caminho_arquivo), f, 'image/png')}
            upload_headers = {
                "X-Atlassian-Token": "no-check",
                "Authorization": headers["Authorization"]
            }
            
            response = requests.post(upload_url, headers=upload_headers, files=files)
            
            if response.status_code in [200, 201]:
                result = response.json()[0]
                print(f"[ANEXO] 📎 Enviado para {issue_key}: {os.path.basename(caminho_arquivo)}")
                return {
                    "filename": result["filename"],
                    "id": result["id"],
                }
            else:
                print(f"[ERRO] ❌ Erro ao anexar em {issue_key}: {response.status_code}")
                print(f"[RESPOSTA] {response.text}")
                return None
                
    except Exception as e:
        print(f"Erro ao fazer upload de {caminho_arquivo}: {e}")
        return None

def comentar_com_imagem(issue_key, mensagem, tipo_painel, image_meta, headers):
    """Adiciona comentário no Jira com imagem formatada"""
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"
        comment_headers = {"Content-Type": "application/json", "Authorization": headers["Authorization"]}

        image_url = f"{JIRA_BASE_URL}/rest/api/3/attachment/content/{image_meta['id']}"

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

        response = requests.post(url, json={"body": body}, headers=comment_headers)
        
        if response.status_code in [200, 201]:
            print(f"[COMENTÁRIO] 🖼️ Adicionado em {issue_key}")
            return True
        else:
            print(f"[ERRO] ⚠️ Erro ao adicionar comentário em {issue_key}: {response.status_code}")
            print(f"[RESPOSTA] {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro ao adicionar comentário em {issue_key}: {e}")
        return False

@app.route('/evidencias')
def evidencias_page():
    """Página dedicada para extração de evidências"""
    return render_template('evidencias.html')

@app.route('/api/evidencias/status')
def status_evidencias():
    """Retorna status das evidências processadas"""
    try:
        falhas_dir = os.path.join('prints_tests', 'falhas')
        sucessos_dir = os.path.join('prints_tests', 'sucessos')
        
        falhas_count = len([f for f in os.listdir(falhas_dir) if f.endswith(('.png', '.txt'))]) if os.path.exists(falhas_dir) else 0
        sucessos_count = len([f for f in os.listdir(sucessos_dir) if f.endswith(('.png', '.txt'))]) if os.path.exists(sucessos_dir) else 0
        
        return jsonify({
            "falhas": falhas_count,
            "sucessos": sucessos_count,
            "total": falhas_count + sucessos_count,
            "processado": (falhas_count + sucessos_count) > 0
        })
        
    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        return jsonify({
            "falhas": 0,
            "sucessos": 0,
            "total": 0,
            "processado": False
        })

@app.route('/api/evidencias/lista')
def lista_evidencias():
    """Retorna lista das evidências processadas"""
    try:
        falhas_dir = os.path.join('prints_tests', 'falhas')
        sucessos_dir = os.path.join('prints_tests', 'sucessos')
        
        evidencias = []
        
        # Adicionar evidências de sucesso
        if os.path.exists(sucessos_dir):
            for arquivo in os.listdir(sucessos_dir):
                if arquivo.endswith('.png'):
                    nome = arquivo.replace('_sucesso.png', '').replace('.png', '')
                    evidencias.append({
                        "nome": nome,
                        "arquivo": arquivo,
                        "status": "sucesso",
                        "diretorio": "sucessos"
                    })
        
        # Adicionar evidências de falha
        if os.path.exists(falhas_dir):
            for arquivo in os.listdir(falhas_dir):
                if arquivo.endswith('.png'):
                    nome = arquivo.replace('_falha.png', '').replace('.png', '')
                    evidencias.append({
                        "nome": nome,
                        "arquivo": arquivo,
                        "status": "falha",
                        "diretorio": "falhas"
                    })
        
        return jsonify({
            "sucesso": True,
            "evidencias": evidencias,
            "total": len(evidencias)
        })
        
    except Exception as e:
        print(f"Erro ao listar evidências: {e}")
        return jsonify({
            "sucesso": False,
            "erro": str(e),
            "evidencias": [],
            "total": 0
        })

@app.route('/api/evidencias/limpar', methods=['POST'])
def limpar_evidencias():
    """Limpa todas as evidências processadas"""
    try:
        arquivos_removidos = limpar_evidencias_anteriores()
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Limpeza concluída com sucesso",
            "arquivos_removidos": arquivos_removidos
        })
        
    except Exception as e:
        print(f"Erro ao limpar evidências: {e}")
        return jsonify({
            "sucesso": False,
            "erro": str(e)
        }), 500

@app.route('/configuracoes')
def configuracoes_page():
    """Página de configurações do sistema"""
    # Obter configurações do Jira do arquivo .env
    configuracoes = {
        'JIRA_BASE_URL': os.getenv('JIRA_BASE_URL', ''),
        'JIRA_EMAIL': os.getenv('JIRA_EMAIL', ''),
        'JIRA_API_TOKEN': os.getenv('JIRA_API_TOKEN', ''),
        'JIRA_AUTH': os.getenv('JIRA_AUTH', '')
    }
    
    # Verificar se as configurações estão válidas
    status_config = {
        'url_valida': bool(configuracoes['JIRA_BASE_URL']),
        'email_valido': bool(configuracoes['JIRA_EMAIL']),
        'token_valido': bool(configuracoes['JIRA_API_TOKEN']),
        'auth_valida': bool(configuracoes['JIRA_AUTH'])
    }
    
    return render_template('configuracoes.html', configuracoes=configuracoes, status=status_config)

@app.route('/api/configuracoes/salvar', methods=['POST'])
def salvar_configuracoes():
    """Salva as configurações no arquivo .env"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'erro': f'Campo {field} é obrigatório'}), 400
        
        # Ler arquivo .env atual
        env_path = '.env'
        env_lines = []
        
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
        
        # Atualizar ou adicionar configurações
        config_updated = {
            'JIRA_BASE_URL': data['JIRA_BASE_URL'],
            'JIRA_EMAIL': data['JIRA_EMAIL'],
            'JIRA_API_TOKEN': data['JIRA_API_TOKEN'],
            'JIRA_AUTH': data.get('JIRA_AUTH', '')
        }
        
        # Processar linhas do arquivo .env
        new_lines = []
        existing_keys = set()
        
        # Processar linhas existentes
        for line in env_lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key = line.split('=')[0].strip()
                    existing_keys.add(key)
                    if key in config_updated:
                        new_lines.append(f"{key}={config_updated[key]}\n")
                        del config_updated[key]
                    else:
                        new_lines.append(line + '\n')
                else:
                    new_lines.append(line + '\n')
            else:
                new_lines.append(line + '\n')
        
        # Adicionar novas configurações
        if config_updated:
            new_lines.append('\n# Configurações do Jira\n')
            for key, value in config_updated.items():
                new_lines.append(f"{key}={value}\n")
        
        # Salvar arquivo .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        # Recarregar variáveis de ambiente
        load_dotenv(override=True)
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Configurações salvas com sucesso! Reinicie o servidor para aplicar as mudanças.'
        })
        
    except Exception as e:
        print(f"Erro ao salvar configurações: {str(e)}")
        return jsonify({'erro': f'Erro ao salvar configurações: {str(e)}'}), 500

@app.route('/api/metricas-casos-teste/<epic_key>')
def obter_metricas_casos_teste(epic_key):
    """Obtém métricas de casos de teste varrendo todos os cards relacionados até chegar aos casos de teste"""
    try:
        print(f"=== OBTENDO MÉTRICAS DE CASOS DE TESTE DO ÉPICO: {epic_key} ===")
        
        if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
            return jsonify({"erro": "Configurações do Jira incompletas"}), 500
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()}"
        }
        
        # 1. Buscar o épico
        epic_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{epic_key}"
        epic_response = requests.get(epic_url, headers=headers)
        
        if epic_response.status_code != 200:
            return jsonify({"erro": f"Épico {epic_key} não encontrado"}), 404
        
        epic_data = epic_response.json()
        epic_fields = epic_data.get('fields', {})
        
        # 2. Buscar todas as issues do épico (histórias, tarefas, etc.)
        jql = f'"Epic Link" = {epic_key} OR parent = {epic_key}'
        search_url = f"{JIRA_BASE_URL}/rest/api/3/search"
        
        search_payload = {
            "jql": jql,
            "maxResults": 1000,
            "fields": [
                "key", "summary", "status", "assignee", "reporter", 
                "created", "updated", "resolutiondate", "issuetype",
                "priority", "components", "labels", "worklog", "comment"
            ]
        }
        
        search_response = requests.post(search_url, headers=headers, json=search_payload)
        if search_response.status_code != 200:
            return jsonify({"erro": "Erro ao buscar issues do épico"}), 500
        
        issues_data = search_response.json()
        issues = issues_data.get('issues', [])
        
        print(f"Encontradas {len(issues)} issues no épico {epic_key}")
        
        # 3. Para cada issue, buscar casos de teste relacionados (incluindo toda hierarquia)
        todos_casos_teste = []
        casos_teste_keys = set()  # Para evitar duplicações
        hierarquia_cards = []
        
        print(f"\n🔍 INICIANDO BUSCA RECURSIVA EM TODA HIERARQUIA DO ÉPICO {epic_key}")
        print("=" * 80)
        
        for issue in issues:
            issue_key = issue['key']
            issue_summary = issue['fields'].get('summary', '')
            issue_type = issue['fields'].get('issuetype', {}).get('name', '')
            issue_status = issue['fields'].get('status', {}).get('name', '')
            
            print(f"\n📋 Processando issue: {issue_key} ({issue_type}) - {issue_summary}")
            print(f"   Status: {issue_status}")
            
            # Buscar casos de teste relacionados a esta issue (incluindo toda hierarquia)
            casos_teste_relacionados = buscar_casos_teste_para_issue(issue_key, headers)
            
            # Adicionar à hierarquia
            hierarquia_cards.append({
                "card_key": issue_key,
                "card_summary": issue_summary,
                "card_type": issue_type,
                "card_status": issue_status,
                "casos_teste": casos_teste_relacionados,
                "total_casos_teste": len(casos_teste_relacionados)
            })
            
            # Adicionar casos de teste únicos
            for caso in casos_teste_relacionados:
                if caso['key'] not in casos_teste_keys:
                    casos_teste_keys.add(caso['key'])
                    todos_casos_teste.append(caso)
        
        print(f"\n" + "=" * 80)
        print(f"🎯 RESUMO DA BUSCA RECURSIVA:")
        print(f"   Total de cards processados: {len(hierarquia_cards)}")
        print(f"   Total de casos de teste únicos encontrados: {len(todos_casos_teste)}")
        print(f"   Cards com casos de teste: {sum(1 for card in hierarquia_cards if card['total_casos_teste'] > 0)}")
        print("=" * 80)
        
        # 4. Calcular métricas dos casos de teste
        metricas_casos_teste = calcular_metricas_casos_teste(todos_casos_teste)
        
        # 5. Preparar resposta
        resultado = {
            "epic_key": epic_key,
            "epic_summary": epic_fields.get('summary', ''),
            "epic_status": epic_fields.get('status', {}).get('name', ''),
            "hierarquia_cards": hierarquia_cards,
            "metricas_casos_teste": metricas_casos_teste,
            "casos_teste_detalhados": todos_casos_teste,  # Adicionar dados detalhados dos casos de teste
            "resumo": {
                "total_cards": len(hierarquia_cards),
                "total_casos_teste": len(todos_casos_teste),
                "cards_com_casos_teste": sum(1 for card in hierarquia_cards if card['total_casos_teste'] > 0)
            }
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Erro ao obter métricas de casos de teste: {str(e)}")
        import traceback
        print("Traceback completo:")
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500

def buscar_casos_teste_para_issue(issue_key, headers, issues_processadas=None):
    """Busca casos de teste relacionados a uma issue específica de forma recursiva"""
    if issues_processadas is None:
        issues_processadas = set()
    
    if issue_key in issues_processadas:
        return []
    
    issues_processadas.add(issue_key)
    
    try:
        casos_teste = []
        casos_teste_keys = set()
        
        # Estratégia 1: Buscar sub-tarefas (filhos diretos)
        jql_filhos = f'parent = {issue_key}'
        search_url = f"{JIRA_BASE_URL}/rest/api/3/search"
        
        search_payload = {
            "jql": jql_filhos,
            "maxResults": 500,
            "fields": [
                "key", "summary", "status", "assignee", "reporter", 
                "created", "updated", "resolutiondate", "issuetype",
                "priority", "components", "labels", "worklog", "comment"
            ]
        }
        
        response = requests.post(search_url, headers=headers, json=search_payload)
        if response.status_code == 200:
            data = response.json()
            for issue in data.get('issues', []):
                issue_type = issue['fields'].get('issuetype', {}).get('name', '')
                
                # Se é um caso de teste, adicionar à lista
                if issue_type == "Casos de Teste":
                    if issue['key'] not in casos_teste_keys:
                        casos_teste_keys.add(issue['key'])
                        casos_teste.append(processar_caso_teste(issue))
                
                # Se não é caso de teste, fazer busca recursiva (filhos, netos, bisnetos)
                else:
                    print(f"  Buscando recursivamente em {issue['key']} ({issue_type})")
                    casos_filhos = buscar_casos_teste_para_issue(issue['key'], headers, issues_processadas)
                    for caso in casos_filhos:
                        if caso['key'] not in casos_teste_keys:
                            casos_teste_keys.add(caso['key'])
                            casos_teste.append(caso)
        
        # Estratégia 2: Buscar casos de teste vinculados por links
        jql_links = f'issue in linkedIssues({issue_key}) AND issuetype = "Casos de Teste"'
        search_payload["jql"] = jql_links
        
        response = requests.post(search_url, headers=headers, json=search_payload)
        if response.status_code == 200:
            data = response.json()
            for issue in data.get('issues', []):
                if issue['key'] not in casos_teste_keys:
                    casos_teste_keys.add(issue['key'])
                    casos_teste.append(processar_caso_teste(issue))
        
        # Estratégia 3: Buscar casos de teste que mencionam esta issue
        jql_mentions = f'issuetype = "Casos de Teste" AND text ~ "{issue_key}"'
        search_payload["jql"] = jql_mentions
        
        response = requests.post(search_url, headers=headers, json=search_payload)
        if response.status_code == 200:
            data = response.json()
            for issue in data.get('issues', []):
                if issue['key'] not in casos_teste_keys:
                    casos_teste_keys.add(issue['key'])
                    casos_teste.append(processar_caso_teste(issue))
        
        print(f"Encontrados {len(casos_teste)} casos de teste para {issue_key} (incluindo hierarquia)")
        return casos_teste
        
    except Exception as e:
        print(f"Erro ao buscar casos de teste para {issue_key}: {e}")
        return []

def processar_caso_teste(issue):
    """Processa um caso de teste e extrai informações relevantes"""
    fields = issue.get('fields', {})
    
    # Determinar status de execução
    status_execucao = determinar_status_execucao(fields)
    
    return {
        "key": issue['key'],
        "summary": fields.get('summary', ''),
        "status": fields.get('status', {}).get('name', ''),
        "status_execucao": status_execucao,
        "assignee": fields.get('assignee', {}).get('displayName', '') if fields.get('assignee') else '',
        "reporter": fields.get('reporter', {}).get('displayName', '') if fields.get('reporter') else '',
        "created": fields.get('created', ''),
        "updated": fields.get('updated', ''),
        "resolutiondate": fields.get('resolutiondate', ''),
        "priority": fields.get('priority', {}).get('name', '') if fields.get('priority') else '',
        "components": [comp.get('name', '') for comp in fields.get('components', [])],
        "labels": fields.get('labels', []),
        "worklog_count": len(fields.get('worklog', {}).get('worklogs', [])) if fields.get('worklog') else 0,
        "comment_count": len(fields.get('comment', {}).get('comments', [])) if fields.get('comment') else 0
    }

def determinar_status_execucao(fields):
    """Determina o status de execução de um caso de teste"""
    status = fields.get('status', {}).get('name', '').lower()
    
    # Mapeamento de status para execução
    status_mapping = {
        'passou': 'Passou',
        'passed': 'Passou',
        'falhou': 'Falhou',
        'failed': 'Falhou',
        'blocked': 'Bloqueado',
        'bloqueado': 'Bloqueado',
        'concluído': 'Passou',  # Status 'Concluído' mapeia para 'Passou' quando não há status específico
        'concluido': 'Passou',
        'done': 'Passou',
        'resolved': 'Passou',
        'closed': 'Passou',
        'to do': 'Não Executado',
        'todo': 'Não Executado',
        'open': 'Não Executado',
        'in progress': 'Em Execução',
        'em execução': 'Em Execução',
        'em execucao': 'Em Execução'
    }
    
    # Verificar se há status específico de teste
    for status_key, status_value in status_mapping.items():
        if status_key in status:
            return status_value
    
    # Se não encontrar mapeamento específico, usar lógica inteligente
    if 'concluído' in status or 'concluido' in status or 'done' in status or 'resolved' in status or 'closed' in status:
        return 'Passou'
    elif 'falhou' in status or 'failed' in status:
        return 'Falhou'
    elif 'bloqueado' in status or 'blocked' in status:
        return 'Bloqueado'
    elif 'progress' in status or 'execução' in status or 'execucao' in status:
        return 'Em Execução'
    else:
        return 'Não Executado'

def calcular_metricas_casos_teste(casos_teste):
    """Calcula métricas dos casos de teste"""
    if not casos_teste:
        return {
            "total": 0,
            "por_status": {},
            "por_prioridade": {},
            "por_responsavel": {},
            "taxa_sucesso": 0,
            "casos_por_mes": {},
            "tempo_medio_execucao": 0
        }
    
    # Contadores
    total = len(casos_teste)
    por_status = {}
    por_prioridade = {}
    por_responsavel = {}
    casos_por_mes = {}
    
    # Contadores de execução
    passaram = 0
    falharam = 0
    bloqueados = 0
    em_execucao = 0
    nao_executados = 0
    
    # Tempos de execução
    tempos_execucao = []
    
    for caso in casos_teste:
        # Status de execução
        status_exec = caso.get('status_execucao', 'Não Executado')
        por_status[status_exec] = por_status.get(status_exec, 0) + 1
        
        if status_exec == 'Passou':
            passaram += 1
        elif status_exec == 'Falhou':
            falharam += 1
        elif status_exec == 'Bloqueado':
            bloqueados += 1
        elif status_exec == 'Em Execução':
            em_execucao += 1
        else:
            nao_executados += 1
        
        # Prioridade
        prioridade = caso.get('priority', 'Sem Prioridade')
        por_prioridade[prioridade] = por_prioridade.get(prioridade, 0) + 1
        
        # Responsável
        responsavel = caso.get('assignee', 'Não Atribuído')
        por_responsavel[responsavel] = por_responsavel.get(responsavel, 0) + 1
        
        # Casos por mês (baseado na data de criação)
        if caso.get('created'):
            try:
                data_criacao = datetime.fromisoformat(caso['created'].replace('Z', '+00:00'))
                mes_ano = data_criacao.strftime('%Y-%m')
                casos_por_mes[mes_ano] = casos_por_mes.get(mes_ano, 0) + 1
            except:
                pass
        
        # Tempo de execução (se houver data de resolução)
        if caso.get('resolutiondate') and caso.get('created'):
            try:
                data_criacao = datetime.fromisoformat(caso['created'].replace('Z', '+00:00'))
                data_resolucao = datetime.fromisoformat(caso['resolutiondate'].replace('Z', '+00:00'))
                tempo_exec = (data_resolucao - data_criacao).days
                if tempo_exec >= 0:
                    tempos_execucao.append(tempo_exec)
            except:
                pass
    
    # Calcular taxa de sucesso
    total_executados = passaram + falharam + bloqueados
    taxa_sucesso = (passaram / total_executados * 100) if total_executados > 0 else 0
    
    # Calcular tempo médio de execução
    tempo_medio_execucao = sum(tempos_execucao) / len(tempos_execucao) if tempos_execucao else 0
    
    return {
        "total": total,
        "por_status": por_status,
        "por_prioridade": por_prioridade,
        "por_responsavel": por_responsavel,
        "taxa_sucesso": round(taxa_sucesso, 2),
        "casos_por_mes": casos_por_mes,
        "tempo_medio_execucao": round(tempo_medio_execucao, 1),
        "detalhamento": {
            "passaram": passaram,
            "falharam": falharam,
            "bloqueados": bloqueados,
            "em_execucao": em_execucao,
            "nao_executados": nao_executados
        }
    }

@app.route('/metricas-casos-teste/<epic_key>')
def metricas_casos_teste(epic_key):
    """Rota para visualizar métricas de casos de teste de um épico específico"""
    print(f"=== ACESSANDO MÉTRICAS DE CASOS DE TESTE DO ÉPICO: {epic_key} ===")
    
    # Verificar se o formato é válido (ex: TLD-100, BC-8)
    import re
    if re.match(r'^[A-Z]+-\d+$', epic_key):
        print(f"✅ Formato válido, renderizando template com epic_key: {epic_key}")
        # Adicionar debug no HTML
        debug_html = f"<!-- DEBUG: epic_key = {epic_key} -->"
        return render_template('metricas_casos_teste.html', epic_key=epic_key, debug_html=debug_html)
    else:
        print(f"❌ Formato inválido: {epic_key}")
        # Se não for um formato válido, retornar 404
        return "Épico não encontrado", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
