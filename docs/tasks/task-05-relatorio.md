# Relatório de execução — TASK-05

## Mudanças entregues

- detector virou uma interface substituível; o stub é identificado como `simulated`, limitado a dev/test e recusado em produção;
- upload passou a validar quantidade, MIME, conteúdo real, bytes por arquivo/requisição e pixels;
- temporários são exclusivos por requisição, nomes externos não são persistidos e IDs são opacos;
- API diferencia rejeição atômica, resultado parcial e indisponibilidade total;
- boxes e regras não cruzam imagens, e evidências carregam detector, versão, modo, imagem, box e confiança;
- ausência de evidência permanece `DESCONHECIDO`; detecção simulada nunca resulta em `OK`;
- relatório usa autoescape, e o frontend deixou de usar `dangerouslySetInnerHTML`;
- retenção configurada passou a remover artefatos expirados;
- dependências foram separadas entre runtime e desenvolvimento e o lock foi atualizado;
- Docker/Compose usam processos sem privilégios e CI cobre backend, frontend e builds de contêiner;
- documentação passou a declarar estado e limitações reais da PoC.

## Validação

- `uv sync --frozen`: passou;
- `uv run black --check src scripts tests`: passou;
- `uv run ruff check src scripts tests`: passou;
- `uv run mypy`: passou, 18 arquivos verificados;
- `uv run pytest`: 30 testes passaram, cobertura total de 93,77%;
- `npm run type-check && npm run lint && npm run build`: passou com Vite 8.2.0;
- `npm audit --audit-level=high`: 0 vulnerabilidades;
- `docker compose config --quiet`: passou;
- builds das imagens de backend e frontend: passaram;
- smoke test: backend e frontend saudáveis, `/health`, `/` e `/api/health`
  responderam com sucesso dentro do WSL;
- inspeção: processos sem privilégios, `cap_drop: ALL` e root filesystem somente
  leitura para os dois serviços;
- `git diff --check`: passou.

O encaminhamento de portas do WSL para o Windows não estava ativo: uma chamada
feita no host expirou, enquanto as mesmas portas e o proxy responderam dentro do
WSL. Isso é uma característica do ambiente local, não do Compose validado.

## Riscos residuais

- não há detector real nem métricas de desempenho;
- não há autenticação/autorização ou isolamento multi-tenant;
- a retenção é aplicada oportunisticamente quando uma análise começa;
- relatórios persistentes devem ser protegidos pelo ambiente de implantação;
- a PoC continua inadequada para decisão autônoma ou laudo NR-12.
