#!/usr/bin/env python3
"""
Script para testar as correções implementadas no SB Admin 2
"""

import requests
import time
import webbrowser
from pathlib import Path

def test_server():
    """Testa se o servidor Flask está rodando"""
    try:
        # Tentar conectar na porta 8081
        response = requests.get('http://localhost:8081', timeout=5)
        if response.status_code == 200:
            print("✅ Servidor Flask está rodando na porta 8081")
            return True
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando na porta 8081")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def check_files():
    """Verifica se os arquivos necessários existem"""
    files_to_check = [
        'static/js/sb-admin-2-custom.js',
        'static/css/sb-admin-2-custom.css',
        'templates/base_sb_admin.html',
        'teste_sb_admin.html'
    ]
    
    print("\n📁 Verificando arquivos:")
    all_exist = True
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NÃO ENCONTRADO")
            all_exist = False
    
    return all_exist

def open_test_page():
    """Abre a página de teste no navegador"""
    test_file = Path('teste_sb_admin.html')
    if test_file.exists():
        print(f"\n🌐 Abrindo página de teste: {test_file.absolute()}")
        webbrowser.open(f'file://{test_file.absolute()}')
    else:
        print("❌ Arquivo de teste não encontrado")

def main():
    """Função principal"""
    print("🔧 Teste das Correções SB Admin 2")
    print("=" * 50)
    
    # Verificar arquivos
    files_ok = check_files()
    
    if not files_ok:
        print("\n❌ Alguns arquivos necessários não foram encontrados!")
        return
    
    # Testar servidor
    print("\n🌐 Testando servidor Flask...")
    server_ok = test_server()
    
    if server_ok:
        print("\n✅ Tudo pronto! Você pode:")
        print("1. Acessar http://localhost:8081 no navegador")
        print("2. Abrir o arquivo teste_sb_admin.html diretamente")
        print("3. Verificar o console (F12) para logs de debug")
        
        # Perguntar se quer abrir a página de teste
        try:
            response = input("\nDeseja abrir a página de teste? (s/n): ").lower()
            if response in ['s', 'sim', 'y', 'yes']:
                open_test_page()
        except KeyboardInterrupt:
            print("\n\n👋 Teste cancelado pelo usuário")
    else:
        print("\n❌ Servidor não está rodando!")
        print("Execute: python app.py")
        print("Ou use uma porta diferente se 8081 estiver ocupada")

if __name__ == "__main__":
    main()
