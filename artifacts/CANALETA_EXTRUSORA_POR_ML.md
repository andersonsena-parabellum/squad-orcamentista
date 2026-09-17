# Recorte SINAPI — execução com extrusora por metro linear

**Natureza:** consulta/leitura, fail-closed. Nenhum preço, BDI, margem ou “quanto cobrar” foi inventado.  
**Data da consulta:** 2026-09-17.  
**Fonte:** SINAPI, UF BA, competência **2026-07**, status **LIBERADA** (`03-BASE_DE_PRECOS/FONTES_DADOS.json`). Capacidades `consulta`, `paradigma_cpu` e `preco_direto` = LIBERADA.  
**Banco:** `03-BASE_DE_PRECOS/base_precos.db` SHA-256 `a59957251f947dc83f7439d379fbbd1bc1b6d08337fe0cf776d174aff747be34` (confere com o registro). ZIP origem SHA-256 `58c131f997560332cf2d7f7f90644790d5c6e2a909a2963b18f136779312b14f`.  
**Índices Markdown de disciplina:** quarentenados — **não** usados para precificação.

---

## 0. Veredito fail-closed (o que existe / o que não existe)

**Não existe composição SINAPI BA 2026-07 de “canaleta com extrusora”.**

Busca SQL read-only:

```sql
SELECT codigo, unidade, descricao
FROM composicoes
WHERE fonte = 'SINAPI'
  AND descricao LIKE '%CANALETA%'
  AND descricao LIKE '%EXTRUSORA%';
-- n = 0
```

Busca textual do script `consultar_composicao.py EXTRUSORA --fonte SINAPI --regime nao_desonerado` devolve **16** registros, todos da família **guia / guia+sarjeta conjugados / CHI-CHP da máquina**. Nenhum descreve canaleta.

As composições cujo nome contém `CANALETA` são outra família (pré-moldada meia-cana, canaleta armada com fôrma, bloco canaleta de alvenaria, grelha). Nenhuma traz `92960`/`92961`. Exemplo aberto: `106004` usa fôrma `96536`, armação `92915` e concretagem `105944` — **sem extrusora**.

**Composição paradigma adotada para o recorte por metro linear com extrusora:** `94263` (citada no histórico do squad; unidade `M`; menor seção da família; trecho reto).

**Se o serviço da obra for de fato uma canaleta de drenagem moldada in loco com extrusora**, a tabela oficial **não** tem o item. O analogismo mais próximo *funcional* (drenagem longitudinal moldada com a mesma máquina) é **guia + sarjeta conjugados** `94267` (trecho reto, 45 cm de base). Isso **não** substitui o serviço “canaleta” sem decisão humana de De-Para. Números de `94267` vêm no §7, sem misturar com o paradigma.

---

## 1. Respostas diretas — paradigma `94263`

Fonte SINAPI BA 2026-07. Unidade da composição: **M** (metro linear).  
Totais de grupo = soma de `coeficiente × preço unitário armazenado` no SQLite (conta reproduzível). O custo **publicado** da composição é o campo oficial `custo_*` e fecha com residual de arredondamento da cadeia CAIXA (ver §4.4).

| Pergunta | Não desonerado | Desonerado |
|---|---:|---:|
| **1. Locação / equipamento extrusora** (CHI `92961` + CHP `92960`) | **R$ 0,765718 / m** | **R$ 0,765718 / m** |
| idem, 2 casas | R$ 0,77 / m | R$ 0,77 / m |
| **2. Mão de obra de 1º nível** (`88316` + `88309` + `88243`) | **R$ 20,361921 / m** | **R$ 19,350622 / m** |
| idem, 2 casas | R$ 20,36 / m | R$ 19,35 / m |
| **3. Custo direto oficial publicado** da composição | **R$ 43,21 / m** | **R$ 42,18 / m** |
| Soma linha a linha (PU armazenados, 2 casas) | R$ 43,251139 / m | R$ 42,216928 / m |
| Residual (publicado − soma linhas) | − R$ 0,041139 / m | − R$ 0,036928 / m |

