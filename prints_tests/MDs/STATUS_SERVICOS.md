# Status dos Serviços

## ✅ Serviços Ativos

### Aplicação Flask
- **Status**: ✅ Rodando
- **Porta**: 8081
- **URL**: http://localhost:8081
- **Página Principal**: http://localhost:8081/
- **Importação**: http://localhost:8081/importar-planilha

### APIs Disponíveis
- ✅ `POST /api/extrair-id-planilha` - Extrai ID da URL
- ✅ `POST /api/carregar-abas-planilha` - Carrega abas
- ✅ `POST /api/visualizar-planilha` - Visualiza dados
- ✅ `POST /api/importar-planilha` - Importa para Jira

## 🔧 Como Verificar Status

### Verificar se está rodando:
```bash
curl http://localhost:8081/importar-planilha
```

### Verificar porta:
```bash
lsof -i :8081
```

### Verificar processos:
```bash
ps aux | grep "python.*app.py"
```

## 🚀 Como Reiniciar

### Método 1: Manual
```bash
source venv/bin/activate
python app.py
```

### Método 2: Script Automático
```bash
./start_server.sh
```

### Método 3: Parar e Reiniciar
```bash
pkill -f "python.*app.py"
source venv/bin/activate
python app.py
```

## 📊 Logs Úteis

### Ver logs em tempo real:
```bash
tail -f /dev/null  # Se houver arquivo de log
```

### Verificar erros:
```bash
ps aux | grep python
```

## 🔍 Diagnóstico de Problemas

### Se a porta 8081 estiver ocupada:
```bash
lsof -i :8081
kill -9 <PID>
```

### Se o ambiente virtual não estiver ativo:
```bash
source venv/bin/activate
```

### Se as dependências estiverem faltando:
```bash
pip install -r requirements.txt
```

## 📞 Suporte

Se os serviços caírem:
1. Execute `./start_server.sh` para reiniciar automaticamente
2. Verifique se há erros no console
3. Confirme se a porta 8081 está livre
4. Reinicie manualmente se necessário

## 🎯 URLs Importantes

- **Página Principal**: http://localhost:8081/
- **Importar Planilha**: http://localhost:8081/importar-planilha
- **Visualizar Planilha**: http://localhost:8081/planilha/CREDT-1161
- **API Status**: http://localhost:8081/api/extrair-id-planilha (POST)
