# Setup do Backend no Windows

Como você não tem o `psql` instalado, criei scripts Node.js para configurar o banco de dados.

## 🚀 Passo a Passo Completo

### 1. Instalar Dependências

Abra o PowerShell ou CMD na pasta do backend:

```powershell
cd C:\Projetos\Fluxo Ideal\fluxo-ideal-ccm-backend
npm install
```

### 2. Configurar Banco de Dados

Opção A - Usar o script Node.js (RECOMENDADO):
```powershell
npm run db:init
```

Este comando vai:
- Conectar ao PostgreSQL em 10.102.1.16
- Criar todas as tabelas necessárias
- Inserir dados de exemplo
- Mostrar o status das tabelas

Opção B - Testar apenas a conexão:
```powershell
npm run db:test
```

### 3. Iniciar o Servidor

```powershell
npm run dev
```

O servidor estará rodando em: http://localhost:3000

## 🧪 Testar a API

### Usando PowerShell:

```powershell
# Testar se a API está rodando
Invoke-RestMethod -Uri "http://localhost:3000" -Method GET

# Verificar saúde dos serviços
Invoke-RestMethod -Uri "http://localhost:3000/api/health" -Method GET

# Listar clientes
Invoke-RestMethod -Uri "http://localhost:3000/api/clients" -Method GET

# Criar um novo cliente
$body = @{
    name = "Server-Test-01"
    ip_address = "10.102.1.30"
    status = "online"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/api/clients" -Method POST -Body $body -ContentType "application/json"
```

### Usando curl (Git Bash):

```bash
# Testar se a API está rodando
curl http://localhost:3000

# Verificar saúde dos serviços
curl http://localhost:3000/api/health

# Listar clientes
curl http://localhost:3000/api/clients

# Criar um novo cliente
curl -X POST http://localhost:3000/api/clients \
  -H "Content-Type: application/json" \
  -d '{"name":"Server-Test-01","ip_address":"10.102.1.30","status":"online"}'
```

## 🔍 Verificar Logs

O servidor mostra logs detalhados no console:
- ✅ Conexões bem-sucedidas (PostgreSQL e Redis)
- ❌ Erros de conexão
- 📝 Requisições HTTP
- 🔄 Cache hits/misses

## 🛠️ Troubleshooting

### Erro: "Cannot connect to PostgreSQL"

1. Verifique se o servidor 10.102.1.16 está acessível:
```powershell
Test-NetConnection -ComputerName 10.102.1.16 -Port 5432
```

2. Verifique as credenciais no arquivo `.env`

### Erro: "Cannot connect to Redis"

1. Verifique se o Redis está acessível:
```powershell
Test-NetConnection -ComputerName 10.102.1.16 -Port 6379
```

2. Verifique a senha do Redis no arquivo `.env`

### Erro: "Module not found"

Reinstale as dependências:
```powershell
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json
npm install
```

## 📊 Estrutura das Tabelas

Após rodar `npm run db:init`, você terá:

- **clients**: Tabela principal com informações dos clientes
- **client_metrics**: Métricas históricas
- **alerts**: Sistema de alertas
- **users**: Usuários do sistema (se não usar Keycloak)

## 🔧 Scripts Disponíveis

```powershell
npm run dev        # Desenvolvimento com auto-reload
npm start          # Produção
npm run db:init    # Criar/atualizar banco de dados
npm run db:test    # Testar conexão com o banco
npm run lint       # Verificar código
```

## 📝 Próximos Passos

1. ✅ Backend rodando
2. ✅ Banco de dados configurado
3. ➡️ Integrar com o frontend (porta 5173)
4. ➡️ Configurar Keycloak (se necessário)
5. ➡️ Deploy em produção