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
    """Extrai texto simples da descrição em formato Atlassian Document Format"""
    if not descricao or not descricao.get("content"):
        return ""
    
    texto = ""
    for content in descricao.get("content", []):
        if content.get("type") == "paragraph":
            for item in content.get("content", []):
                if item.get("type") == "text":
                    texto += item.get("text", "")
        elif content.get("type") == "codeBlock":
            texto += f"\n```\n{content.get('content', [{}])[0].get('text', '')}\n```\n"
    
    return texto.strip()

def extrair_texto_campo(campo):
    """Extrai texto simples de campos customizados"""
    if not campo or not campo.get("content"):
        return ""
    
    texto = ""
    for content in campo.get("content", []):
        if content.get("type") == "paragraph":
            for item in content.get("content", []):
                if item.get("type") == "text":
                    texto += item.get("text", "")
    
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



















if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
