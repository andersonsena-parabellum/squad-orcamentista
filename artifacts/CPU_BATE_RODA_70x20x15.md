# CPU PRP-BTR-001 — Bate-roda de concreto 70 × 20 × 15 cm

**Status da ficha:** `MODELO ANALÍTICO — USO DIRETO BLOQUEADO`  
**Motivo do bloqueio de preço total:** o insumo da peça pré-moldada 70 × 20 × 15 cm **não existe** na SINAPI BA 2026-07 com preço positivo; cotação (Etapa 7 / DC-007) **não foi executada** (proibido envio de e-mail).  
**Não entra em catálogo oficial.** Artefato avulso em `artifacts/`. Não altera `FONTES_DADOS.json`.

---

## 0. Preflight do repositório

Comando:

```bash
python3 scripts/validate_repository.py
```

Resultado (2026-09-17T09:43:05.166989+00:00):

| Campo | Valor |
|---|---|
| `gate` | **`LIBERADO`** |
| `restricoes_ativas` | 5 (todas P1) |
| P1 | `PRECEDENTES_NAO_LIBERADOS` = `QUARENTENADA` |
| P1 | `FONTE_NAO_LIBERADA` = `ORSE_LEGADO_QUARENTENA` |
| P1 | `COMPOSICOES_SEM_PRECO_NA_UF` = 2144 |
| P1 | `INSUMOS_SEM_PRECO_NA_UF` = 1672 |
| P1 | `COEFICIENTES_NAO_POSITIVOS` = 4 |

As restrições P1 **não** paralisam este escopo: a fonte **SINAPI** está `LIBERADA` para consulta, paradigma de CPU e preço direto na BA. Cada linha sem preço positivo na UF permanece bloqueada individualmente. O corpus SUPAT em quarentena **não** foi citado como exigência.

---

## 1. Identificação

| Campo | Valor |
|---|---|
| Código sugerido | `PRP-BTR-001` |
| Descrição oficial proposta | `BATE-RODA DE CONCRETO PRÉ-MOLDADO 70 × 20 × 15 CM — FORNECIMENTO E ASSENTAMENTO COM ARGAMASSA, SOBRE PISO EXISTENTE` |
| Unidade | `UN` |
| Dimensão | 70 × 20 × 15 cm |
| Volume unitário (informativo) | **0,021 m³** = 0,70 × 0,20 × 0,15 |
| Massa aproximada (informativa) | ~50 kg se γ = 2.400 kg/m³ — **não usada para precificar** |
| Regime adotado na ficha | **não desonerado** (comparativo desonerado na seção 8) |
| UF / competência / fonte | BA / 2026-07 / SINAPI `LIBERADA` |
| BDI | não aplicável nesta ficha (custo direto) |
| Disciplina típica | urbanização / estacionamento / sinalização de piso |

O volume 0,021 m³ **não converte** esta CPU para m³. A unidade remunerada é `UN`. O volume só sustenta (a) a comparação geométrica com o paradigma 94275 e (b) a hipótese B (moldado in loco), que permanece incompleta.

---

## 2. Cascata de preços aplicada

| Etapa | Resultado |
|---|---|
| **0 — Fontes** | Serviço especificado: bate-roda de concreto 70 × 20 × 15 cm, UN. Sem LI/projeto desta tarefa. |
| **1 — SINAPI exato** | Existe `103734` “FORNECIMENTO E INSTALAÇÃO DE BATE RODAS SOBRE ASFALTO. AF_03/2022”, UN. **Não serve como preço direto:** (i) o insumo é **resina com pinos**, não concreto; (ii) execução **sobre asfalto** com martelete e adesivo; (iii) custo BA **SEM PREÇO — USO BLOQUEADO** (insumos 44729 e 44737 sem preço). |
| **2 — SINAPI adaptável** | **Adotada na hipótese A (recomendada).** Copia mão de obra, argamassa e perda da peça da família AF_01/2024, composição `94275` (assentamento de guia pré-fabricada de concreto). Troca só o insumo da peça. |
| **2b — Sugestão ao projetista** | **Não adotada.** Substituir bate-roda por meio-fio 41679 mudaria a função (contenção linear ≠ batente de roda). |
| **3 — ORSE paradigma** | **Não utilizada.** Partição `ORSE` no SQLite = 0 registros; script oficial exigiu `bs4` (ausente). Cache local não contém bate-roda. Preço ORSE direto fora de SE continuaria condicionado. |
| **4 — CPU catálogo** | Modelo estrutural `PRH.019` (bate-roda 50 × 15 × 8 cm). Uso como modelo `LIBERADO`; uso direto `BLOQUEADO_ATE_REVALIDACAO`. Coeficiente histórico 0,3 H de servente **não** foi copiado (exige revalidação; não é caderno SINAPI). |
| **5/6 — CPU nova** | Esta ficha. Coeficientes oficiais da 94275 + peça COT bloqueada. |
| **7 — Cotação** | **Não executada.** Peça marcada `BLOQUEADO`. |
| **8 — Minuta de e-mail** | **Não redigida / não enviada.** |

