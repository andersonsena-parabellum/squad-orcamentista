# Restrições conhecidas para uso produtivo

Esta versão opera em modo **fail-closed**. O núcleo SINAPI BA está liberado; fontes ou registros não comprovados ficam isolados e não paralisam escopos independentes.

## Resolvido — SINAPI oficial verificável

- Estado: `LIBERADA` para Bahia, competência `2026-07`, regimes desonerado e não desonerado.
- Origem: ZIP XLSX oficial da CAIXA preservado em `03-BASE_DE_PRECOS/00-FONTES_OFICIAIS/` e registrado por SHA-256.
- Importação: `python scripts/importar_sinapi.py`, com reconciliação dos quatro relatórios, analítico e troca atômica da partição SINAPI.
- Limitação oficial: 2.144 composições e 1.672 insumos não têm preço positivo para BA em ambos os regimes; o uso desses registros é bloqueado individualmente.

## P1 — ORSE sintética/genérica

- Estado: `QUARENTENADA`.
- Evidência: 1.050/1.050 composições ORSE apresentam descrições parametrizadas genéricas; há referências analíticas órfãs por fonte.
- Necessário: substituir por exportação oficial verificável, com competência/UF, hash e importação reproduzível.

## P1 — corpus de precedentes sem revisão por caso

- Estado: `QUARENTENADA`.
- Evidência: o conjunto legado mistura fala do analista, resposta da FPE e ação inferida automaticamente.
- Necessário: vincular cada caso ao documento e hash de origem, registrar página/tabela/parágrafo, classificar a autoria do texto e obter revisão humana.

## P1 — exceções oficiais e legado isolado

- SINAPI: 2.144 composições e 1.672 insumos sem preço positivo na BA; quatro coeficientes analíticos oficiais iguais a zero.
- SINAPI: zero referências órfãs após a importação oficial.
- ORSE em quarentena: 1.050 descrições genéricas e referências analíticas não confiáveis; não são avaliadas como fonte liberada.

Esses números são reproduzíveis com `python scripts/validate_repository.py`. O gate do runtime fica verde quando não há P0; cada orçamento continua bloqueado se usar item sem preço ou fonte não liberada.
