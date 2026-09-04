# Bloqueios conhecidos para uso produtivo

Esta versão corrige a arquitetura e opera em modo **fail-closed**. O código pode ser testado, mas a precificação e a citação automática de precedentes permanecem bloqueadas até a cadeia de custódia ser recomposta.

## P0 — SINAPI sem publicação bruta verificável

- Estado: `NAO_VERIFICADA`.
- Necessário: arquivo oficial da competência e UF aplicáveis, regime(s), URL ou identificação da publicação, hash SHA-256 e reconciliação integral com o SQLite.
- Não basta alterar manualmente o status no JSON; o arquivo bruto e o hash precisam existir e corresponder.

## P0 — ORSE sintética/genérica

- Estado: `QUARENTENADA`.
- Evidência: 1.050/1.050 composições ORSE apresentam descrições parametrizadas genéricas; há referências analíticas órfãs por fonte.
- Necessário: substituir por exportação oficial verificável, com competência/UF, hash e importação reproduzível.

## P0 — corpus de precedentes sem revisão por caso

- Estado: `QUARENTENADA`.
- Evidência: o conjunto legado mistura fala do analista, resposta da FPE e ação inferida automaticamente.
- Necessário: vincular cada caso ao documento e hash de origem, registrar página/tabela/parágrafo, classificar a autoria do texto e obter revisão humana.

## P1 — qualidade interna do SQLite legado

- 1.856 composições com preço zero ou ausente em algum regime.
- 620 insumos com preço zero ou ausente em algum regime.
- 9 coeficientes nulos ou não positivos.
- 2.342 referências a insumos órfãs por fonte.
- 92 referências a composições auxiliares órfãs por fonte.

Esses números são reproduzíveis com `python scripts/validate_repository.py`. O gate só ficará verde quando não houver achados bloqueantes e as fontes efetivamente usadas estiverem liberadas.
