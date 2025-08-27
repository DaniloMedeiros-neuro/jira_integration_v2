from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pandas as pd
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import re
from urllib.parse import urlparse, parse_qs
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
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
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
    """Busca issues similares para sugerir correção de digitação"""
    try:
        # Extrair prefixo e número da issue
        if '-' in issue_key:
            prefixo, numero = issue_key.split('-', 1)
        else:
            return []
        
        # Buscar issues com o mesmo prefixo
        jql = f'project = {prefixo} AND issuekey LIKE "{prefixo}-%" ORDER BY created DESC'
        url = f"{JIRA_BASE_URL}/rest/api/3/search"
        
        payload = {
            "jql": jql,
            "maxResults": 10,
            "fields": ["key", "summary"]
        }
        
        response = requests.post(url, headers=HEADERS, json=payload, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 200:
            data = response.json()
            issues = data.get('issues', [])
            
            # Filtrar issues mais similares (mesmo número ou próximo)
            sugestoes = []
            for issue in issues:
                issue_key_found = issue['key']
                if issue_key_found != issue_key:  # Não sugerir a mesma issue
                    sugestoes.append(issue_key_found)
            
            return sugestoes[:5]  # Retornar até 5 sugestões
        
        return []
        
    except Exception as e:
        print(f"Erro ao buscar issues similares: {e}")
        return []

def obter_tipos_issue_disponiveis(project_key):
    """Obtém todos os tipos de issue disponíveis no projeto"""
    try:
        # Primeira tentativa: obter metadados completos do projeto
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/createmeta?projectKeys={project_key}"
        response = requests.get(url, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 200:
            data = response.json()
            tipos_disponiveis = []
            subtarefas = []
            issues_normais = []
            
            if 'projects' in data and data['projects']:
                project = data['projects'][0]
                if 'issuetypes' in project:
                    for issue_type in project['issuetypes']:
                        nome = issue_type['name']
                        eh_subtarefa = issue_type.get('subtask', False)
                        
                        tipos_disponiveis.append(nome)
                        if eh_subtarefa:
                            subtarefas.append(nome)
                        else:
                            issues_normais.append(nome)
                        
                        print(f"Tipo disponível: {nome} (subtarefa: {eh_subtarefa})")
            
            print(f"Subtarefas encontradas: {subtarefas}")
            print(f"Issues normais encontradas: {issues_normais}")
            return tipos_disponiveis, subtarefas, issues_normais
        else:
            print(f"Erro ao obter tipos de issue: {response.status_code} - {response.text}")
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

@app.route('/<requisito_id>')
def requisito_direto(requisito_id):
    """Rota para acessar diretamente um requisito via URL"""
    # Verificar se o formato é válido (ex: CREDT-1161)
    import re
    if re.match(r'^[A-Z]+-\d+$', requisito_id):
        return render_template('index.html')
    else:
        # Se não for um formato válido, retornar 404
        return "Página não encontrada", 404

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

@app.route('/teste-epic/<epic_key>')
def teste_epic(epic_key):
    """Rota de teste para verificar se o parâmetro está sendo passado"""
    print(f"=== TESTE EPIC: {epic_key} ===")
    debug_html = f"<!-- DEBUG: epic_key = {epic_key} -->"
    return render_template('teste_epic.html', epic_key=epic_key, debug_html=debug_html)

@app.route('/metricas/<epic_key>')
def metricas_epico_direto(epic_key):
    """Rota para acessar diretamente a análise de um épico via URL"""
    print(f"=== ACESSANDO MÉTRICAS DO ÉPICO: {epic_key} ===")
    
    # Verificar se o formato é válido (ex: TLD-100, BC-8)
    import re
    if re.match(r'^[A-Z]+-\d+$', epic_key):
        print(f"✅ Formato válido, renderizando template com epic_key: {epic_key}")
        # Adicionar debug no HTML
        debug_html = f"<!-- DEBUG: epic_key = {epic_key} -->"
        return render_template('metricas.html', epic_key=epic_key, debug_html=debug_html)
    else:
        print(f"❌ Formato inválido: {epic_key}")
        # Se não for um formato válido, retornar 404
        return "Épico não encontrado", 404

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
            "status": fields.get('status', {}).get('name', 'To Do'),
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
        
        if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
            print("Erro: Configurações do Jira incompletas")
            return jsonify({"erro": "Configurações do Jira incompletas. Verifique as variáveis de ambiente."}), 500
        
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
        todos_tipos, subtarefas, issues_normais = obter_tipos_issue_disponiveis(project_key)
        
        # SEMPRE criar como "Caso de Teste" (não como subtarefa)
        tipo_caso_teste = "Caso de Teste"
        eh_subtarefa = False
        
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

@app.route('/api/caso-teste/<issue_key>', methods=['DELETE'])
def excluir_caso_teste(issue_key):
    """Exclui um caso de teste"""
    try:
        url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
        response = requests.delete(url, headers=HEADERS, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        
        if response.status_code == 204:
            return jsonify({
                "sucesso": True,
                "mensagem": f"Caso de teste {issue_key} excluído com sucesso"
            })
        else:
            return jsonify({"erro": f"Erro ao excluir caso de teste: {response.status_code}", "detalhes": response.text}), 500
            
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
                
                if 'pre_condicoes' in campos_alterados:
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

@app.route('/api/metricas-sprint/<sprint_id>')
def obter_metricas_sprint(sprint_id):
    """Obtém métricas de uma sprint específica"""
    try:
        print(f"=== OBTENDO MÉTRICAS DA SPRINT: {sprint_id} ===")
        
        if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
            return jsonify({"erro": "Configurações do Jira incompletas"}), 500
        
        # Buscar informações da sprint
        sprint_url = f"{JIRA_BASE_URL}/rest/agile/1.0/sprint/{sprint_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()}"
        }
        
        sprint_response = requests.get(sprint_url, headers=headers)
        if sprint_response.status_code != 200:
            return jsonify({"erro": f"Sprint {sprint_id} não encontrada"}), 404
        
        sprint_data = sprint_response.json()
        
        # Buscar issues da sprint
        issues_url = f"{JIRA_BASE_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
        issues_response = requests.get(issues_url, headers=headers)
        
        if issues_response.status_code != 200:
            return jsonify({"erro": "Erro ao buscar issues da sprint"}), 500
        
        issues_data = issues_response.json()
        issues = issues_data.get('issues', [])
        
        # Calcular métricas da sprint
        metricas = calcular_metricas_sprint(sprint_data, issues)
        
        return jsonify(metricas)
        
    except Exception as e:
        print(f"Erro ao obter métricas da sprint: {str(e)}")
        return jsonify({"erro": str(e)}), 500

def calcular_metricas_sprint(sprint_data, issues):
    """Calcula métricas de uma sprint"""
    
    total_issues = len(issues)
    issues_concluidas = sum(1 for issue in issues if issue['fields'].get('status', {}).get('name') in ['Done', 'Resolved', 'Closed'])
    
    # Story points
    story_points_total = sum(issue['fields'].get('storypoints', 0) or 0 for issue in issues)
    story_points_concluidos = sum(
        issue['fields'].get('storypoints', 0) or 0 
        for issue in issues 
        if issue['fields'].get('status', {}).get('name') in ['Done', 'Resolved', 'Closed']
    )
    
    # Velocidade
    velocity = story_points_concluidos
    
    # Burndown data
    burndown_data = []
    for issue in issues:
        if issue['fields'].get('status', {}).get('name') in ['Done', 'Resolved', 'Closed']:
            resolved_date = issue['fields'].get('resolutiondate')
            if resolved_date:
                burndown_data.append({
                    'date': resolved_date,
                    'story_points': issue['fields'].get('storypoints', 0) or 0
                })
    
    return {
        "sprint_info": {
            "id": sprint_data.get('id'),
            "name": sprint_data.get('name'),
            "state": sprint_data.get('state'),
            "startDate": sprint_data.get('startDate'),
            "endDate": sprint_data.get('endDate'),
            "goal": sprint_data.get('goal')
        },
        "metricas": {
            "total_issues": total_issues,
            "issues_concluidas": issues_concluidas,
            "issues_pendentes": total_issues - issues_concluidas,
            "story_points_total": story_points_total,
            "story_points_concluidos": story_points_concluidos,
            "velocity": velocity,
            "percentual_conclusao": round((issues_concluidas / total_issues * 100), 2) if total_issues > 0 else 0
        },
        "burndown_data": burndown_data
    }

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
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{JIRA_API_TOKEN}'.encode()).decode()}"
        }
        
        for issue in issues:
            # Buscar casos de teste relacionados
            issue_key = issue['key']
            test_cases_jql = f'issue in linkedIssues({issue_key}) AND issuetype = "Test"'
            test_search_url = f"{JIRA_BASE_URL}/rest/api/3/search"
            
            test_payload = {
                "jql": test_cases_jql,
                "maxResults": 50,
                "fields": ["key", "summary", "status", "assignee", "customfield_10016"]  # customfield_10016 é o status do teste
            }
            
            try:
                test_response = requests.post(test_search_url, headers=headers, json=test_payload)
                if test_response.status_code == 200:
                    test_data = test_response.json()
                    for test_case in test_data.get('issues', []):
                        casos_teste.append({
                            'key': test_case['key'],
                            'summary': test_case['fields'].get('summary', ''),
                            'status': test_case['fields'].get('status', {}).get('name', ''),
                            'test_status': test_case['fields'].get('customfield_10016', {}).get('value', 'Não Executado'),
                            'assignee': test_case['fields'].get('assignee', {}).get('displayName', 'Não atribuído') if test_case['fields'].get('assignee') else 'Não atribuído',
                            'ultima_execucao': 'N/A'  # Seria necessário buscar no histórico
                        })
            except Exception as e:
                print(f"Erro ao buscar casos de teste para {issue_key}: {e}")
        
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
        
        # Executar script de extração de prints
        import subprocess
        import sys
        
        try:
            result = subprocess.run([sys.executable, 'extrair_prints.py'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                # Contar arquivos gerados
                falhas_dir = os.path.join('prints_tests', 'falhas')
                sucessos_dir = os.path.join('prints_tests', 'sucessos')
                
                falhas_count = len([f for f in os.listdir(falhas_dir) if f.endswith('.png')]) if os.path.exists(falhas_dir) else 0
                sucessos_count = len([f for f in os.listdir(sucessos_dir) if f.endswith('.png')]) if os.path.exists(sucessos_dir) else 0
                
                return jsonify({
                    "sucesso": True,
                    "mensagem": "Evidências processadas com sucesso",
                    "estatisticas": {
                        "falhas": falhas_count,
                        "sucessos": sucessos_count,
                        "total": falhas_count + sucessos_count
                    }
                })
            else:
                return jsonify({"erro": f"Erro no processamento: {result.stderr}"}), 500
                
        except Exception as e:
            return jsonify({"erro": f"Erro ao executar script: {str(e)}"}), 500
            
    except Exception as e:
        print(f"Erro no upload de evidências: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route('/api/evidencias/enviar', methods=['POST'])
def enviar_evidencias_jira():
    """Envia evidências processadas para o Jira"""
    try:
        # Executar script de envio de evidências
        import subprocess
        import sys
        
        try:
            result = subprocess.run([sys.executable, 'adicionar_evidencias.py'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                # Contar arquivos enviados (simulação)
                falhas_dir = os.path.join('prints_tests', 'falhas')
                sucessos_dir = os.path.join('prints_tests', 'sucessos')
                
                falhas_count = len([f for f in os.listdir(falhas_dir) if f.endswith('.png')]) if os.path.exists(falhas_dir) else 0
                sucessos_count = len([f for f in os.listdir(sucessos_dir) if f.endswith('.png')]) if os.path.exists(sucessos_dir) else 0
                
                return jsonify({
                    "sucesso": True,
                    "mensagem": "Evidências enviadas com sucesso",
                    "enviados": falhas_count + sucessos_count,
                    "estatisticas": {
                        "falhas": falhas_count,
                        "sucessos": sucessos_count
                    }
                })
            else:
                return jsonify({"erro": f"Erro no envio: {result.stderr}"}), 500
                
        except Exception as e:
            return jsonify({"erro": f"Erro ao executar script: {str(e)}"}), 500
            
    except Exception as e:
        print(f"Erro no envio de evidências: {str(e)}")
        return jsonify({"erro": str(e)}), 500

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
        
        falhas_count = len([f for f in os.listdir(falhas_dir) if f.endswith('.png')]) if os.path.exists(falhas_dir) else 0
        sucessos_count = len([f for f in os.listdir(sucessos_dir) if f.endswith('.png')]) if os.path.exists(sucessos_dir) else 0
        
        return jsonify({
            "falhas": falhas_count,
            "sucessos": sucessos_count,
            "total": falhas_count + sucessos_count,
            "processado": (falhas_count + sucessos_count) > 0
        })
        
    except Exception as e:
        print(f"Erro ao obter status das evidências: {str(e)}")
        return jsonify({"erro": str(e)}), 500

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
