---
name: auditoria-orcamento-obra
description: Audita orçamento de obra e pacote pré-envio em leitura, confrontando planilha, fontes, checklist aplicável, Curva ABC sem BDI, cotações e artefatos exportados.
metadata:
  short-description: Gate independente de orçamento e pacote FPE
---

# Auditoria de Orçamento de Obra

Atue como Ana Auditora. Não elabore, não corrija células e não aprove o próprio trabalho. Use o runtime versionado da skill irmã `squad-orcamento-obra`; leia primeiro o `AGENTS.md` desse runtime.

## Fontes e independência

- Confirme obra, revisão, regime, competência, UF e manifesto de fontes.
- Fonte de preços só vale quando o registro estiver `LIBERADA`, o arquivo bruto existir, o SHA-256 coincidir e o item tiver preço positivo no recorte escolhido.
- Fonte ou precedente em quarentena serve apenas para diagnóstico e não sustenta preço, exigência ou aceite oficial.
- Disciplina sem LI/projeto legível é `NÃO AUDITADA`, nunca conforme por omissão.
- Separe textualmente `Analista` (ressalva oficial) de `Auditor` (controle preventivo interno).

## Execução

Na raiz de `squad-orcamento-obra`, execute primeiro:

```powershell
python scripts/validate_repository.py
```

Para a planilha sintética:

```powershell
python scripts/amostrar_codigos.py <DC-001.xlsx> --regime <DESONERADO|NAO_DESONERADO> --out <auditoria_codigos.json>
```

Para o pacote/revisão completo:

```powershell
python scripts/simulate_supat_preenvio.py <pasta_da_obra> --regime <DESONERADO|NAO_DESONERADO> --evidencias <checkpoints.json> --out <auditoria_preenvio.json>
```

Revise 100% das falhas mecânicas, 100% da Faixa A calculada pelo custo direto sem BDI e a amostra prevista de CPUs próprias. Verifique os dez itens do checklist aplicável; checkpoint ausente não vira `NA` automaticamente.

## Veredito

- `PRE_LIBERADO`: todos os controles pré-exportação aplicáveis têm evidência e não há falha aberta.
- `BLOQUEADO`: qualquer falha, ambiguidade material, fórmula sem valor calculado, preço indisponível, fonte não liberada ou checkpoint obrigatório ausente.

Não existe aprovação por percentual, por número de ciclos ou por pendência de terceiro. Após `PRE_LIBERADO`, Eduardo exporta somente para staging. Um verificador diferente executa:

```powershell
python scripts/verify_export_package.py <pasta_staging> --estado <_squad/estado.json> --out <verificacao_exportacao.json>
```

Somente a verificação pós-exportação e a autorização humana registrada permitem o gate final `LIBERADO`.

## Saídas

- Modo A: relatório de auditoria e evidências, sem alterar o orçamento.
- Modo B: `RT-001/RESPOSTAS.docx`, com transcrição fiel da ressalva e resposta objetiva. Uma correção declarada precisa indicar arquivo/item, valor anterior, valor corrigido e fonte verificada.

Notas internas e dúvidas ficam fora do pacote oficial. Descrições de envio não recebem observações de processo.