**O que a tabela remunera de “locação”:** não há insumo de aluguel de mercado. A composição paga o **custo horário da máquina própria** SINAPI (CHI + CHP da extrusora 14 CV, AF_12/2015), convertido para R$/m pelos coeficientes `0,0722 CHI/m` e `0,0144 CHP/m`. Esse envelope é o que a composição **permite gastar** de equipamento por metro. Cotação de locadora, mobilização e operador avulso **não** estão neste número.

**Preço de venda:** `custo_direto × (1 + BDI)`. BDI é decisão humana/edital (Acórdão 2622/2013-TCU). **Não calculado aqui.**

A composição **não** traz código de “operador de extrusora”. A equipe de 1º nível é pedreiro, servente e ajudante especializado.

---

## 2. Identificação oficial da composição escolhida

| Campo | Valor (ipsis verbis do SQLite / script) |
|---|---|
| Código | **94263** |
| Descrição | GUIA (MEIO-FIO) CONCRETO, MOLDADA IN LOCO EM TRECHO RETO COM EXTRUSORA, 13 CM BASE X 22 CM ALTURA. AF_01/2024 |
| Unidade | **M** |
| Grupo | Guias e sarjetas |
| Fonte / UF / competência | SINAPI / BA / 2026-07 |
| Regime não desonerado | R$ 43,21 |
| Regime desonerado | R$ 42,18 |
| Status da fonte | LIBERADA |

Comando:

```bash
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94263 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94263 --fonte SINAPI --regime desonerado
```

---

## 3. Quadro analítico de 1º nível — `94263`

Fórmula de cada linha: `total = coeficiente × PU`, com PU = `custo_*` (composição auxiliar) ou `preco_*` (insumo) no SQLite.  
Classificação: **LOC** = CHI/CHP da extrusora; **MO** = mão de obra de 1º nível; **OUT** = demais insumos.

### 3.1 Não desonerado

| Cl. | Tipo | Código | Und | Coef. | PU (R$) | Total linha (R$/m) | Descrição (ipsis verbis) |
|---|---|---|---|---:|---:|---:|---|
| LOC | COMPOSICAO | 92961 | CHI | 0,0722 | 6,11 | 0,441142 | MÁQUINA EXTRUSORA DE CONCRETO PARA GUIAS E SARJETAS, MOTOR A DIESEL, POTÊNCIA 14 CV - CHI DIURNO. AF_12/2015 |
| LOC | COMPOSICAO | 92960 | CHP | 0,0144 | 22,54 | 0,324576 | MÁQUINA EXTRUSORA DE CONCRETO PARA GUIAS E SARJETAS, MOTOR A DIESEL, POTÊNCIA 14 CV - CHP DIURNO. AF_12/2015 |
| MO | COMPOSICAO | 88316 | H | 0,4078 | 26,14 | 10,659892 | SERVENTE COM ENCARGOS COMPLEMENTARES |
| MO | COMPOSICAO | 88309 | H | 0,2039 | 35,77 | 7,293503 | PEDREIRO COM ENCARGOS COMPLEMENTARES |
| MO | COMPOSICAO | 88243 | H | 0,0867 | 27,78 | 2,408526 | AJUDANTE ESPECIALIZADO COM ENCARGOS COMPLEMENTARES |
| OUT | COMPOSICAO | 88631 | M3 | 0,0016 | 841,00 | 1,345600 | ARGAMASSA TRAÇO 1:4 (EM VOLUME DE CIMENTO E AREIA MÉDIA ÚMIDA), PREPARO MANUAL. AF_07/2026 |
| OUT | INSUMO | 34492 | M3 | 0,0314 | 632,50 | 19,860500 | CONCRETO USINADO BOMBEAVEL, CLASSE DE RESISTENCIA C20, COM BRITA 0 E 1, SLUMP = 100 +/- 20 MM, EXCLUI SERVICO DE BOMBEAMENTO (NBR 8953) |
| OUT | INSUMO | 370 | M3 | 0,0066 | 139,00 | 0,917400 | AREIA MEDIA - POSTO JAZIDA/FORNECEDOR (RETIRADO NA JAZIDA, SEM TRANSPORTE) |
| | | | | | **Soma linhas** | **43,251139** | |
| | | | | | **Custo publicado** | **43,21** | campo `custo_nao_deson` |
| | | | | | **Residual** | **−0,041139** | ver §4.4 |

