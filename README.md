# PicSafe AI

PoC de apoio à pré-avaliação visual de máquinas. O projeto recebe de 4 a 12 imagens, executa um detector substituível, aplica regras conservadoras e gera um relatório rastreável.

> A PoC não emite laudo, não declara conformidade com a NR-12 e não substitui inspeção presencial ou validação por profissional habilitado.

## Estado real do detector

O repositório **não contém um modelo de visão treinado**. O único backend disponível é um stub determinístico para desenvolvimento e testes, sempre identificado como `simulated`. Ele não pode produzir status `OK` e é recusado em produção. A aplicação falha ao iniciar se `DETECTOR_BACKEND` não for configurado explicitamente.

## Execução local

Requisitos: Python 3.11+, [uv](https://docs.astral.sh/uv/) e Node.js 22+.

```bash
copy config.env.example config.env
uv sync --frozen
uv run uvicorn picsafe_ai.api.main:app --reload
```

Em outro terminal:

```bash
cd frontend
npm ci
npm run dev
```

A API fica em `http://localhost:8000`, e a interface em `http://localhost:5173`. Não adicione segredos ao `config.env`; nenhum segredo é necessário para o stub.

## Contêineres

```bash
docker compose up --build
```

A interface fica em `http://localhost:3000`. O Compose usa o stub explicitamente em modo de desenvolvimento, usuário sem privilégios, capabilities removidas e armazenamento temporário isolado.

## Qualidade

```bash
uv run black --check src scripts tests
uv run ruff check src scripts tests
uv run mypy
uv run pytest
cd frontend
npm run type-check
npm run lint
npm run build
```

O CI repete essas verificações e constrói as imagens de backend e frontend. A cobertura mínima do backend é 80%.

## Privacidade e retenção

Uploads são validados por conteúdo, recebem identificadores opacos e ficam em um workspace exclusivo removido ao final da requisição. Apenas relatório e imagens anotadas são persistidos em `reports/`, com retenção configurável por `IMAGE_RETENTION_DAYS` (30 dias por padrão). Evite enviar dados pessoais e opere com base legal e controles adequados ao seu contexto.

Detalhes de escopo e limitações estão em [docs/00_visao-geral.md](docs/00_visao-geral.md) e [docs/01_escopo-poc.md](docs/01_escopo-poc.md).

## Licença

MIT. Consulte [LICENSE](LICENSE).
