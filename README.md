# POC ICTIM — Pregão Eletrônico nº 001/2026

Plataforma completa com DLT, Workflows, Kanban, Chatbot NLP, Voz, IDP/OCR e Motor de Automação.

## Iniciar em um comando

```bash
cp .env.example .env   # editar se necessário
docker compose up --build
```

Aguarde todos os serviços subirem (~2-3 min na primeira vez).

## Acessos

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

## Credenciais padrão

- **E-mail:** admin@poc.com
- **Senha:** admin123

## Roteiro de demonstração

1. Login em `http://localhost:3000/login`
2. **Fluxos** → Novo Fluxo → Adicionar Etapas → Configurar SLA
3. **Kanban** → Selecionar Fluxo → Criar Processo → Aceitar/Devolver
4. **Redes DLT** → Criar Rede → Criar Contrato Inteligente
5. **API Keys** → Gerar accessKey/secretKey → Testar via curl/Postman
6. **Registros DLT** → Verificar hashes gerados automaticamente
7. **Demo NLP** → Chat contextual + NLP Playground
8. **Voz Receptiva** → Simular chamada com texto
9. **Campanhas de Voz** → Criar campanha ativa
10. **IDP/OCR** → Upload de documento → Processar → Exportar JSON
11. **Automações** → Criar script Python → Executar → Validar Segurança IA

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `NLP_PROVIDER` | `mock` | `mock` ou `openai` |
| `OPENAI_API_KEY` | — | Necessário se `NLP_PROVIDER=openai` |
| `SECRET_KEY` | `supersecretkey...` | Chave JWT — alterar em produção |

## Serviços no docker-compose

| Container | Porta | Descrição |
|---|---|---|
| postgres | 5432 | Banco de dados PostgreSQL 16 |
| redis | 6379 | Cache e broker Celery |
| backend | 8000 | FastAPI + Uvicorn |
| celery-worker | — | Workers para OCR e Automações |
| frontend | 3000 | Next.js 15 |