**Totais de grupo (não desonerado):**

| Grupo | Conta | R$/m |
|---|---|---:|
| Locação / CHI-CHP / equipamento extrusora | 0,0722×6,11 + 0,0144×22,54 | **0,765718** |
| Mão de obra 1º nível | 0,4078×26,14 + 0,2039×35,77 + 0,0867×27,78 | **20,361921** |
| Demais insumos | 0,0016×841,00 + 0,0314×632,50 + 0,0066×139,00 | **22,123500** |

Peso aproximado sobre a soma das linhas: equipamento **1,77%**; MO **47,08%**; demais **51,15%**. O concreto `34492` sozinho é R$ 19,86/m.

### 3.2 Desonerado

Equipamento e materiais de 1º nível (`34492`, `370`) **não mudam** de regime. Mudam MO e a argamassa auxiliar (porque a argamassa contém servente).

| Cl. | Tipo | Código | Und | Coef. | PU (R$) | Total linha (R$/m) | Descrição (ipsis verbis) |
|---|---|---|---|---:|---:|---:|---|
| LOC | COMPOSICAO | 92961 | CHI | 0,0722 | 6,11 | 0,441142 | MÁQUINA EXTRUSORA DE CONCRETO PARA GUIAS E SARJETAS, MOTOR A DIESEL, POTÊNCIA 14 CV - CHI DIURNO. AF_12/2015 |
| LOC | COMPOSICAO | 92960 | CHP | 0,0144 | 22,54 | 0,324576 | MÁQUINA EXTRUSORA DE CONCRETO PARA GUIAS E SARJETAS, MOTOR A DIESEL, POTÊNCIA 14 CV - CHP DIURNO. AF_12/2015 |
| MO | COMPOSICAO | 88316 | H | 0,4078 | 24,91 | 10,158298 | SERVENTE COM ENCARGOS COMPLEMENTARES |
| MO | COMPOSICAO | 88309 | H | 0,2039 | 33,84 | 6,899976 | PEDREIRO COM ENCARGOS COMPLEMENTARES |
| MO | COMPOSICAO | 88243 | H | 0,0867 | 26,44 | 2,292348 | AJUDANTE ESPECIALIZADO COM ENCARGOS COMPLEMENTARES |
| OUT | COMPOSICAO | 88631 | M3 | 0,0016 | 826,68 | 1,322688 | ARGAMASSA TRAÇO 1:4 (EM VOLUME DE CIMENTO E AREIA MÉDIA ÚMIDA), PREPARO MANUAL. AF_07/2026 |
| OUT | INSUMO | 34492 | M3 | 0,0314 | 632,50 | 19,860500 | CONCRETO USINADO BOMBEAVEL, CLASSE DE RESISTENCIA C20, COM BRITA 0 E 1, SLUMP = 100 +/- 20 MM, EXCLUI SERVICO DE BOMBEAMENTO (NBR 8953) |
| OUT | INSUMO | 370 | M3 | 0,0066 | 139,00 | 0,917400 | AREIA MEDIA - POSTO JAZIDA/FORNECEDOR (RETIRADO NA JAZIDA, SEM TRANSPORTE) |
| | | | | | **Soma linhas** | **42,216928** | |
| | | | | | **Custo publicado** | **42,18** | campo `custo_deson` |
| | | | | | **Residual** | **−0,036928** | ver §4.4 |

**Totais de grupo (desonerado):**