---

## 3. Duas hipóteses técnicas (ambiguidade material)

A especificação “bate-roda de concreto 70 × 20 × 15 cm” é, no mercado, uma **peça pré-moldada comercial**. Também é possível moldar in loco o mesmo prisma. As duas hipóteses ficam registradas. **Preço inventado: zero.**

### Hipótese A — RECOMENDADA — pré-moldado + assentamento (UN)

- Fornecimento da peça 70 × 20 × 15 cm + assentamento sobre **piso existente**.
- Junta/colchão de **argamassa 1:3** (SINAPI 88629), copiada da 94275.
- Mão de obra SINAPI **88309** (pedreiro) e **88316** (servente), coeficientes oficiais da 94275.
- **Não inclui:** vala, lastro de areia 370, pintura, chumbador metálico, furação de asfalto, armação, forma, concreto usinado.

**Por que A e não a 103734:** a 103734 é bate-roda de **resina** sobre **asfalto**, com pinos, adesivo e martelete. A peça pedida é **concreto**. A 103734 permanece evidência de que o SINAPI trata “bate rodas” em UN, e reserva de MO caso o projeto seja asfalto+pinos (seção 6).

**Por que A e não usar 41679 como peça:** o insumo 41679 é meio-fio 1,00 m × 20 × 12/15 cm. Dimensão e função diferentes. Preço R$ 25,25/UN **não** pode ser adotado como proxy.

### Hipótese B — NÃO RECOMENDADA PARA PREÇO — moldado in loco

- Prisma 0,70 × 0,20 × 0,15 m = 0,021 m³ de concreto.
- Insumo de produção `94964` (concreto FCK 20 MPa, betoneira 400 L) tem preço BA positivo: R$ 639,03/m³ × 0,021 = **R$ 13,42** (não desonerado) — isso é **só preparo** do concreto, sem lançamento, forma nem acabamento.
- Composições de concretagem disponíveis (`96555` bloco de coroamento FCK 30 com jerica; `94263` guia moldada com **extrusora**; `105021` verga pré-moldada com aço e forma de viga) **não** descrevem este prisma isolado. Copiá-las exigiria coeficiente de forma/reuso e/ou armação **não evidenciados** para bate-roda.
- **Veredito B:** ficha de execução in loco **BLOQUEADA** até decisão humana de paradigma de forma + lançamento. Não se inventam horas.

---

## 4. Paradigma geométrico da hipótese A (94275)

Composição paradigma (consulta CLI, fonte SINAPI, regime não desonerado):

`94275` — ASSENTAMENTO DE GUIA (MEIO-FIO) EM TRECHO RETO, CONFECCIONADA EM CONCRETO PRÉ-FABRICADO, DIMENSÕES 100X15X13X20 CM (COMPRIMENTO X BASE INFERIOR X BASE SUPERIOR X ALTURA). AF_01/2024  
Unidade: **M** | Grupo: Guias e sarjetas | **R$ 40,71** (BA 2026-07, não desonerado)

| Grandeza | 94275 (por m = 1 peça de 1,00 m) | PRP-BTR-001 (1 UN = 1 peça) |
|---|---|---|
| Área de contato no piso | 1,00 × (0,15+0,13)/2 = **0,14 m²** | 0,70 × 0,20 = **0,14 m²** |
| Volume da peça | 1,00 × 0,14 × 0,20 = **0,028 m³** | **0,021 m³** |
| Argamassa 88629 | 0,0012 m³/m → ~8,6 mm sobre 0,14 m² | **0,0012 m³/UN** (mesma área de contato) |
| Pedreiro / servente | 0,2151 H/m cada | **0,2151 H/UN** cada (mesmo contato; peça ~25% mais leve) |
| Perda da peça | 1,005 | **1,005** (mesmo fator AF_01/2024) |
| Areia 370 | 0,0066 m³/m (leito de vala de guia) | **excluída** (assento sobre piso existente) |

