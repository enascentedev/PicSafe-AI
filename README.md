# 🛡️ PicSafe AI

PoC de Triagem Visual de Segurança de Máquinas (NR-12)

## 📋 Sobre o Projeto

O **PicSafe AI** é uma ferramenta de **triagem visual (pré-avaliação)** baseada em imagens de máquinas industriais, para **acelerar a identificação de indícios de riscos** relacionados a itens visuais associados à NR-12.

### ⚠️ Importante

Esta é uma **pré-avaliação automatizada**. Os resultados são **indiciais** e **requerem validação por profissional habilitado** (Engenheiro de Segurança) para emissão de laudo oficial.

**NÃO emite laudo, NÃO declara conformidade NR-12, NÃO substitui inspeção presencial.**

### 🚧 O detector de visão computacional é um stub

Leia antes de interpretar qualquer resultado desta PoC:

> **Não existe modelo de visão computacional treinado neste projeto.** A classe `VisionDetector` (`src/picsafe_ai/vision/detector.py`) devolve detecções **simuladas**, escolhidas a partir de palavras no **nome do arquivo** da imagem (`emergency`, `guard`, `moving`, `danger`, `sign`…). Os valores de confiança exibidos — 0.85, 0.78, 0.92 e outros — são **constantes fixas no código**, não medições.
>
> Consequência: o checklist e o relatório HTML gerados são **demonstrações do fluxo de dados**, não avaliações de segurança. Nenhum número produzido por esta PoC descreve o estado real de uma máquina.

O objetivo do stub é permitir desenvolver e testar a API, o motor de regras e o relatório antes de existir um modelo treinado.

## 📊 Estado atual

| Item | Estado | Evidência |
|---|---|---|
| API REST (upload, análise, relatório) | Implementado | `src/picsafe_ai/api/main.py` |
| Schemas e contratos Pydantic | Implementado | `src/picsafe_ai/api/schemas.py` |
| Motor de regras NR-12 determinístico | Implementado | `src/picsafe_ai/checklist/rules.py` — com testes em `tests/test_rules.py` |
| Geração de relatório HTML | Implementado | `src/picsafe_ai/reporting/report_html.py` |
| Anotação de imagens | Implementado | `src/picsafe_ai/reporting/annotate.py` |
| Interface web (React + Vite) | Implementado | `frontend/src/` |
| **Detecção de objetos de segurança** | **Simulado** | `src/picsafe_ai/vision/detector.py` — stub por nome de arquivo |
| Métricas do modelo (precisão, recall) | Planejado | não há modelo treinado nem dataset avaliado |
| Expurgo por retenção de imagens | Planejado | `IMAGE_RETENTION_DAYS` existe na configuração, sem rotina que a aplique |
| Imagem Docker do front-end | Planejado | `frontend/Dockerfile` não existe; o serviço está sob o profile `frontend` no compose |
| Documentação em `docs/` | Planejado | os arquivos `00_`–`08_` ainda não foram escritos |

**Legenda** — *Implementado*: funciona ponta a ponta. *Simulado*: mock/stub, não reflete comportamento real. *Planejado*: não implementado.

## 🔐 Privacidade e ciclo de vida das imagens

Onde os dados ficam e por quanto tempo, conforme o código atual (`api/main.py`, `config.py`):

| Artefato | Onde | Retenção real |
|---|---|---|
| Imagem enviada | `uploads/` | **Apagada logo após o processamento** (`Path(path).unlink()`) |
| Imagem anotada | `reports/` | **Permanece por tempo indeterminado** — não há expurgo |
| Relatório HTML | `reports/` | **Permanece por tempo indeterminado** — não há expurgo |

A variável `IMAGE_RETENTION_DAYS` está prevista na configuração, mas **nenhuma rotina a aplica**: configurá-la não apaga nada hoje. Quem operar esta PoC precisa remover `reports/` manualmente conforme sua própria política de retenção.

Nenhuma imagem é enviada a serviços externos: todo o processamento é local. Os diretórios `uploads/`, `reports/` e `temp/` estão no `.gitignore` e não são versionados.

## 🏗️ Arquitetura

**Backend (Python/FastAPI)** — API com schemas Pydantic · detector de objetos (**stub**, ver acima) · motor determinístico de regras NR-12 · geração de relatório HTML

**Frontend (React/TypeScript)** — interface com Shadcn/ui · upload múltiplo de imagens · visualização de relatórios · responsivo

## 📦 Instalação e Execução

Pré-requisitos: Python 3.10+, Node.js 18+ e [uv](https://docs.astral.sh/uv/).

### Backend

```bash
uv sync

# Configuração (opcional — há valores padrão para tudo)
cp config.env.example config.env

uv run uvicorn src.picsafe_ai.api.main:app --reload
```

A API sobe em `http://localhost:8000`; documentação interativa em `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker build -t picsafe-ai .
docker run --rm -p 8000:8000 --env-file config.env picsafe-ai
```

O arquivo de configuração **não é copiado para a imagem** — as variáveis são passadas em tempo de execução. O `docker-compose.yml` sobe apenas a API por padrão; o serviço de front-end está sob o profile `frontend` e depende de um `frontend/Dockerfile` que ainda não existe.

## 🧪 Desenvolvimento

```bash
uv run pytest              # testes
uv run ruff check .        # lint
uv run black --check .     # formatação
uv run mypy .              # tipagem

cd frontend && npm run build
```

### Estrutura

```text
picsafe-ai/
├── src/picsafe_ai/
│   ├── api/                 # FastAPI
│   ├── vision/              # detector (stub)
│   ├── checklist/           # motor de regras
│   ├── reporting/           # relatórios e anotação
│   └── utils/
├── frontend/                # React + Vite + TypeScript
├── tests/                   # testes de regras e schemas
└── .cursor/rules/           # regras de contexto do repositório
```

## 📄 Licença

MIT — veja o arquivo [LICENSE](LICENSE).

## 📞 Contato

Emanuel Nascente — [emanuelnascente@gmail.com](mailto:emanuelnascente@gmail.com)
Dúvidas e sugestões: [issues do repositório](https://github.com/enascentedev/PicSafe-AI/issues).

---

**PicSafe AI v0.1.0** — PoC de triagem visual NR-12