| Grupo | Conta | R$/m |
|---|---|---:|
| Locação / CHI-CHP / equipamento extrusora | 0,0722×6,11 + 0,0144×22,54 | **0,765718** |
| Mão de obra 1º nível | 0,4078×24,91 + 0,2039×33,84 + 0,0867×26,44 | **19,350622** |
| Demais insumos | 0,0016×826,68 + 0,0314×632,50 + 0,0066×139,00 | **22,100588** |

---

## 4. Abertura das auxiliares de equipamento (extrusora embutida)

A extrusora **não** entra como locação avulsa: entra como composições auxiliares `92960` (CHP) e `92961` (CHI). Abaixo, o analítico delas. Preços de equipamento **iguais** nos dois regimes.

### 4.1 `92960` — CHP diurno (R$ 22,54 / CHP)

Descrição: MÁQUINA EXTRUSORA DE CONCRETO PARA GUIAS E SARJETAS, MOTOR A DIESEL, POTÊNCIA 14 CV - CHP DIURNO. AF_12/2015  
Unidade: **CHP**. Coef. na `94263`: **0,0144 CHP/m**.

| Código | Und | Coef. em 92960 | PU (R$) | Contribuição no CHP (R$/h) | Contribuição na `94263` (R$/m) = 0,0144 × PU | Descrição |
|---|---|---:|---:|---:|---:|---|
| 92956 | H | 1,0 | 4,97 | 4,97 | 0,071568 | … DEPRECIAÇÃO. AF_12/2015 |
| 92957 | H | 1,0 | 1,14 | 1,14 | 0,016416 | … JUROS. AF_12/2015 |
| 92958 | H | 1,0 | 5,43 | 5,43 | 0,078192 | … MANUTENÇÃO. AF_12/2015 |
| 92959 | H | 1,0 | 11,00 | 11,00 | 0,158400 | … MATERIAIS NA OPERAÇÃO. AF_12/2015 |
| | | | **Soma** | **22,54** | **0,324576** | confere com PU publicado de 92960 |

### 4.2 `92961` — CHI diurno (R$ 6,11 / CHI)

Descrição: MÁQUINA EXTRUSORA DE CONCRETO PARA GUIAS E SARJETAS, MOTOR A DIESEL, POTÊNCIA 14 CV - CHI DIURNO. AF_12/2015  
Unidade: **CHI**. Coef. na `94263`: **0,0722 CHI/m**. CHI **não** remunera manutenção nem diesel (só depreciação + juros, máquina parada).

| Código | Und | Coef. em 92961 | PU (R$) | Contribuição no CHI (R$/h) | Contribuição na `94263` (R$/m) = 0,0722 × PU | Descrição |
|---|---|---:|---:|---:|---:|---|
| 92956 | H | 1,0 | 4,97 | 4,97 | 0,358834 | … DEPRECIAÇÃO. AF_12/2015 |
| 92957 | H | 1,0 | 1,14 | 1,14 | 0,082308 | … JUROS. AF_12/2015 |
| | | | **Soma** | **6,11** | **0,441142** | confere com PU publicado de 92961 |

### 4.3 Segundo nível — depreciação, juros, manutenção, diesel

**`92959` materiais na operação** (R$ 11,00 / H, ambos os regimes):

| Tipo | Código | Und | Coef. | PU (R$) | Total | Descrição |
|---|---|---|---:|---:|---:|---|
| INSUMO | 4221 | L | 1,55 | 7,10 | 11,005 → publicado 11,00 | OLEO DIESEL COMBUSTIVEL COMUM METROPOLITANO S-10 OU S-500 |

Diesel embutido na `94263`: `0,0144 h/m × 1,55 L/h = 0,02232 L/m` → `0,02232 × 7,10 = R$ 0,158472 / m` (fecha com 0,0144×11,00 = R$ 0,158400 no PU publicado de 92959; residual de R$ 0,000072/m na cadeia do diesel).

**`92956` / `92957` / `92958`** apontam o insumo de **aquisição** `13836`:

