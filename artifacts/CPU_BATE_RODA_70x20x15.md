# CPU PRP-BTR-001 — Bate-roda de concreto 70 × 20 × 15 cm

**Status da ficha:** `PRECIFÍCÁVEL — PROXY VOLUMÉTRICO (Etapa 2 / de-para funcional)`  
**Custo direto total (hipótese A, não desonerado, sem BDI):** **R$ 34,18 / UN**  
**Isto não é SINAPI exato de bate-roda 70 × 20 × 15 cm.** A peça é o insumo SINAPI `41679` (meio-fio/guia pré-moldada), convertido por volumetria. Função meio-fio ≠ bate-roda: risco registrado, **preço não bloqueado** (determinação explícita desta revisão).  
**Não entra em catálogo oficial.** Artefato avulso em `artifacts/`. Não altera `FONTES_DADOS.json`. Sem COT. Sem e-mail.

---

## 0. Preflight do repositório

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

SINAPI BA 2026-07 permanece `LIBERADA` para consulta, paradigma e preço direto. Corpus SUPAT em quarentena não foi citado como exigência.

---

## 1. Identificação

| Campo | Valor |
|---|---|
| Código sugerido | `PRP-BTR-001` |
| Descrição oficial proposta | `BATE-RODA DE CONCRETO PRÉ-MOLDADO 70 × 20 × 15 CM — FORNECIMENTO E ASSENTAMENTO COM ARGAMASSA, SOBRE PISO EXISTENTE` |
| Unidade | `UN` |
| Dimensão alvo | 70 × 20 × 15 cm |
| Volume alvo | **0,021 m³** = 0,70 × 0,20 × 0,15 |
| Peça SINAPI (proxy) | `41679` — MEIO-FIO OU GUIA DE CONCRETO PRE-MOLDADO, COMP 1 M, *20 X 12/15* CM (H X L1/L2) |
| Regime da ficha | **não desonerado** (desonerado no anexo, seção 9) |
| UF / competência / fonte | BA / 2026-07 / SINAPI `LIBERADA` |
| BDI | não aplicável (custo direto) |

A unidade remunerada da CPU é `UN` (1 bate-roda). O volume só define o coeficiente do insumo `41679`.

---

## 2. Cascata de preços aplicada

| Etapa | Resultado |
|---|---|
| **0 — Fontes** | Serviço: bate-roda de concreto 70 × 20 × 15 cm, UN. |
| **1 — SINAPI exato** | `103734` é bate-rodas de **resina** sobre asfalto, UN, **SEM PREÇO** (44729 e 44737). Insumo `44729` BATE-RODAS DE RESINA… **SEM PREÇO**. Não há insumo SINAPI “bate-roda de concreto”. |
| **2 — SINAPI adaptável / de-para funcional** | **Adotada.** MO e argamassa da `94275`; peça = insumo `41679` da mesma composição, coeficiente por **volumetria** × perda 1,005. |
| **2b** | Não se sugere ao projetista trocar o serviço por meio-fio linear. O 41679 entra só como **proxy de concreto pré-moldado**, não como substituição funcional. |
| **3 — ORSE** | Não utilizada (partição local vazia; script ORSE sem `bs4`). |
| **4 — CPU catálogo** | `PRH.019` (50 × 15 × 8 cm) só como modelo estrutural. Coef. histórico 0,3 H **não** copiado. |
| **5/6 — CPU nova** | Esta ficha. |
| **7 — Cotação** | **Não aplicável nesta revisão** — a peça tem preço SINAPI BA positivo. |
| **8 — E-mail** | Não enviado. |

---

## 3. Escolha do insumo da peça (sem COT)

Consulta CLI (2026-09-17), fonte SINAPI, regime não desonerado:

```
[FONTE LIBERADA] SINAPI 41679 — MEIO-FIO OU GUIA DE CONCRETO PRE-MOLDADO, COMP 1 M, *20 X 12/15* CM (H X L1/L2)
UF BA | competência 2026-07 | Unidade: UN | Tipo: MATERIAL | R$ 25,25
```

Mesmo preço no regime desonerado: **R$ 25,25** (insumo, sem encargos de MO).

**Adotado: `41679`.** Motivos, todos verificáveis:

1. É o insumo da peça na composição paradigma `94275` (CLI: `INSUMO 41679 | UN | coef. 1.005 | R$ 25,25`).
2. Material: concreto pré-moldado, unidade `UN`, preço BA positivo.
3. A descrição oficial traz **H = 20 cm** e **L2 = 15 cm**, as duas seções transversais do bate-roda 70 × 20 × 15 cm.
4. Único insumo SINAPI cujo nome contém “BATE-RODAS” é `44729` (resina, SEM PREÇO) — material errado e linha bloqueada.