Não se converteu M→UN por 0,70 m de comprimento: a área de junta é idêntica à do metro da 94275. Converter por 0,70 subestimaria argamassa e MO sem evidência de caderno.

A 94275 **não é lançada como serviço** nesta CPU (seria meio-fio). Só se copiam coeficientes oficiais e se troca o material da peça.

---

## 5. Quadro analítico — hipótese A recomendada

**Unidade da CPU:** 1 UN  
**Regime:** não desonerado  
**Fonte / UF / competência:** SINAPI BA 2026-07  
**Totais de linha:** `ROUND(coeficiente × preço_unitário, 2)` com os preços devolvidos pelo script.

| Tipo | Banco | Código | Descrição (*ipsis verbis* da consulta, ou proposta COT) | Und | Coef. | Origem do coef. | Preço unit. BA | Regime | Competência | Total linha | Status |
|---|---|---|---|---|---:|---|---:|---|---|---:|---|
| MO (comp. aux.) | SINAPI | `88309` | PEDREIRO COM ENCARGOS COMPLEMENTARES | H | 0,2151 | 94275 | R$ 35,77 | nao_desonerado | 2026-07 | R$ 7,69 | PRECIFÍCÁVEL |
| MO (comp. aux.) | SINAPI | `88316` | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0,2151 | 94275 | R$ 26,14 | nao_desonerado | 2026-07 | R$ 5,62 | PRECIFÍCÁVEL |
| Comp. aux. | SINAPI | `88629` | ARGAMASSA TRAÇO 1:3 (EM VOLUME DE CIMENTO E AREIA MÉDIA ÚMIDA), PREPARO MANUAL. AF_07/2026 | M3 | 0,0012 | 94275 | R$ 938,86 | nao_desonerado | 2026-07 | R$ 1,13 | PRECIFÍCÁVEL |
| Insumo | COT | `COT-BTR-70X20X15` | BATE-RODA DE CONCRETO PRÉ-MOLDADO 70 × 20 × 15 CM | UN | 1,005 | perda 94275 / AF_01/2024 | — | — | — | — | **BLOQUEADO** |

**Parcela precificável (sem a peça):** R$ 7,69 + R$ 5,62 + R$ 1,13 = **R$ 14,44 / UN** (custo direto, sem BDI).  
**Custo direto total da CPU:** **BLOQUEADO** — falta preço da peça com evidência (Etapa 7: três fornecedores com CNPJ, mediana FOB, DC-007).

A argamassa `88629` já embute servente de preparo (coef. 12,3150605 H/m³ na própria composição). Não se soma outra hora de preparo.

### Linhas deliberadamente fora da CPU A

| Código | Motivo da exclusão |
|---|---|
| `370` AREIA MEDIA | Leito de vala da guia 94275; premissa A é piso existente. |
| `41679` MEIO-FIO … 20 X 12/15 CM | Peça de função e dimensão diferentes. Preço R$ 25,25 **não** é proxy. |
| `103734` / `44729` / `44737` / `102274` / `102275` | Família resina + asfalto + pinos + martelete. Ver seção 6. |
| `102498` PINTURA DE MEIO-FIO (caiação) | Pintura de guia com cal, por metro; não é acabamento de bate-roda. |
| `94964` concreto FCK 20 | Pertence à hipótese B (produção in loco). |

---

## 6. Evidência SINAPI de mão de obra (obrigatória)

Nenhuma hora foi inventada. Os códigos de MO são composições SINAPI com encargos complementares.

### 6.1 Coeficientes adotados (94275) — hipótese A

Consulta: `python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94275 --fonte SINAPI --regime nao_desonerado`

```
COMPOSICAO 88316 | H | coef. 0.2151 | R$ 26,14 | SERVENTE COM ENCARGOS COMPLEMENTARES
COMPOSICAO 88309 | H | coef. 0.2151 | R$ 35,77 | PEDREIRO COM ENCARGOS COMPLEMENTARES
```

Consulta direta dos códigos de MO:

```
[FONTE LIBERADA] SINAPI 88309 — PEDREIRO COM ENCARGOS COMPLEMENTARES
UF BA | competência 2026-07 | Unidade: H | R$ 35,77

[FONTE LIBERADA] SINAPI 88316 — SERVENTE COM ENCARGOS COMPLEMENTARES
UF BA | competência 2026-07 | Unidade: H | R$ 26,14
```

### 6.2 Coeficientes da 103734 — reserva (não adotados na A)

Consulta: `python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 103734 --fonte SINAPI --regime nao_desonerado`  
Saída: composição **SEM PREÇO — USO BLOQUEADO**, mas o analítico oficial existe:

| Código | Und | Coef. | Preço unit. BA (não desonerado) | Descrição | Uso nesta ficha |
|---|---|---:|---|---|---|
| `88316` | H | 0,2599 | R$ 26,14 | SERVENTE COM ENCARGOS COMPLEMENTARES | Reserva se execução = asfalto+pinos |
| `88309` | H | 0,0113 | R$ 35,77 | PEDREIRO COM ENCARGOS COMPLEMENTARES | Idem |
| `102275` | CHP | 0,0137 | R$ 43,63 | MARTELO DEMOLIDOR ELÉTRICO … 30 KG - CHP DIURNO. AF_01/2021 | Só asfalto; não entra na A |
| `102274` | CHI | 0,0353 | R$ 40,77 | MARTELO DEMOLIDOR ELÉTRICO … 30 KG - CHI DIURNO. AF_01/2021 | Só asfalto; não entra na A |
| `44737` | UN | 0,218 | SEM PREÇO | ADESIVO (COLA) DE RESINA COM CATALISADOR | **BLOQUEADO** |
| `44729` | UN | 1,0 | SEM PREÇO | BATE-RODAS DE RESINA COM DOIS PINOS DE FIXACAO | **BLOQUEADO** (material errado) |

Parcela de MO+equipamento da 103734, se um dia o projeto for asfalto: R$ 6,79 + R$ 0,40 + R$ 0,60 + R$ 1,44 = **R$ 9,23 / UN**, ainda **sem** peça e adesivo (ambos bloqueados).

### 6.3 Modelo de catálogo PRH.019 — não revalidado

`consultar_cpu_propria.py bate-roda` → `PRH.019` | UN | BATE-RODA 50×15×8 cm — FORNECIMENTO E FIXAÇÃO  
Referência declarada: `REF. SINAPI 88316 (fixação de peça pré-moldada)`  
Itens: 88316 coef. **0,3 H** + insumo próprio `INS.035`.  
`uso_direto = BLOQUEADO_ATE_REVALIDACAO`. O 0,3 H **não** foi usado.

---

## 7. Premissas explícitas (hipótese A)

1. A peça é **pré-moldada de concreto**, dimensões 70 × 20 × 15 cm, fornecida pronta.
2. Assentamento **sobre piso existente** (concreto, intertravado ou equivalente), sem vala.
3. Fixação por **argamassa 1:3** (88629), não por pinos/resina/chumbador.
4. Sem pintura (faixa amarela etc.). Se o projeto exigir, é item à parte — não usar 102498 (caiação de meio-fio).
5. Sem armação, forma, concreto usinado ou extrusora.
6. Quantidade na planilha = **líquida em UN**. A perda 0,5% (coef. 1,005) fica **dentro** da CPU, copiada da 94275.
7. Areia 370 da 94275 **não** entra.
8. Frete da peça, descarga e içamento mecanizado: fora do escopo (a 94275 também não traz caminhão).
9. Se o projeto for **asfalto + pinos**, abandonar esta CPU e reabrir a família 103734 (ainda bloqueada nos insumos).

---

## 8. Comparativo desonerado (somente linhas precificáveis)

Mesmos coeficientes; preços do script `--regime desonerado`.

| Código | Coef. | Preço unit. desonerado | Total linha |
|---|---:|---:|---:|
| 88309 | 0,2151 | R$ 33,84 | R$ 7,28 |
| 88316 | 0,2151 | R$ 24,91 | R$ 5,36 |
| 88629 | 0,0012 | R$ 923,71 | R$ 1,11 |
| **Parcela precificável** | | | **R$ 13,75** |
| Peça COT | 1,005 | — | **BLOQUEADO** |

A ficha oficial desta CPU permanece no regime **não desonerado**, alinhada ao uso mais comum em obras públicas da pasta. Troca de regime é decisão de obra, não desta ficha.