| Campo | Valor |
|---|---|
| Código | 13836 |
| Descrição | MAQUINA EXTRUSORA DE CONCRETO PARA GUIAS E SARJETAS, COM MOTOR A DIESEL E POTENCIA DE 14 CV |
| Unidade | UN |
| Tipo | EQUIPAMENTO (AQUISIÇÃO) |
| Preço BA 2026-07 | **SEM PREÇO — USO BLOQUEADO** (desonerado e não desonerado) |

Fail-closed: **não** reconstruir CHI/CHP a partir de `13836`. Os custos publicados de `92956` (R$ 4,97/H), `92957` (R$ 1,14/H), `92958` (R$ 5,43/H), `92960` e `92961` **são** os valores oficiais a usar. Coeficientes sobre `13836`: depreciação `6,4e-05`; juros `1,48e-05`; manutenção `7e-05` — registrados, mas o insumo está sem preço na UF.

### 4.4 Residual publicado vs soma das linhas

A soma `Σ (coef × PU armazenado com 2 casas)` da `94263` não desonerada é R$ 43,251139; o campo oficial é R$ 43,21 (Δ = −R$ 0,041139/m). No desonerado: R$ 42,216928 vs R$ 42,18 (Δ = −R$ 0,036928/m). O mesmo padrão (~R$ 0,03 a R$ 0,05) aparece em toda a família `94263`–`94272`.

Causa: o custo publicado da CAIXA é calculado na planilha oficial com cadeia de arredondamento própria; o SQLite guarda PU já arredondados em 2 casas. **Não foi feito ajuste artificial.** Para o recorte de locação e MO, a conta reproduzível é `coef × PU armazenado`. Para o custo direto total da composição (contexto de venda), usar o **campo publicado**.

---

## 5. Mão de obra — o que entra e o que não entra

### 5.1 1º nível da `94263` (resposta da pergunta 2)

Não desonerado:

```
servente  0,4078 h/m × R$ 26,14/h = R$ 10,659892/m
pedreiro  0,2039 h/m × R$ 35,77/h = R$  7,293503/m
ajud.esp. 0,0867 h/m × R$ 27,78/h = R$  2,408526/m
────────────────────────────────────────────────
MO 1º nível                         R$ 20,361921/m
```

Desonerado:

```
servente  0,4078 × 24,91 = R$ 10,158298/m
pedreiro  0,2039 × 33,84 = R$  6,899976/m
ajud.esp. 0,0867 × 26,44 = R$  2,292348/m
────────────────────────────────────────
MO 1º nível                R$ 19,350622/m
```

`88243` é “AJUDANTE ESPECIALIZADO COM ENCARGOS COMPLEMENTARES” — **não** há no analítico a palavra “operador”. Não foi inferido cargo além do texto oficial.

### 5.2 MO aninhada na argamassa `88631` (não somada no grupo MO)

`88631` foi classificada em **demais insumos** (é argamassa, não execução da guia). Internamente contém servente de preparo:

| | Não desonerado | Desonerado |
|---|---:|---:|
| Coef. de `88631` na `94263` | 0,0016 M3/m | 0,0016 M3/m |
| Coef. de `88316` na `88631` | 11,6386896 H/M3 | 11,6386896 H/M3 |
| Horas de servente aninhadas | 0,01862190336 h/m | 0,01862190336 h/m |
| PU servente | R$ 26,14 | R$ 24,91 |
| MO aninhada | **R$ 0,486777 / m** | **R$ 0,463872 / m** |

Se alguém somar essa parcela à MO de 1º nível (critério diferente, **não** adotado neste recorte): R$ 20,848698/m (ND) e R$ 19,814494/m (D). O grupo oficial de resposta permanece o 1º nível.

Analítico de `88631` não desonerado (R$ 841,00 / M3):

