# Visão geral

O PicSafe AI é uma prova de conceito para organizar uma **pré-avaliação visual** de máquinas. O fluxo aceita evidências fotográficas, executa um detector substituível, aplica regras determinísticas e produz um checklist rastreável.

## Limites obrigatórios

- Não emite laudo técnico.
- Não declara conformidade ou não conformidade com a NR-12.
- Não substitui inspeção presencial nem profissional habilitado.
- Ausência de detecção não é evidência de condição segura; o estado correspondente é `DESCONHECIDO`.
- Confianças são probabilidades do detector, não métricas de segurança.

## Estado atual

Não existe modelo real integrado nem métricas de dataset. O backend `stub` é simulado, serve somente a desenvolvimento/testes e é exibido como tal em API, relatório e interface. Em produção, a configuração exige `DETECTOR_BACKEND=real`, mas a inicialização falha até que uma implementação real seja integrada de forma explícita.

## Fluxo de dados

1. A API exige 4–12 imagens JPEG, PNG ou WebP.
2. Cada arquivo é lido em blocos, limitado por bytes e pixels e decodificado de verdade.
3. A requisição usa um diretório temporário exclusivo e IDs opacos.
4. Falhas de validação rejeitam o lote inteiro com HTTP 422.
5. Falha do detector em parte das imagens gera resposta `partial`; falha em todas gera HTTP 503.
6. Regras associam evidências apenas dentro da mesma imagem.
7. Temporários são removidos; relatório e imagens anotadas seguem a retenção configurada.

## Segurança e privacidade

O cliente deve enviar somente dados necessários e observar base legal, transparência, controle de acesso e descarte. Nomes originais e paths locais não integram a resposta. Relatórios usam autoescape e a interface os exibe em iframe sem permissões.