Insumo 41679 (não usado): R$ 25,25 nos dois regimes.

---

## 9. Hipótese B — quadro incompleto (não precificar)

Volume: 0,70 × 0,20 × 0,15 = **0,021 m³/UN**.

| Código | Papel | Evidência | Status |
|---|---|---|---|
| `94964` CONCRETO FCK = 20MPA … BETONEIRA 400 L | Produção do concreto | R$ 639,03/m³ × 0,021 = R$ 13,42 (não desonerado). Desonerado: R$ 631,72/m³. A 94964 **já contém** servente 2,5333 H/m³ e operador de betoneira — só preparo. | PRECIFÍCÁVEL isoladamente; **não fecha** o serviço |
| `92270` FABRICAÇÃO DE FÔRMA PARA VIGAS … E = 25 MM | Forma | Área lateral do prisma = 2×(0,70×0,15)+2×(0,20×0,15) = **0,27 m²**, sem fundo (piso existente). Falta fator de reuso do caderno de formas. 105021 usa 0,04 m²/m para verga — outra peça. | **BLOQUEADO** (coef. de reuso sem evidência) |
| `88309` / `88316` lançamento | MO de concretagem | 96555 (bloco de coroamento FCK 30 + jerica) e 94263 (guia com extrusora) são serviços distintos. | **BLOQUEADO** (horas não copiadas de serviço incompatível) |
| Armação | — | Bate-roda comercial típico é não armado; 105021 inclui CA-50. Sem projeto estrutural. | Fora / não inventar |

**Veredito B:** `BLOQUEADO`. Não publicar preço in loco.

---

## 10. Buscas realizadas (catálogo, SINAPI, SQL)

### 10.1 Catálogo CPU (`consultar_cpu_propria.py`)

| Termo | Resultado relevante |
|---|---|
| `bate-roda` | **PRH.019** UN — BATE-RODA 50×15×8 cm (modelo; uso direto bloqueado) |
| `guia` / `meio-fio` | nenhum |
| `pré-moldado` / `pre-moldado` | PRH.003 pisante 60×60; PRH.004 banco |
| `assentamento` | PRH.003, PRH.015, PRH.017, PRH.047 |
| `concreto` | PRH.054 base 40×40×20 (MO 0,25/0,4 H **não revalidadas** + insumo próprio); PRH.060/061 usam 94964 |

Não há CPU catalogada 70 × 20 × 15 cm.

### 10.2 Script `consultar_composicao.py` (SINAPI)

Códigos consultados com `--fonte SINAPI` e `--regime nao_desonerado` (e desonerado nos da seção 8):  
`103734`, `94275`, `94273`, `94277`, `94279`, `94294`, `103296`, `103293`, `103300`, `105021`, `105022`, `94964`, `88309`, `88316`, `88629`, `41679`, `44729`, `44737`, `370`, `92270`, `96555`, `102274`, `102275`, `102498`.

Busca textual: `BATE RODA` → só 103734. `BATE-RODA` → nenhum. `BATE` → ruído de “batente”.

### 10.3 SQL somente leitura (documentado)

Banco: `03-BASE_DE_PRECOS/base_precos.db` (SHA-256 conferido, seção 11).

```sql
-- composições SINAPI de bate-roda / meio-fio / guia
SELECT codigo, unidade, grupo, custo_nao_deson, descricao
FROM composicoes
WHERE fonte = 'SINAPI'
  AND (
    descricao LIKE '%BATE RODA%' OR descricao LIKE '%BATE-RODA%'
    OR descricao LIKE '%MEIO-FIO%' OR descricao LIKE '%MEIO FIO%'
    OR descricao LIKE '%GUIA (MEIO%'
  )
ORDER BY codigo;

-- insumos SINAPI de bate-roda / guia de concreto
SELECT codigo, unidade, tipo, preco_nao_deson, descricao
FROM insumos
WHERE fonte = 'SINAPI'
  AND (
    UPPER(descricao) LIKE '%BATE-RODA%'
    OR UPPER(descricao) LIKE '%BATE RODA%'
    OR UPPER(descricao) LIKE '%MEIO-FIO%'
    OR (UPPER(descricao) LIKE '%GUIA%' AND UPPER(descricao) LIKE '%CONCRETO%')
  )
ORDER BY codigo;

-- ORSE na partição local (resultado: 0 composições)
SELECT count(*) FROM composicoes WHERE fonte = 'ORSE';
```

