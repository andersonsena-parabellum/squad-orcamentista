# Mapa de Composições Próprias

O catálogo separa **modelo estrutural** de **uso direto**. Modelos ajudam a decompor novos serviços, mas não transmitem automaticamente coeficientes, perdas, preços ou aceite de outra obra.

## Situação atual

O arquivo `CATALOGO_CPU_PROPRIAS.json` contém **61 modelos estruturais** recuperados do pacote R01 da Praça do Hospital, com o JSON original preservado por SHA-256. A duplicata idêntica `PRH.007-1` foi deduplicada. Todos estão:

- `uso_como_modelo = LIBERADO`;
- `uso_direto = BLOQUEADO_ATE_REVALIDACAO`;
- `preco = RECALCULAR_NA_DATA_BASE_DA_OBRA`.

Consulte por código ou descrição:

```powershell
python 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py pergolado
```

A ficha avulsa `PRP-001-TI` permanece [quarentenada](por_disciplina/CPU_PRP_001_RACK_44U.md), pois não integra o catálogo validado e não contém as evidências declaradas de preço e coeficientes.

As antigas referências `PRP-002-AV` e `PRP-003-EST` foram removidas do índice vigente porque não existem fichas correspondentes no repositório. Elas permanecem rastreáveis na tag `v0.1.0-baseline`.

## Critérios para uso direto em uma obra

1. Ficha analítica completa, com versão e responsável técnico pela revisão.
2. Referência paradigmática comprovada e fonte de preços `LIBERADA`.
3. Coeficientes tecnicamente justificados; nenhuma regra fixa de horas substitui a análise do serviço.
4. Insumos de mercado acompanhados do DC-007 e de pelo menos três propostas comparáveis, com CNPJ e datas verificáveis.
5. Preço adotado pela mediana das propostas válidas, na mesma base econômica e logística.
6. Validação mecânica e aprovação humana registradas com hash do artefato.