### Alternativas SINAPI de peça pré-moldada de concreto (não adotadas)

Volumes calculados só das dimensões *ipsis verbis* da descrição. Alvo = 0,021 m³.

| Código | Descrição oficial (CLI) | Und | Preço BA | Volume da peça | \|Δ\| vs 0,021 | Por que não |
|---|---|---|---:|---:|---:|---|
| **41679** | COMP 1 M, *20 X 12/15* CM (H X L1/L2) | UN | R$ 25,25 | **0,027 m³** | 0,006 | **Adotado** |
| 41683 | COMP 80 CM, *30 X 10/10* (H X L1/L2) | UN | R$ 20,51 | 0,024 m³ | 0,003 | Volume mais próximo, mas seção 30×10 cm não casa com 20×15; **não** é o insumo da 94275 |
| 41681 | COMP 80 CM, *25 X 08/08* CM (H X L1/L2) | UN | R$ 17,28 | 0,016 m³ | 0,005 | Seção 25×8 cm |
| 4062 | COMP 1 M, *30 X 15* CM (H X L) | UN | R$ 27,88 | 0,045 m³ | 0,024 | H = 30 cm |
| 41680 | COMP *39* CM, *19 X 6,5/6,5* CM | UN | R$ 11,04 | 0,0048165 m³ | 0,016 | Guia de jardim |
| 44729 | BATE-RODAS DE RESINA COM DOIS PINOS DE FIXACAO | UN | SEM PREÇO | — | — | Resina; **BLOQUEADO** |

SQL somente leitura (insumos de meio-fio / bate-roda / guia de concreto):

```sql
SELECT codigo, unidade, tipo, preco_nao_deson, descricao
FROM insumos
WHERE fonte = 'SINAPI'
  AND (
    UPPER(descricao) LIKE '%MEIO-FIO%'
    OR UPPER(descricao) LIKE '%BATE-RODA%'
    OR UPPER(descricao) LIKE '%BATE RODA%'
    OR (UPPER(descricao) LIKE '%GUIA%' AND UPPER(descricao) LIKE '%CONCRETO%' AND UPPER(descricao) LIKE '%PRE%')
  )
ORDER BY codigo;
```

---

## 4. Conta de volumetria (aberta)

### 4.1 Volume alvo (1 UN de bate-roda)

\[
V_{\text{alvo}} = 0{,}70 \times 0{,}20 \times 0{,}15 = 0{,}021\ \mathrm{m}^{3}
\]

Prisma retangular. Nenhuma perda geométrica extra.

### 4.2 Volume da peça SINAPI 41679

Ficha do insumo: `COMP 1 M, *20 X 12/15* CM (H X L1/L2)`.

| Símbolo | Origem na descrição | Valor |
|---|---|---|
| Comprimento | COMP 1 M | 1,00 m |
| H | 20 cm | 0,20 m |
| L1 | 12 cm | 0,12 m |
| L2 | 15 cm | 0,15 m |

Seção trapezoidal (L1/L2):

\[
V_{41679} = 1{,}00 \times 0{,}20 \times \frac{0{,}12 + 0{,}15}{2} = 1{,}00 \times 0{,}20 \times 0{,}135 = 0{,}027\ \mathrm{m}^{3}
\]

**Nota de ficha (não misturar):** a composição `94275` descreve a guia como `100X15X13X20 CM` (C × base inf. × base sup. × altura) → volume 1,00 × 0,20 × (0,15+0,13)/2 = **0,028 m³**. O coeficiente da peça usa as dimensões do **insumo 41679** (0,027 m³), como pedido. A MO/argamassa continuam copiadas da 94275.

### 4.3 Fator de perda

Na 94275 o insumo 41679 entra com **coef. 1,005** (perda 0,5%). O mesmo fator multiplica a razão volumétrica.

### 4.4 Coeficiente do insumo 41679 nesta CPU

\[
k = \frac{V_{\text{alvo}}}{V_{41679}} \times 1{,}005 = \frac{0{,}021}{0{,}027} \times 1{,}005
\]

\[
\frac{0{,}021}{0{,}027} = 0{,}777\overline{7} = \frac{7}{9}
\]

\[
k = 0{,}777\overline{7} \times 1{,}005 = 0{,}7816\overline{6} = \frac{469}{600}
\]

**Coeficiente adotado na planilha:** `0,781667` (6 casas, `ROUND_HALF_UP` de 0,781666…).  
Conferência: \(0{,}781667 \times 25{,}25 = 19{,}737092\ldots \rightarrow\) **R$ 19,74** — igual a \(0{,}7816\overline{6} \times 25{,}25 = 19{,}73708\ldots\) arredondado a 2 casas.

