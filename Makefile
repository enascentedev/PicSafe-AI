# Makefile para PicSafe AI

.PHONY: help install dev test lint format type-check clean build docs

# Variáveis
PYTHON := uv run python
UV := uv
FRONTEND_DIR := frontend

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala todas as dependências
	$(UV) sync
	cd $(FRONTEND_DIR) && npm install

dev: ## Executa ambos backend e frontend em modo desenvolvimento
	@echo "Iniciando backend..."
	$(UV) run uvicorn src.picsafe_ai.api.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Iniciando frontend..."
	cd $(FRONTEND_DIR) && npm run dev &
	@echo "Aplicações iniciadas. Backend: http://localhost:8000, Frontend: http://localhost:3000"
	@echo "Pressione Ctrl+C para parar"

dev-backend: ## Executa apenas o backend
	$(UV) run uvicorn src.picsafe_ai.api.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Executa apenas o frontend
	cd $(FRONTEND_DIR) && npm run dev

test: ## Executa todos os testes
	$(UV) run pytest tests/ -v --tb=short

test-backend: ## Executa testes do backend
	$(UV) run pytest tests/ -v --tb=short

test-frontend: ## Executa testes do frontend
	cd $(FRONTEND_DIR) && npm test

lint: ## Executa linting em Python e JavaScript
	$(UV) run ruff check src/ tests/
	cd $(FRONTEND_DIR) && npm run lint

format: ## Formata código Python e JavaScript
	$(UV) run black src/ tests/
	$(UV) run ruff check --fix src/ tests/
	cd $(FRONTEND_DIR) && npm run format

type-check: ## Executa verificação de tipos
	$(UV) run mypy src/
	cd $(FRONTEND_DIR) && npm run type-check

security: ## Executa verificações de segurança
	$(UV) run pip-audit
	cd $(FRONTEND_DIR) && npm audit

clean: ## Limpa arquivos temporários
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	cd $(FRONTEND_DIR) && rm -rf node_modules/.cache
	cd $(FRONTEND_DIR) && rm -rf dist

build: ## Build para produção
	$(UV) build
	cd $(FRONTEND_DIR) && npm run build

docs: ## Gera documentação
	@echo "Documentação está em docs/"
	@echo "Para visualizar: python -m http.server 8001 -d docs/"

docker-build: ## Build da imagem Docker
	docker build -t picsafe-ai .

docker-run: ## Executa container Docker
	docker run -p 8000:8000 picsafe-ai

setup: ## Configuração inicial do projeto
	$(UV) sync
	cp config.env .env.example
	@echo "✅ Backend configurado"
	cd $(FRONTEND_DIR) && npm install
	@echo "✅ Frontend configurado"
	@echo "📝 Edite .env com suas configurações"
	@echo "🚀 Execute 'make dev' para iniciar desenvolvimento"

check: ## Executa todas as verificações (lint, type, test)
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	@echo "✅ Todas as verificações passaram!"