| Tipo | Código | Und | Coef. | PU (R$) | Descrição |
|---|---|---|---:|---:|---|
| COMPOSICAO | 88316 | H | 11,6386896 | 26,14 | SERVENTE COM ENCARGOS COMPLEMENTARES |
| INSUMO | 1379 | KG | 380,1934236 | 1,00 | CIMENTO PORTLAND COMPOSTO CP II-32 |
| INSUMO | 370 | M3 | 1,126499 | 139,00 | AREIA MEDIA - POSTO JAZIDA/FORNECEDOR (RETIRADO NA JAZIDA, SEM TRANSPORTE) |

Desonerado: mesmo coeficientes; `88316` a R$ 24,91; composição publicada R$ 826,68 / M3.

### 5.3 Encargos complementares (abertura de `88316` / `88309` / `88243`)

Já inclusos no PU horário usado acima. Não somar de novo. Não desonerado (cada um coef. 1,0 H):

| Composição | PU (R$/H) ND | PU (R$/H) D | Insumo-base horista ND |
|---|---:|---:|---|
| 88316 SERVENTE COM ENCARGOS COMPLEMENTARES | 26,14 | 24,91 | 6111 SERVENTE DE OBRAS (HORISTA) R$ 16,37 |
| 88309 PEDREIRO COM ENCARGOS COMPLEMENTARES | 35,77 | 33,84 | 4750 PEDREIRO (HORISTA) R$ 25,75 |
| 88243 AJUDANTE ESPECIALIZADO COM ENCARGOS COMPLEMENTARES | 27,78 | 26,44 | 242 AJUDANTE ESPECIALIZADO (HORISTA) R$ 18,15 |

Os PU incluem alimentação, transporte, exames, seguro, ferramentas, EPI e curso (encargos complementares CAIXA). Detalhamento conferido no script; não altera os totais de §3.

---

## 6. Família SINAPI com extrusora (alternativas relevantes)

Todas unidade **M**, grupo “Guias e sarjetas”, AF_01/2024, BA 2026-07. Locação = `92961`+`92960`; MO 1º nível = `88316`+`88309`+`88243`. Totais de grupo = `coef × PU` (ND / D). Equipamento com PU idêntico nos dois regimes.

| Código | Trecho / seção (ipsis verbis, resumida) | Publicado ND | Publicado D | Locação R$/m | MO 1º nível ND | MO 1º nível D |
|---|---|---:|---:|---:|---:|---:|
| **94263** | GUIA … TRECHO RETO … 13×22 cm **← paradigma** | **43,21** | **42,18** | **0,765718** | **20,361921** | **19,350622** |
| 94264 | GUIA … TRECHO CURVO … 13×22 cm | 48,82 | 47,53 | 1,163893 | 25,568879 | 24,299987 |
| 94265 | GUIA … TRECHO RETO … 15×30 cm | 59,14 | 58,02 | 0,877207 | 21,809796 | 20,726872 |
| 94266 | GUIA … TRECHO CURVO … 15×30 cm | 65,55 | 64,13 | 1,333170 | 27,775041 | 26,397022 |
| 94267 | GUIA E SARJETA CONJUGADOS … RETO … 45 cm (15+30) × 22 cm | 71,33 | 70,13 | 0,966849 | 22,979679 | 21,838882 |
| 94268 | idem CURVO 45×22 | 78,40 | 76,87 | 1,469371 | 29,547240 | 28,081552 |
| 94269 | conjugados RETO 60 cm (15+45) × 26 cm | 102,69 | 101,24 | 1,344399 | 27,937203 | 26,551162 |
| 94270 | conjugados CURVO 60×26 | 112,52 | 110,61 | 2,043965 | 37,076190 | 35,238052 |
| 94271 | conjugados RETO 65 cm (15+50) × 26 cm | 125,37 | 123,62 | 1,795664 | 33,832950 | 32,155252 |
| 94272 | conjugados CURVO 65×26 | 138,49 | 136,15 | 2,728215 | 46,036040 | 43,754657 |

Descrições oficiais integrais de `94264`–`94272` estão no SQLite (busca `EXTRUSORA`); não foram parafraseadas para precificar.

CHI/CHP da máquina (mesmo PU em todos):