### 4.5 Preço da linha da peça

| Item | Valor | Fonte |
|---|---|---|
| Preço unitário 41679 | R$ 25,25 / UN | CLI SINAPI BA 2026-07, ambos os regimes |
| Coeficiente | 0,781667 UN/UN | seção 4.4 |
| Total da linha | **R$ 19,74** | `ROUND(0,781667 × 25,25; 2)` |

---

## 5. Premissa e risco do proxy (não bloqueia preço)

- **Premissa:** o concreto pré-moldado da guia `41679` remunera, por m³, o concreto da peça de bate-roda, após igualar volumes e aplicar a perda oficial 1,005.
- **Risco:** meio-fio é contenção linear de pavimento; bate-roda é batente isolado de estacionamento. Seção trapezoidal 12/15 cm ≠ retângulo 20 × 15 cm. Acabamento, armação e fôrma de fábrica podem diferir.
- **O que o proxy não faz:** não transforma o serviço orçado em “assentamento de meio-fio 94275”; a 94275 não é lançada. Areia 370 (leito de vala) permanece fora.
- Determinação desta revisão: registrar o risco e **precificar**.

---

## 6. Quadro analítico — hipótese A (recomendada)

**Unidade:** 1 UN · **Regime:** não desonerado · **Fonte:** SINAPI BA 2026-07  
Totais de linha: `ROUND(coeficiente × preço_unitário; 2)` com preços do CLI.

| Tipo | Banco | Código | Descrição (*ipsis verbis* da consulta) | Und | Coef. | Origem do coef. | Preço unit. BA | Regime | Competência | Total linha | Status |
|---|---|---|---|---|---:|---|---:|---|---|---:|---|
| MO | SINAPI | `88309` | PEDREIRO COM ENCARGOS COMPLEMENTARES | H | 0,2151 | 94275 | R$ 35,77 | nao_desonerado | 2026-07 | R$ 7,69 | PRECIFÍCÁVEL |
| MO | SINAPI | `88316` | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0,2151 | 94275 | R$ 26,14 | nao_desonerado | 2026-07 | R$ 5,62 | PRECIFÍCÁVEL |
| Comp. aux. | SINAPI | `88629` | ARGAMASSA TRAÇO 1:3 (EM VOLUME DE CIMENTO E AREIA MÉDIA ÚMIDA), PREPARO MANUAL. AF_07/2026 | M3 | 0,0012 | 94275 (área de contato 0,14 m²) | R$ 938,86 | nao_desonerado | 2026-07 | R$ 1,13 | PRECIFÍCÁVEL |
| Insumo | SINAPI | `41679` | MEIO-FIO OU GUIA DE CONCRETO PRE-MOLDADO, COMP 1 M, *20 X 12/15* CM (H X L1/L2) | UN | 0,781667 | (0,021/0,027)×1,005 | R$ 25,25 | nao_desonerado | 2026-07 | R$ 19,74 | PRECIFÍCÁVEL |

**Custo direto total hipótese A:** R$ 7,69 + R$ 5,62 + R$ 1,13 + R$ 19,74 = **R$ 34,18 / UN** (sem BDI).

A `88629` já embute servente de preparo (12,3150605 H/m³). Não se soma outra hora de preparo.

MO da 94275 permanece **por UN** (0,2151 H), não escalada pela volumetria: a área de junta do bate-roda (0,70 × 0,20 = 0,14 m²) coincide com a da guia 94275 medida pelas bases 15/13 cm da composição (1,00 × 0,14 = 0,14 m²). A peça é mais leve (~0,021 vs 0,027 m³); não se inventou redução de hora.

### Fora da CPU A

| Código | Motivo |
|---|---|
| `370` AREIA MEDIA | Leito de vala da 94275; premissa = piso existente. |
| `103734` / `44729` / `44737` / `102274` / `102275` | Família resina + asfalto. |
| `102498` | Caiação de meio-fio, por metro. |
| `94964` | Hipótese B (preparo in loco). |
| Qualquer `COT-*` | Proibido nesta revisão. |

---

## 7. Evidência SINAPI de mão de obra

Nenhuma hora inventada.

Consulta `94275 --fonte SINAPI --regime nao_desonerado`:

```
COMPOSICAO 88316 | H | coef. 0.2151 | R$ 26,14 | SERVENTE COM ENCARGOS COMPLEMENTARES
COMPOSICAO 88309 | H | coef. 0.2151 | R$ 35,77 | PEDREIRO COM ENCARGOS COMPLEMENTARES
INSUMO 41679 | UN | coef. 1.005 | R$ 25,25 | MEIO-FIO OU GUIA DE CONCRETO PRE-MOLDADO, COMP 1 M, *20 X 12/15* CM (H X L1/L2)
COMPOSICAO 88629 | M3 | coef. 0.0012 | R$ 938,86 | ARGAMASSA TRAÇO 1:3 …
```

