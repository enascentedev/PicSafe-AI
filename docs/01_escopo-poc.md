# Escopo da PoC

## Incluído

- contrato `VisionDetector` substituível;
- stub determinístico explicitamente simulado;
- validação binária de uploads e limites de recursos;
- pós-processamento isolado por imagem e classe;
- checklist conservador com referências estruturadas de evidência;
- resultado parcial declarado por imagem;
- relatório HTML autoescapado e imagens anotadas;
- frontend com renderização isolada do relatório;
- testes automatizados, CI e imagens de contêiner sem privilégios.

## Fora do escopo

- detector real, treinamento, dataset e métricas de precisão/recall;
- OCR, reconhecimento de pessoas ou biometria;
- interpretação integral da NR-12;
- decisão autônoma de segurança, emissão de laudo ou assinatura técnica;
- autenticação, autorização, banco de dados e operação multi-tenant;
- armazenamento imutável, trilha de auditoria regulatória ou backup.

## Critérios para integrar um detector real

Uma implementação futura deve satisfazer o `VisionDetector`, declarar metadados reais, converter boxes para coordenadas normalizadas, usar limiares configurados e levantar `DetectorError` para falhas esperadas. Antes de uso além da PoC, são necessários dataset representativo, métricas por classe, análise de vieses, versionamento do artefato e validação com profissional habilitado.

## Semântica do checklist

- `ATENÇÃO`: existe evidência visual que merece revisão presencial.
- `DESCONHECIDO`: não há evidência suficiente ou o detector é simulado.
- `OK`: reservado a evidência positiva de detector real; ainda assim não representa conformidade normativa.
