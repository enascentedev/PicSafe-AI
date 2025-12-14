# 🛡️ PicSafe AI

PoC de Triagem Visual de Segurança de Máquinas (NR-12)

## 📋 Sobre o Projeto

O **PicSafe AI** é uma ferramenta de **triagem visual (pré-avaliação)** baseada em imagens/vídeo de máquinas industriais para **acelerar a identificação de indícios de riscos** relacionados a itens visuais associados à NR-12.

### ⚠️ Importante

Esta é uma **pré-avaliação automatizada**. Os resultados são **indiciais** e **requerem validação por profissional habilitado** (Engenheiro de Segurança) para emissão de laudo oficial.

**NÃO emite laudo, NÃO declara conformidade NR-12, NÃO substitui inspeção presencial.**

## 🚀 Funcionalidades

- ✅ Upload de 4-12 imagens por máquina
- 🔍 Detecção automática de objetos de segurança
- 📋 Checklist preliminar com estados: OK | ATENÇÃO | DESCONHECIDO
- 📸 Sugestões de fotos pendentes
- 📄 Relatório HTML detalhado
- 🎯 Interface web moderna (React + Tailwind)

## 🏗️ Arquitetura

### Backend (Python/FastAPI)
- **API**: FastAPI com schemas Pydantic
- **Visão**: Detector de objetos (YOLO/inicialmente stub)
- **Regras**: Motor determinístico NR-12
- **Relatórios**: Geração HTML automática

### Frontend (React/TypeScript)
- **UI**: Interface moderna com Shadcn/ui
- **Upload**: Drag & drop de múltiplas imagens
- **Visualização**: Relatórios interativos
- **Responsivo**: Funciona em desktop e mobile

## 📦 Instalação e Execução

### Pré-requisitos

- Python 3.10+
- Node.js 18+
- uv (gerenciador de pacotes Python)

### Backend

```bash
# Instalar dependências
uv sync

# Configurar ambiente
cp config.env .env
# Editar .env com sua OPENAI_API_KEY

# Executar API
uv run uvicorn src.picsafe_ai.api.main:app --reload
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Executar desenvolvimento
npm run dev
```

## 📚 Documentação

- [📖 Visão Geral](docs/00_visao-geral.md)
- [🎯 Escopo do PoC](docs/01_escopo-poc.md)
- [📸 Fluxo de Imagens](docs/02_fluxo-coleta-imagens.md)
- [🏷️ Rotulagem Dataset](docs/03_rotulagem-dataset.md)
- [🤖 Modelo e Métricas](docs/04_modelo-e-metricas.md)
- [📋 Motor de Regras](docs/05_checklist-motor-regras.md)
- [🔌 API e Relatório](docs/06_api-relatorio.md)
- [🔍 Validação](docs/07_validacao-com-engenheiro.md)
- [⚠️ Riscos e Limitações](docs/08_riscos-e-limitacoes.md)

## 🧪 Desenvolvimento

### Estrutura do Projeto

```
picsafe-ai/
├── src/picsafe_ai/          # Backend Python
│   ├── api/                 # FastAPI
│   ├── vision/              # Detecção de objetos
│   ├── checklist/           # Motor de regras
│   ├── reporting/           # Relatórios
│   └── utils/               # Utilitários
├── frontend/                # React/TypeScript
├── tests/                   # Testes
├── docs/                    # Documentação
└── .cursor/rules/           # Regras do Cursor
```

### Comandos Úteis

```bash
# Backend
uv run pytest              # Executar testes
uv run ruff check .        # Lint
uv run black .             # Format
uv run mypy .              # Type check

# Frontend
npm run build              # Build produção
npm run lint               # ESLint
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🙏 Agradecimentos

- Baseado na NR-12 (Norma Regulamentadora 12)
- Desenvolvido com foco em segurança industrial
- Gratidão aos engenheiros de segurança que colaboraram

## 📞 Contato

Para dúvidas ou sugestões, entre em contato:

- **Email**: picsafe@example.com
- **Issues**: [GitHub Issues](https://github.com/seu-repo/picsafe-ai/issues)

---

**PicSafe AI v0.1.0** - PoC de Triagem Visual NR-12