Achados materiais extra (não usados como preço):

- `103296` INSTALAÇÃO DE BALIZADOR PRÉ-FABRICADO DE CONCRETO … SOBRE PISO DE CONCRETO EXISTENTE — UN, **SEM PREÇO** (insumo 44452 bloqueado). MO 1,2308 H servente + 1,8461 H pedreiro + martelete + concreto FCK 15 de chumbamento. Serviço mais pesado (peça 30×60 cm chumbada). Não copiado.
- Família 94273–94280: assentamento de guias pré-fabricadas com preço BA positivo.
- Insumo `44729` BATE-RODAS DE RESINA COM DOIS PINOS DE FIXACAO — **SEM PREÇO**.

---

## 11. Proveniência, hashes e competência

De `03-BASE_DE_PRECOS/FONTES_DADOS.json` (não alterado). Hashes conferidos em 2026-09-17 contra os arquivos locais:

| Artefato | Status | Competência | SHA-256 |
|---|---|---|---|
| SQLite `base_precos.db` | índice válido | schema 2.0.0 | `a59957251f947dc83f7439d379fbbd1bc1b6d08337fe0cf776d174aff747be34` |
| ZIP SINAPI origem | `LIBERADA` | 2026-07 | `58c131f997560332cf2d7f7f90644790d5c6e2a909a2963b18f136779312b14f` |
| `CATALOGO_CPU_PROPRIAS.json` | modelo `LIBERADA`; preço direto bloqueado até revalidação | CATALOGO-2026-09-05 | `6040320ea4a55e2f511f497785613fca585a6e97eb2a365dd5d574f70db73f35` |
| JSON original PRH.019 | origem do modelo 50×15×8 | Praça do Hospital R01 | `23fceea78548ce3255ae470bbe64073283617de542b677de5081ea61048797fa` |

URL oficial SINAPI registrada: `https://www.caixa.gov.br/Downloads/sinapi-relatorios-mensais/SINAPI-2026-07-formato-xlsx.zip`.

Capacidades SINAPI: `consulta`, `paradigma_cpu` e `preco_direto` = `LIBERADA`. Linha sem preço positivo na UF continua bloqueada (caso 103734 / 44729 / 44737).

---

## 12. Comandos de consulta (reprodução)

```bash
python3 scripts/validate_repository.py

python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py bate-roda
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py guia
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py "meio-fio"
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py "pré-moldado"
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py "pre-moldado"
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py bloco
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py assentamento
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py concreto

python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 103734 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 103734 --fonte SINAPI --regime desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py "BATE RODA" --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94275 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88309 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88316 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88629 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 44729 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94964 --fonte SINAPI --regime nao_desonerado
```

ORSE: `consultar_orse_oficial.py "bate-roda"` falhou com `ModuleNotFoundError: No module named 'bs4'`. Não foi instalado pacote para forçar consulta. SQL local `fonte='ORSE'` = 0 linhas.

---

## 13. Gate desta ficha (fail-closed)

| Controle | Resultado |
|---|---|
| Repositório `validate_repository.py` | `LIBERADO` (P1 conhecidas) |
| Fonte de cada linha de preço | SINAPI BA 2026-07 `LIBERADA`, hash conferido |
| Mão de obra | Códigos SINAPI 88309 e 88316; coeficientes da 94275 (não inventados) |
| Peça 70 × 20 × 15 cm | **BLOQUEADO** — sem código SINAPI correspondente com preço > 0 |
| Hipótese B (in loco) | **BLOQUEADO** — forma e lançamento sem paradigma compatível |
| Cotação / e-mail | não executados |
| `FONTES_DADOS.json` | não alterado |
| Catálogo oficial CPU | não alterado |
| Uso direto em planilha de envio | **BLOQUEADO** até DC-007 da peça + revalidação humana |

**Para destravar uso direto:** (1) três cotações da peça com CNPJ e âncora 70 × 20 × 15 cm, mediana FOB no DC-007; (2) confirmar premissa de assentamento (argamassa em piso × pinos em asfalto); (3) revalidar coeficientes no projeto; (4) se asfalto+pinos, reciclar 103734 e cotar também adesivo 44737.

Espelho JSON: `artifacts/CPU_BATE_RODA_70x20x15.json`.
