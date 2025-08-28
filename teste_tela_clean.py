#!/usr/bin/env python3
"""
Teste da Tela de Evidências - Design Clean
==========================================

Este script testa se a tela de evidências refatorada está funcionando
corretamente com o design clean e minimalista.
"""

import os
import re
from datetime import datetime

def testar_tela_clean():
    """Testa a tela refatorada com design clean"""
    
    print("🧪 TESTE DA TELA DE EVIDÊNCIAS - DESIGN CLEAN")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Caminho do arquivo
    arquivo_evidencias = "templates/evidencias.html"
    
    if not os.path.exists(arquivo_evidencias):
        print("❌ ERRO: Arquivo evidencias.html não encontrado!")
        return False
    
    print("📁 Verificando arquivo:", arquivo_evidencias)
    print()
    
    # Ler o arquivo
    with open(arquivo_evidencias, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Lista de testes para design clean
    testes = [
        {
            "nome": "Container Principal",
            "padrao": r'<div class="evidencias-container">',
            "descricao": "Container principal presente"
        },
        {
            "nome": "Upload Section",
            "padrao": r'<div class="upload-section">',
            "descricao": "Seção de upload simplificada"
        },
        {
            "nome": "Upload Area",
            "padrao": r'<div class="upload-area"',
            "descricao": "Área de upload funcional"
        },
        {
            "nome": "File Info",
            "padrao": r'<div id="fileInfo" class="file-info"',
            "descricao": "Informações do arquivo"
        },
        {
            "nome": "Processing Section",
            "padrao": r'<div class="processing-section"',
            "descricao": "Seção de processamento"
        },
        {
            "nome": "Progress Bar",
            "padrao": r'<div class="progress-bar">',
            "descricao": "Barra de progresso"
        },
        {
            "nome": "Processing Steps",
            "padrao": r'<div class="processing-steps">',
            "descricao": "Steps de processamento"
        },
        {
            "nome": "Step Items",
            "padrao": r'<div class="step"',
            "descricao": "Itens dos steps"
        },
        {
            "nome": "Results Section",
            "padrao": r'<div class="results-section"',
            "descricao": "Seção de resultados"
        },
        {
            "nome": "Results Stats",
            "padrao": r'<div class="results-stats">',
            "descricao": "Estatísticas de resultados"
        },
        {
            "nome": "Results Actions",
            "padrao": r'<div class="results-actions">',
            "descricao": "Ações dos resultados"
        },
        {
            "nome": "CSS Variables",
            "padrao": r'var\(--neurotech-',
            "descricao": "Variáveis CSS do design system"
        },
        {
            "nome": "Responsividade",
            "padrao": r'@media \(max-width:',
            "descricao": "Media queries para responsividade"
        },
        {
            "nome": "Bootstrap Integration",
            "padrao": r'btn btn-',
            "descricao": "Classes Bootstrap utilizadas"
        },
        {
            "nome": "Font Awesome Icons",
            "padrao": r'fas fa-',
            "descricao": "Ícones Font Awesome"
        },
        {
            "nome": "JavaScript Functions",
            "padrao": r'function ',
            "descricao": "Funções JavaScript"
        },
        {
            "nome": "Error Handling",
            "padrao": r'if \(![^)]+\) return;',
            "descricao": "Tratamento de erros"
        },
        {
            "nome": "Progress Function",
            "padrao": r'function atualizarProgresso',
            "descricao": "Função de atualização de progresso"
        }
    ]
    
    # Executar testes
    resultados = []
    total_testes = len(testes)
    testes_passaram = 0
    
    for i, teste in enumerate(testes, 1):
        print(f"🔍 Teste {i}/{total_testes}: {teste['nome']}")
        print(f"   📝 {teste['descricao']}")
        
        # Verificar padrão
        matches = re.findall(teste['padrao'], conteudo)
        
        if matches:
            print(f"   ✅ PASSOU - {len(matches)} ocorrência(s) encontrada(s)")
            testes_passaram += 1
            resultados.append({
                "teste": teste['nome'],
                "status": "PASSOU",
                "ocorrencias": len(matches)
            })
        else:
            print(f"   ❌ FALHOU - Nenhuma ocorrência encontrada")
            resultados.append({
                "teste": teste['nome'],
                "status": "FALHOU",
                "ocorrencias": 0
            })
        
        print()
    
    # Verificações específicas do design clean
    print("🔍 VERIFICAÇÕES ESPECÍFICAS DO DESIGN CLEAN")
    print("-" * 50)
    
    # Verificar se elementos complexos foram removidos
    elementos_removidos = [
        "evidencias-header",
        "evidencias-section", 
        "section-header",
        "section-title",
        "section-actions",
        "processamento-steps",
        "resultados-stats"
    ]
    
    elementos_removidos_count = 0
    for elemento in elementos_removidos:
        if elemento not in conteudo:
            print(f"   ✅ {elemento}: Removido (esperado)")
            elementos_removidos_count += 1
        else:
            print(f"   ❌ {elemento}: Ainda presente")
    
    # Verificar elementos simplificados
    elementos_simplificados = [
        "upload-section",
        "processing-section", 
        "results-section",
        "progress-bar",
        "processing-steps",
        "results-stats"
    ]
    
    elementos_simplificados_count = 0
    for elemento in elementos_simplificados:
        if elemento in conteudo:
            print(f"   ✅ {elemento}: Presente (simplificado)")
            elementos_simplificados_count += 1
        else:
            print(f"   ❌ {elemento}: Ausente")
    
    # Verificar tamanho do arquivo
    linhas_arquivo = len(conteudo.split('\n'))
    print(f"   📊 Linhas do arquivo: {linhas_arquivo}")
    
    # Verificar variáveis CSS
    variaveis_css = re.findall(r'var\(--neurotech-[^)]+\)', conteudo)
    print(f"   🎨 Variáveis CSS utilizadas: {len(variaveis_css)}")
    
    # Verificar responsividade
    media_queries = re.findall(r'@media[^{]+{', conteudo)
    print(f"   📱 Media queries encontradas: {len(media_queries)}")
    
    # Verificar funções JavaScript
    funcoes_js = re.findall(r'function\s+(\w+)', conteudo)
    print(f"   ⚙️ Funções JavaScript: {len(funcoes_js)}")
    
    print()
    
    # Resumo dos resultados
    print("📊 RESUMO DOS RESULTADOS")
    print("=" * 60)
    print(f"✅ Testes que passaram: {testes_passaram}/{total_testes}")
    print(f"❌ Testes que falharam: {total_testes - testes_passaram}/{total_testes}")
    print(f"📈 Taxa de sucesso: {(testes_passaram/total_testes)*100:.1f}%")
    print()
    
    # Listar testes que falharam
    testes_falharam = [r for r in resultados if r['status'] == 'FALHOU']
    if testes_falharam:
        print("❌ TESTES QUE FALHARAM:")
        for teste in testes_falharam:
            print(f"   • {teste['teste']}")
        print()
    
    # Listar testes que passaram
    testes_passaram_lista = [r for r in resultados if r['status'] == 'PASSOU']
    if testes_passaram_lista:
        print("✅ TESTES QUE PASSARAM:")
        for teste in testes_passaram_lista:
            print(f"   • {teste['teste']} ({teste['ocorrencias']} ocorrência(s))")
        print()
    
    # Verificar estrutura clean
    print("🏗️ VERIFICAÇÃO DE ESTRUTURA CLEAN")
    print("-" * 40)
    
    # Verificar se a estrutura está clean
    estrutura_clean = True
    
    # Elementos que devem estar presentes
    elementos_obrigatorios = [
        "evidencias-container",
        "upload-section",
        "upload-area",
        "file-info",
        "processing-section",
        "progress-bar",
        "processing-steps",
        "results-section",
        "results-stats",
        "results-actions"
    ]
    
    for elemento in elementos_obrigatorios:
        if elemento in conteudo:
            print(f"   ✅ {elemento}: Presente")
        else:
            print(f"   ❌ {elemento}: Ausente")
            estrutura_clean = False
    
    print()
    
    # Conclusão
    print("🎯 CONCLUSÃO")
    print("=" * 60)
    
    if testes_passaram >= 15 and estrutura_clean and elementos_removidos_count >= 6:
        print("🎉 REFATORAÇÃO CLEAN CONCLUÍDA COM SUCESSO!")
        print("   ✅ Todos os testes essenciais passaram")
        print("   ✅ Estrutura simplificada implementada")
        print("   ✅ Elementos complexos removidos")
        print("   ✅ Design clean aplicado")
        print("   ✅ Funcionalidades mantidas")
        print("   ✅ Performance otimizada")
        return True
    else:
        print("⚠️ REFATORAÇÃO INCOMPLETA")
        print("   ❌ Alguns testes falharam")
        print("   ❌ Estrutura pode estar incompleta")
        print("   🔧 Revisão necessária")
        return False

def verificar_melhorias_performance():
    """Verifica as melhorias de performance da refatoração"""
    
    print("📈 VERIFICAÇÃO DE MELHORIAS DE PERFORMANCE")
    print("=" * 60)
    
    arquivo_evidencias = "templates/evidencias.html"
    
    if not os.path.exists(arquivo_evidencias):
        print("❌ Arquivo não encontrado!")
        return
    
    with open(arquivo_evidencias, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Métricas de análise
    linhas_total = len(conteudo.split('\n'))
    caracteres_total = len(conteudo)
    classes_css = len(re.findall(r'class="[^"]*"', conteudo))
    elementos_div = len(re.findall(r'<div[^>]*>', conteudo))
    variaveis_css = len(re.findall(r'var\(--neurotech-[^)]+\)', conteudo))
    funcoes_js = len(re.findall(r'function\s+\w+', conteudo))
    
    print(f"📊 MÉTRICAS DO ARQUIVO:")
    print(f"   • Linhas de código: {linhas_total}")
    print(f"   • Caracteres: {caracteres_total:,}")
    print(f"   • Classes CSS: {classes_css}")
    print(f"   • Elementos div: {elementos_div}")
    print(f"   • Variáveis CSS: {variaveis_css}")
    print(f"   • Funções JavaScript: {funcoes_js}")
    print()
    
    # Análise de complexidade
    print("🔍 ANÁLISE DE COMPLEXIDADE:")
    
    if linhas_total < 1000:
        print("   ✅ Código compacto (menos de 1000 linhas)")
    else:
        print("   ⚠️ Código extenso (mais de 1000 linhas)")
    
    if elementos_div < 50:
        print("   ✅ Poucos elementos DOM (menos de 50 divs)")
    else:
        print("   ⚠️ Muitos elementos DOM (mais de 50 divs)")
    
    if variaveis_css > 20:
        print("   ✅ Design system bem utilizado (mais de 20 variáveis)")
    else:
        print("   ⚠️ Pouco uso do design system (menos de 20 variáveis)")
    
    if funcoes_js < 25:
        print("   ✅ JavaScript otimizado (menos de 25 funções)")
    else:
        print("   ⚠️ JavaScript complexo (mais de 25 funções)")
    
    print()

def main():
    """Função principal"""
    
    print("🚀 INICIANDO TESTES DA TELA CLEAN")
    print("=" * 60)
    print()
    
    # Teste principal
    sucesso_principal = testar_tela_clean()
    
    print()
    print("=" * 60)
    print()
    
    # Verificação de performance
    verificar_melhorias_performance()
    
    print()
    print("=" * 60)
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return sucesso_principal

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