| Código | Und | PU ND = PU D | Descrição |
|---|---|---:|---|
| 92960 | CHP | 22,54 | … CHP DIURNO. AF_12/2015 |
| 92961 | CHI | 6,11 | … CHI DIURNO. AF_12/2015 |
| 92956 | H | 4,97 | … DEPRECIAÇÃO. AF_12/2015 |
| 92957 | H | 1,14 | … JUROS. AF_12/2015 |
| 92958 | H | 5,43 | … MANUTENÇÃO. AF_12/2015 |
| 92959 | H | 11,00 | … MATERIAIS NA OPERAÇÃO. AF_12/2015 |

---

## 7. Analogismo `94267` (guia + sarjeta conjugados) — se o objeto for drenagem

Não é canaleta. É o item **com extrusora** cuja geometria mais se aproxima de uma seção de drenagem longitudinal (guia 15 cm + sarjeta 30 cm).

Descrição: GUIA (MEIO-FIO) E SARJETA CONJUGADOS DE CONCRETO, MOLDADA IN LOCO EM TRECHO RETO COM EXTRUSORA, 45 CM BASE (15 CM BASE DA GUIA + 30 CM BASE DA SARJETA) X 22 CM ALTURA. AF_01/2024  
Unidade **M**. Publicado: **R$ 71,33 / m** (ND) e **R$ 70,13 / m** (D).

| Grupo | Não desonerado | Desonerado | Conta (ND) |
|---|---:|---:|---|
| Locação / CHI-CHP | **0,966849** | **0,966849** | 0,0911×6,11 + 0,0182×22,54 |
| MO 1º nível | **22,979679** | **21,838882** | 0,453×26,14 + 0,2265×35,77 + 0,1093×27,78 (ND) |
| Demais insumos | 47,413650 | 47,366394 | 0,0033×841,00 + 0,0673×632,50 + 0,0149×139,00 (ND) |
| Soma linhas | 71,360178 | 70,172125 | |
| Publicado | **71,33** | **70,13** | |

Analítico ND (script): `92961` 0,0911 CHI; `92960` 0,0182 CHP; `88631` 0,0033 M3; `88316` 0,453 H; `88309` 0,2265 H; `88243` 0,1093 H; `34492` 0,0673 M3; `370` 0,0149 M3.

Usar `94267` no lugar de uma canaleta exige De-Para humano (seção, armação, grelha, fôrma). Sem isso, permanece bloqueio de substituição.

---

## 8. O que **não** é execução com extrusora (não misturar)

### 8.1 Sarjetas moldadas in loco com fôrma de madeira (sem extrusora)

Família `94281`–`94292`, unidade M. Analítico-tipo (`94287`): pedreiro + servente + concreto `34492` + tábua `6212` + sarrafo `4517` + areia `370`. **Não** há `92960`/`92961`.

| Código | Publicado ND | Publicado D | Descrição (ipsis verbis) |
|---|---:|---:|---|
| 94287 | 41,70 | 40,96 | EXECUÇÃO DE SARJETA DE CONCRETO USINADO, MOLDADA IN LOCO EM TRECHO RETO, 30 CM BASE X 10 CM ALTURA. AF_01/2024 |
| 94281 | 55,32 | 54,53 | … TRECHO RETO, 30 CM BASE X 15 CM ALTURA. AF_01/2024 |
| 94288 | 49,89 | 48,74 | … TRECHO CURVO, 30×10. AF_01/2024 |
| 94282 | 64,54 | 63,28 | … TRECHO CURVO, 30×15. AF_01/2024 |
| 94289 | 54,55 | 53,79 | … RETO, 45×10 |
| 94283 | 75,55 | 74,68 | … RETO, 45×15 |
| 94290 | 62,75 | 61,57 | … CURVO, 45×10 |
| 94284 | 84,78 | 83,43 | … CURVO, 45×15 |
| 94291 | 68,03 | 67,23 | … RETO, 60×10 |
| 94285 | 98,65 | 97,54 | … RETO, 60×15 |
| 94292 | 76,23 | 75,02 | … CURVO, 60×10 |
| 94286 | 107,88 | 106,29 | … CURVO, 60×15 |

