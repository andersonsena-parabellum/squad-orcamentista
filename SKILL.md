---
name: squad-orcamento-obra
description: Orquestra o Squad FPE para levantar, estruturar, precificar, cotar, auditar e fechar revisões de orçamentos de obras, com fontes rastreáveis e gates pré/pós-exportação.
metadata:
  short-description: Squad auditável de orçamento de obras FPE
  argument-hint: "[pasta da obra | revisão Rxx | auditoria e fechamento]"
---

# Squad de Orçamento de Obras FPE

Use esta skill para operar uma obra inteira ou uma revisão do pacote orçamentário. Este diretório é o runtime versionado; leia `AGENTS.md` antes de agir e trate seus scripts como controles determinísticos, não como sugestões.

## Preflight obrigatório

Na raiz desta skill, execute:

```powershell
python scripts/validate_repository.py
```

Prossiga somente se o `gate` for `LIBERADO`. As `restricoes_ativas` não paralisam escopos independentes, mas devem ser respeitadas por fonte:

- `SINAPI` pode sustentar preços apenas quando `FONTES_DADOS.json` estiver `LIBERADA`, o arquivo bruto existir, o hash coincidir e o item tiver preço positivo na UF, competência e regime escolhidos.
- Fonte em quarentena não pode ser usada como preço, paradigma ou prova. Atualmente, a ORSE local é apenas diagnóstica.
- O corpus SUPAT em quarentena não pode ser citado como exigência oficial; o checklist continua utilizável, e cada precedente exige conferência no documento de origem.

Nunca contorne um bloqueio mudando manualmente status ou preço.

## Papéis e segregação

- Sofia inventaria fontes, disciplinas, revisão e regime; inicializa/coordena o estado e redige apenas o relatório interno.
- Levi mede quantidades líquidas e registra a fonte geométrica. Não precifica.
- Elias monta a EAP PMBOK de três níveis por execução, antes da precificação. Não usa pastas BIM como macroetapa.
- Otávio consulta a base mecanicamente, aplica a cascata autorizada e edita o orçamento. Não audita o próprio trabalho.
- Carlos trata itens fora de tabela com especificação-âncora idêntica, três fornecedores elegíveis, CNPJ verificável e mediana FOB. Não envia comunicação externa sem autorização.
- Ana trabalha em leitura, executa os dez itens do checklist e emite somente `PRE_LIBERADO` ou `BLOQUEADO`.
- Eduardo exporta em staging após `PRE_LIBERADO` e não sela o envio.
- O verificador pós-exportação compara os sete pares, conteúdo e hashes; só então a autorização humana permite `LIBERADO`.

Não acumule elaboração, auditoria e liberação no mesmo papel.

## Fluxo de estado

O fluxo válido é:

`FONTES_CONGELADAS → QTO_PRONTO → EAP_PRONTA → PRECIFICACAO_PRONTA → COTACOES_PRONTAS → AUDITORIA_PENDENTE → AUDITORIA_APROVADA → EXPORTACAO_STAGING → POS_EXPORTACAO_OK → AUTORIZADO → SELADO`

Inicialize uma obra com `scripts/iniciar_squad.py`. Avance somente com `scripts/atualizar_estado.py` e um handoff gerado por `scripts/build_handoff.py`; os artefatos e o manifesto de fontes devem conservar os mesmos hashes.

Não existe aprovação por percentual, por limite de ciclos ou por pendência de terceiro. Uma pendência sem evidência permanece bloqueio. Pergunte ao usuário apenas quando uma decisão técnica ambígua muda materialmente o resultado ou exige nova autoridade.

## Quantitativos e EAP

- Declare obra, revisão, regime, competência e fontes antes de medir.
- Inventarie todas as disciplinas. Disciplina sem LI/projeto legível é `NÃO AUDITADA`, nunca `OK` por omissão.
- A quantidade da planilha é líquida na unidade remunerada pela composição. Perdas pertencem aos coeficientes da CPU quando tecnicamente aplicáveis.
- Parede, espessura, unidade ambígua e serviço implícito exigem evidência do projeto/memorial; não aplique regra geométrica universal.
- Inclua serviços necessários à execução apenas quando sustentados pela fonte ou por premissa técnica formalmente registrada.

## Preços e cotações

Consulte códigos com fonte e regime explícitos:

```powershell
python 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 93680 --fonte SINAPI --regime nao_desonerado
```

A cascata é: SINAPI exato; SINAPI adaptável com caderno; sugestão técnica ao projetista; ORSE oficial liberada; CPU catalogada; CPU adaptada; CPU nova documentada; cotação; minuta de solicitação. Pule qualquer etapa cuja fonte esteja bloqueada e registre o motivo. Horas de mão de obra, BDI, encargos, produtividade e perdas não têm valor universal.

## Auditoria e fechamento

Execute a validação de códigos na planilha e a simulação pré-envio:

```powershell
python scripts/amostrar_codigos.py <DC-001.xlsx> --regime NAO_DESONERADO
python scripts/simulate_supat_preenvio.py <pasta_da_obra> --regime <DESONERADO|NAO_DESONERADO> --evidencias <checkpoints.json> --out <auditoria_preenvio.json>
```

A Curva ABC é calculada sobre custo direto sem BDI. Revise 100% das falhas mecânicas, 100% da Faixa A aplicável e a amostra de CPUs próprias. Descrição, unidade, código, preço, fórmula sem cache, mediana incorreta ou checkpoint ausente bloqueiam.

Depois do `PRE_LIBERADO`, gere as sete pastas em staging, cada uma com XLSX e PDF. Valide com:

```powershell
python scripts/verify_export_package.py <pasta_staging> --estado <_squad/estado.json> --out <verificacao_exportacao.json>
```

Preserve todas as revisões e envios anteriores. O pacote oficial contém apenas material externo sanitizado; `RELATORIO-SQUAD.docx`, notas internas e dúvidas não entram no envio.

## Atualização da base

Para reproduzir a publicação SINAPI oficial registrada:

```powershell
python scripts/importar_sinapi.py
```

O importador confere o SHA-256 do ZIP CAIXA, reconcilia regimes, preserva registros oficiais sem preço como indisponíveis e troca somente a partição SINAPI do SQLite de forma atômica.