Consultas diretas:

```
[FONTE LIBERADA] SINAPI 88309 — PEDREIRO COM ENCARGOS COMPLEMENTARES
UF BA | competência 2026-07 | Unidade: H | R$ 35,77

[FONTE LIBERADA] SINAPI 88316 — SERVENTE COM ENCARGOS COMPLEMENTARES
UF BA | competência 2026-07 | Unidade: H | R$ 26,14

[FONTE LIBERADA] SINAPI 88629 — ARGAMASSA TRAÇO 1:3 (EM VOLUME DE CIMENTO E AREIA MÉDIA ÚMIDA), PREPARO MANUAL. AF_07/2026
UF BA | competência 2026-07 | Unidade: M3 | R$ 938,86
```

Reserva 103734 (não adotada na A): servente 0,2599 H; pedreiro 0,0113 H; peça e adesivo SEM PREÇO.

`PRH.019` (catálogo): servente 0,3 H — **não copiado**.

---

## 8. Premissas da hipótese A

1. Peça alvo: concreto pré-moldado 70 × 20 × 15 cm, 1 UN.
2. Material da peça orçado por proxy volumétrico `41679` (não se instala 0,78 m de meio-fio).
3. Assentamento sobre piso existente, argamassa 1:3 (`88629`).
4. Sem vala, areia 370, pintura, chumbador, furação de asfalto, armação, forma de obra.
5. Quantidade na planilha = líquida em UN. Perda 0,5% só no coeficiente da peça.
6. Se o projeto for asfalto + pinos: abandonar esta CPU e reabrir a 103734 (ainda bloqueada nos insumos).

---

## 9. Anexo — regime desonerado

Mesmos coeficientes; preços CLI `--regime desonerado`. Insumo 41679: R$ 25,25 (igual).

| Código | Coef. | Preço unit. desonerado | Total linha |
|---|---:|---:|---:|
| 88309 | 0,2151 | R$ 33,84 | R$ 7,28 |
| 88316 | 0,2151 | R$ 24,91 | R$ 5,36 |
| 88629 | 0,0012 | R$ 923,71 | R$ 1,11 |
| 41679 | 0,781667 | R$ 25,25 | R$ 19,74 |
| **Custo direto total** | | | **R$ 33,49 / UN** |

A ficha principal permanece **não desonerada** (R$ 34,18 / UN).

---

## 10. Hipótese B — moldado in loco (não precificar o serviço completo)

Volume 0,021 m³. `94964` CONCRETO FCK = 20MPA … BETONEIRA 400 L: R$ 639,03/m³ × 0,021 = **R$ 13,42** — só preparo. Forma (`92270`) e lançamento sem paradigma compatível → **BLOQUEADO**. Não se inventam horas.

---

## 11. Proveniência e hashes

De `FONTES_DADOS.json` (não alterado). Conferidos localmente:

| Artefato | SHA-256 |
|---|---|
| `base_precos.db` | `a59957251f947dc83f7439d379fbbd1bc1b6d08337fe0cf776d174aff747be34` |
| ZIP SINAPI 2026-07 | `58c131f997560332cf2d7f7f90644790d5c6e2a909a2963b18f136779312b14f` |
| `CATALOGO_CPU_PROPRIAS.json` | `6040320ea4a55e2f511f497785613fca585a6e97eb2a365dd5d574f70db73f35` |

Capacidades SINAPI: consulta, paradigma_cpu e preco_direto = `LIBERADA`.

---

## 12. Comandos de consulta (reprodução desta revisão)

```bash
python3 scripts/validate_repository.py

python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 41679 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 41679 --fonte SINAPI --regime desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94275 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88309 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88316 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88629 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 41683 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 41681 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 4062 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 44729 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88309 --fonte SINAPI --regime desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88316 --fonte SINAPI --regime desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88629 --fonte SINAPI --regime desonerado
```

---

## 13. Gate desta ficha

| Controle | Resultado |
|---|---|
| `validate_repository.py` | `LIBERADO` |
| Linhas de preço | só SINAPI BA 2026-07 com preço > 0 |
| MO | 88309 e 88316, coef. 94275 |
| Peça | 41679, R$ 25,25, coef. volumétrico 0,781667 |
| COT / e-mail / `FONTES_DADOS` | não utilizados / não alterado |
| Custo direto A (não desonerado) | **R$ 34,18 / UN** |
| Natureza | proxy volumétrico Etapa 2; risco funcional registrado |

Espelho JSON: `artifacts/CPU_BATE_RODA_70x20x15.json`.
