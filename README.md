# Sistema de Monitoramento Multi-Cliente

Sistema de monitoramento com FastAPI, PostgreSQL e Celery para verificação de saúde de múltiplos clientes e seus serviços.

## Funcionalidades

- ✅ CRUD completo de clientes
- ✅ Gerenciamento de serviços por cliente
- ✅ Health checks automáticos a cada 30 segundos
- ✅ Histórico de verificações de saúde
- ✅ API RESTful com documentação automática
- ✅ Background tasks com APScheduler e estrutura para Celery
- ✅ Docker Compose para fácil deployment

## Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM assíncrono
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e broker para Celery
- **Celery** - Processamento de tarefas assíncronas
- **APScheduler** - Agendamento de tarefas
- **Alembic** - Migrações de banco de dados
- **Docker** - Containerização

## Estrutura do Projeto

```
.
├── app/
│   ├── api/              # Endpoints da API
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/             # Configurações e database
│   ├── models/           # Modelos SQLAlchemy
│   ├── schemas/          # Schemas Pydantic
│   ├── services/         # Lógica de negócio
│   ├── tasks/            # Tarefas Celery
│   └── main.py          # Aplicação principal
├── alembic/             # Migrações
├── tests/               # Testes
├── docker-compose.yml   # Orquestração de containers
├── Dockerfile          # Imagem Docker
├── requirements.txt    # Dependências
└── .env               # Variáveis de ambiente
```

## 🚀 Instalação e Execução

### Com Docker (Recomendado)

1. Clone o repositório
2. Copie o arquivo `.env.example` para `.env` e ajuste as configurações se necessário
3. Execute:

```bash
docker-compose up -d
```

A aplicação estará disponível em `http://localhost:9001`

### Desenvolvimento Local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure o PostgreSQL e Redis localmente (ou use Docker apenas para os serviços):
```bash
# Apenas PostgreSQL e Redis via Docker
docker-compose up -d postgres redis
```

3. Execute as migrações:
```bash
alembic upgrade head
```

4. Inicie a aplicação:
```bash
uvicorn app.main:app --reload
```

5. (Opcional) Em terminais separados, inicie o Celery:
```bash
# Terminal 1 - Worker
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 2 - Beat (scheduler)
celery -A app.tasks.celery_app beat --loglevel=info
```

## 📍 Endpoints de Acesso

- **API**: http://localhost:9001
- **Documentação Swagger**: http://localhost:9001/docs
- **Documentação ReDoc**: http://localhost:9001/redoc

## 📚 API Endpoints

### Clientes
- `POST /api/v1/clients` - Cadastrar cliente
- `GET /api/v1/clients` - Listar clientes
- `GET /api/v1/clients/{id}` - Obter cliente
- `PUT /api/v1/clients/{id}` - Atualizar cliente
- `DELETE /api/v1/clients/{id}` - Remover cliente
- `GET /api/v1/clients/{id}/status` - Status dos serviços do cliente

### Serviços
- `POST /api/v1/services` - Cadastrar serviço
- `GET /api/v1/services` - Listar serviços
- `GET /api/v1/services/{id}` - Obter serviço
- `PUT /api/v1/services/{id}` - Atualizar serviço
- `DELETE /api/v1/services/{id}` - Remover serviço

### Health
- `GET /api/v1/health` - Status da API
- `GET /api/v1/health/stats` - Estatísticas do sistema

## 🔧 Variáveis de Ambiente

Veja o arquivo `.env.example` para todas as configurações disponíveis. Principais variáveis:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Configurações do PostgreSQL
- `REDIS_HOST`, `REDIS_PORT` - Configurações do Redis
- `APP_PORT` - Porta da aplicação (padrão: 9001)
- `HEALTH_CHECK_INTERVAL` - Intervalo entre health checks em segundos (padrão: 30)

## 🗄️ Migrações de Banco

Criar nova migração:
```bash
alembic revision --autogenerate -m "descrição da mudança"
```

Aplicar migrações:
```bash
alembic upgrade head
```

Reverter última migração:
```bash
alembic downgrade -1
```

## 📝 Exemplo de Uso

### 1. Cadastrar um cliente:
```bash
curl -X POST "http://localhost:9001/api/v1/clients" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cliente Exemplo",
    "dns": "https://api.exemplo.com",
    "api_key": "sua-api-key-aqui",
    "description": "Cliente de teste"
  }'
```

### 2. Cadastrar um serviço para o cliente:
```bash
curl -X POST "http://localhost:9001/api/v1/services" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "name": "API Principal",
    "endpoint": "https://api.exemplo.com/health",
    "method": "GET",
    "expected_status": 200,
    "timeout": 10
  }'
```

### 3. Verificar status do cliente:
```bash
curl "http://localhost:9001/api/v1/clients/1/status"
```

## ✅ Estrutura Implementada

- **FastAPI** com SQLAlchemy assíncrono e PostgreSQL
- **Modelos**: Client, Service, HealthCheck
- **CRUD completo** para clientes e serviços
- **Health checker** que verifica endpoints externos
- **Background tasks** com APScheduler (executa a cada 30s)
- **Estrutura Celery** preparada (worker e beat configurados)
- **Docker Compose** com PostgreSQL e Redis
- **Alembic** para migrações
- **Configuração** via .env
- **Estrutura organizada** e pronta para expansão

## 🚧 Próximos Passos

- [ ] Adicionar autenticação JWT
- [ ] Implementar notificações (email/webhook) quando serviço ficar offline
- [ ] Dashboard web para visualização
- [ ] Métricas com Prometheus
- [ ] Testes unitários e de integração
- [ ] Rate limiting
- [ ] Backup automático do banco
- [ ] Websockets para atualizações em tempo real
- [ ] Histórico e analytics de uptime