# Instruções para Claude Code

## Migrações de Banco de Dados

**IMPORTANTE**: Sempre que for solicitada uma mudança que impacte a estrutura do banco de dados, você DEVE:

1. **Fazer as alterações nos models** (em `app/models/`)
2. **Gerar a migração automaticamente** usando:
   ```bash
   python -m alembic revision --autogenerate -m "Descrição da mudança"
   ```
3. **Revisar a migração gerada** em `alembic/versions/` para garantir que está correta
4. **Aplicar a migração** ao banco de dados:
   ```bash
   python -m alembic upgrade head
   ```
5. **Informar o usuário** sobre a migração criada e aplicada

### Exemplos de mudanças que requerem migração:
- Adicionar/remover tabelas
- Adicionar/remover colunas
- Alterar tipos de dados
- Adicionar/remover índices
- Adicionar/remover constraints (FK, unique, etc.)
- Alterar relacionamentos entre tabelas

### Comandos úteis do Alembic:
- `python -m alembic current` - Mostra a revisão atual
- `python -m alembic history` - Lista todas as migrações
- `python -m alembic upgrade head` - Aplica todas as migrações pendentes
- `python -m alembic downgrade -1` - Reverte a última migração
- `python -m alembic revision --autogenerate -m "mensagem"` - Cria nova migração

## Configuração do Projeto

### Stack Principal:
- **Backend Python**: FastAPI + SQLAlchemy + Alembic
- **Backend Node.js**: Express (legado, em `src/`)
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **Migrations**: Alembic

### Estrutura de Diretórios:
- `app/` - Código Python/FastAPI
  - `models/` - Modelos SQLAlchemy
  - `schemas/` - Schemas Pydantic
  - `api/` - Endpoints da API
  - `core/` - Configurações core
- `alembic/` - Migrações do banco
- `src/` - Código Node.js (legado)

### Ambiente:
- Python 3.13
- Windows
- Arquivo `.env` com configurações do banco

## Boas Práticas:
1. Sempre verificar se o Alembic está funcionando antes de criar migrações
2. Usar mensagens descritivas nas migrações
3. Revisar o SQL gerado antes de aplicar
4. Manter backup do banco antes de grandes mudanças
5. Testar migrações em ambiente de desenvolvimento primeiro
6. Sempre que for criar um id de tabela, de preferencia ao tipo UUID