# TASK-05 — hardening do PicSafe AI

Status: aprovado e executado no branch `fix/task-05-hardening-picsafe`.

## Objetivo

Transformar a base da PoC em um fluxo seguro, testável e honesto, sem apresentar o stub como inteligência real ou inferir segurança pela ausência de detecção.

## Baseline registrado

- 17 testes: 16 passavam e 1 falhava.
- Ruff: 251 ocorrências.
- `scripts/build_report.py`: erro de sintaxe.
- Não havia CI, `.dockerignore` ou imagem de frontend.
- Uploads confiavam em extensão, usavam paths/nome original e tinham limpeza frágil.
- O frontend injetava o relatório com `dangerouslySetInnerHTML`.

## Plano executado

1. Criar o contrato `VisionDetector` e tornar o stub explícito, limitado a dev/test e incapaz de gerar `OK`.
2. Validar 4–12 JPEG/PNG/WebP por MIME e decodificação, com 10 MiB por arquivo, 60 MiB por requisição e limite de pixels.
3. Isolar cada análise em temporário exclusivo, usar IDs opacos e limpar recursos mesmo em falha.
4. Tornar validações atômicas; declarar falhas parciais do detector e recusar falha total.
5. Impedir associação de boxes entre imagens e adicionar referências estruturadas de evidência.
6. Autoescapar relatórios, isolar sua renderização no frontend e aplicar retenção aos artefatos.
7. Corrigir scripts, tipagem, lint e documentação; atingir cobertura de testes de pelo menos 80%.
8. Endurecer Docker/Compose e adicionar CI de backend, frontend e contêineres.

## Critérios de aceite

- ausência de configuração do detector falha de forma explícita;
- produção não aceita stub;
- nenhum resultado simulado recebe `OK`;
- uploads inválidos retornam 422 sem artefatos finais;
- falhas parciais e totais têm contratos diferentes;
- temporários não sobrevivem ao processamento;
- relatório não executa conteúdo fornecido pelo usuário;
- `black`, Ruff, mypy, pytest/cobertura, TypeScript, ESLint, build e Docker passam.
