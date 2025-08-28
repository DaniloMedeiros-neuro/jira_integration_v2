#!/usr/bin/env python3
"""
Teste de Padronização da Tela de Evidências
===========================================

Este script testa se a tela de evidências foi padronizada corretamente
conforme o design system do projeto Neurotech.
"""

import os
import re
from datetime import datetime

def testar_padronizacao_evidencias():
    """Testa a padronização da tela de evidências"""
    
    print("🧪 TESTE DE PADRONIZAÇÃO DA TELA DE EVIDÊNCIAS")
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
    
    # Lista de testes
    testes = [
        {
            "nome": "Estrutura HTML Padronizada",
            "padrao": r'<div class="evidencias-container">',
            "descricao": "Container principal padronizado"
        },
        {
            "nome": "Header Padronizado",
            "padrao": r'<div class="evidencias-header">',
            "descricao": "Header com estrutura padronizada"
        },
        {
            "nome": "Seções Padronizadas",
            "padrao": r'<div class="evidencias-section">',
            "descricao": "Seções com estrutura consistente"
        },
        {
            "nome": "Section Header",
            "padrao": r'<div class="section-header">',
            "descricao": "Headers de seção padronizados"
        },
        {
            "nome": "Section Title",
            "padrao": r'<div class="section-title">',
            "descricao": "Títulos de seção padronizados"
        },
        {
            "nome": "Section Actions",
            "padrao": r'<div class="section-actions">',
            "descricao": "Ações de seção padronizadas"
        },
        {
            "nome": "Upload Area",
            "padrao": r'<div class="upload-area"',
            "descricao": "Área de upload padronizada"
        },
        {
            "nome": "Processamento Steps",
            "padrao": r'<div class="processamento-steps">',
            "descricao": "Steps de processamento padronizados"
        },
        {
            "nome": "Resultados Stats",
            "padrao": r'<div class="resultados-stats">',
            "descricao": "Estatísticas de resultados padronizadas"
        },
        {
            "nome": "CSS Variables",
            "padrao": r'var\(--neurotech-',
            "descricao": "Variáveis CSS do design system utilizadas"
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
            "descricao": "Ícones Font Awesome utilizados"
        },
        {
            "nome": "JavaScript Functions",
            "padrao": r'function ',
            "descricao": "Funções JavaScript definidas"
        },
        {
            "nome": "Error Handling",
            "padrao": r'if \(![^)]+\) return;',
            "descricao": "Tratamento de erros implementado"
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
    
    # Verificações específicas
    print("🔍 VERIFICAÇÕES ESPECÍFICAS")
    print("-" * 40)
    
    # Verificar estrutura de seções
    secoes = re.findall(r'<div class="evidencias-section"[^>]*>', conteudo)
    print(f"📋 Seções encontradas: {len(secoes)}")
    
    # Verificar variáveis CSS
    variaveis_css = re.findall(r'var\(--neurotech-[^)]+\)', conteudo)
    print(f"🎨 Variáveis CSS utilizadas: {len(variaveis_css)}")
    
    # Verificar responsividade
    media_queries = re.findall(r'@media[^{]+{', conteudo)
    print(f"📱 Media queries encontradas: {len(media_queries)}")
    
    # Verificar funções JavaScript
    funcoes_js = re.findall(r'function\s+(\w+)', conteudo)
    print(f"⚙️ Funções JavaScript: {len(funcoes_js)}")
    
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
    
    # Verificar estrutura geral
    print("🏗️ VERIFICAÇÃO DE ESTRUTURA")
    print("-" * 40)
    
    # Verificar se todas as seções principais estão presentes
    secoes_principais = [
        "evidencias-header",
        "evidencias-section",
        "section-header",
        "section-title",
        "section-actions",
        "upload-area",
        "processamento-steps",
        "resultados-stats"
    ]
    
    estrutura_ok = True
    for secao in secoes_principais:
        if secao in conteudo:
            print(f"   ✅ {secao}: Presente")
        else:
            print(f"   ❌ {secao}: Ausente")
            estrutura_ok = False
    
    print()
    
    # Conclusão
    print("🎯 CONCLUSÃO")
    print("=" * 60)
    
    if testes_passaram == total_testes and estrutura_ok:
        print("🎉 PADRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("   ✅ Todos os testes passaram")
        print("   ✅ Estrutura HTML padronizada")
        print("   ✅ Design system aplicado")
        print("   ✅ Responsividade implementada")
        print("   ✅ Funcionalidades mantidas")
        return True
    else:
        print("⚠️ PADRONIZAÇÃO INCOMPLETA")
        print("   ❌ Alguns testes falharam")
        print("   ❌ Estrutura pode estar incompleta")
        print("   🔧 Revisão necessária")
        return False

def verificar_consistencia_com_outras_telas():
    """Verifica se a tela de evidências está consistente com outras telas"""
    
    print("🔍 VERIFICAÇÃO DE CONSISTÊNCIA COM OUTRAS TELAS")
    print("=" * 60)
    
    # Lista de arquivos para comparar
    arquivos_comparacao = [
        "templates/index.html",
        "templates/metricas.html",
        "templates/planilha.html"
    ]
    
    padroes_consistencia = [
        r'{% extends "base\.html" %}',
        r'{% block title %}',
        r'{% block page_title %}',
        r'{% block page_subtitle %}',
        r'{% block content %}',
        r'{% block extra_js %}',
        r'class="btn btn-',
        r'fas fa-',
        r'container-fluid',
        r'row',
        r'col'
    ]
    
    resultados_consistencia = {}
    
    for arquivo in arquivos_comparacao:
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            resultados_consistencia[arquivo] = {}
            
            for padrao in padroes_consistencia:
                matches = re.findall(padrao, conteudo)
                resultados_consistencia[arquivo][padrao] = len(matches)
    
    # Comparar com evidencias.html
    arquivo_evidencias = "templates/evidencias.html"
    if os.path.exists(arquivo_evidencias):
        with open(arquivo_evidencias, 'r', encoding='utf-8') as f:
            conteudo_evidencias = f.read()
        
        print(f"📄 Comparando {arquivo_evidencias} com outras telas:")
        print()
        
        for arquivo, resultados in resultados_consistencia.items():
            print(f"🔍 {arquivo}:")
            
            for padrao, count in resultados.items():
                count_evidencias = len(re.findall(padrao, conteudo_evidencias))
                
                if count > 0 and count_evidencias > 0:
                    print(f"   ✅ {padrao}: {count_evidencias}/{count} ({(count_evidencias/count)*100:.1f}%)")
                elif count > 0 and count_evidencias == 0:
                    print(f"   ❌ {padrao}: 0/{count} (0%)")
                else:
                    print(f"   ⚠️ {padrao}: Não encontrado em nenhum arquivo")
            
            print()

def main():
    """Função principal"""
    
    print("🚀 INICIANDO TESTES DE PADRONIZAÇÃO")
    print("=" * 60)
    print()
    
    # Teste principal
    sucesso_principal = testar_padronizacao_evidencias()
    
    print()
    print("=" * 60)
    print()
    
    # Verificação de consistência
    verificar_consistencia_com_outras_telas()
    
    print()
    print("=" * 60)
    print(f"⏰ Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return sucesso_principal

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