### 8.2 Canaletas SINAPI (outra família — sem extrusora)

Consulta `CANALETA` no script limita 20 linhas; o SQL read-only listou o conjunto completo. Nenhum item abaixo tem extrusora.

**Pré-moldada meia-cana (fornecimento + instalação), unidade M:**

| Código | ND | D | Descrição |
|---|---:|---:|---|
| 102989 | 44,06 | 43,27 | CANALETA MEIA CANA PRÉ-MOLDADA DE CONCRETO (D = 20 CM) - FORNECIMENTO E INSTALAÇÃO. AF_05/2025 |
| 102990 | 55,53 | 54,50 | … (D = 30 CM) … |
| 102991 | 73,14 | 71,76 | … (D = 40 CM) … |
| 102992 | 106,21 | 105,15 | … (D = 50 CM) … |
| 102993 | 138,11 | 136,73 | … (D = 60 CM) … |
| 102994 | 257,68 | 255,09 | … (D = 80 CM) … |
| 103004 | SEM PREÇO — USO BLOQUEADO | SEM PREÇO | CANALETA DE CONCRETO POLIMÉRICO COM GRELHA, LARGURA DE 13 CM - FORNECIMENTO E INSTALAÇÃO. AF_05/2025 |

**Moldada in loco com fôrma/armação (não extrusora), unidade M** — exemplo `106004` = R$ 211,64/m ND (fôrma + aço + concretagem). Demais: `106005` a `106016` (quadrada / retangular com grelha), publicados de R$ 250,43 a R$ 1.893,68 (ND). `105944` é concretagem em **M3** (R$ 1.008,42 ND / R$ 988,48 D), não ml.

**Bloco canaleta de alvenaria** (`93191`, `93199`, `93205`, `105025`–`105034`): verga/contraverga/cinta — fora do escopo viário.

**Sem preço na UF (bloqueados item a item):** `103004`, `106017` (pré-moldada com grelha, unidade UN), `106265` (canaleta de quadro de bomba).

`102995` (canaleta trapezoidal citada em índice Markdown antigo) **não existe** no SINAPI 2026-07 importado (`Nenhum registro encontrado`).

---

## 9. Preço de venda (o que não foi feito)

```
preço_de_venda = custo_direto_SINAPI × (1 + BDI)
```

- Custo direto paradigma `94263`: **R$ 43,21/m** (ND) ou **R$ 42,18/m** (D), campo publicado.
- BDI: **não calculado**. Depende de edital, regime tributário, localidade e Acórdão 2622/2013-TCU.
- Não há BDI diferenciado nesta composição (não é mero fornecimento de equipamento).
- Locação de mercado, mobilização, operador avulso, lucro e taxa de administração **não** foram estimados.

Se a obra locar a extrusora, o teto que a tabela **remunera** para a máquina no paradigma é **R$ 0,765718/m** (CHI+CHP). Ultrapassar isso é gap comercial versus SINAPI, não número deste recorte.

---

## 10. Reprodutibilidade

```bash
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94263 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94263 --fonte SINAPI --regime desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 92960 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 92961 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 92956 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 92957 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 92958 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 92959 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88631 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py EXTRUSORA --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py CANALETA --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94267 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 13836 --fonte SINAPI --regime nao_desonerado
```

Conta-mestra do paradigma (não desonerado):

```
LOC = 0.0722*6.11 + 0.0144*22.54 = 0.765718
MO  = 0.4078*26.14 + 0.2039*35.77 + 0.0867*27.78 = 20.361921
OUT = 0.0016*841.00 + 0.0314*632.50 + 0.0066*139.00 = 22.123500
SUM = 43.251139
PUB = 43.21
```

`FONTES_DADOS.json` **não** foi alterado. Nenhum preço fora do script/SQLite foi lançado.
