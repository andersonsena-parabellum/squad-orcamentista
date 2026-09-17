# CPU PRP-BTR-001 — Bate-roda de concreto 70 × 20 × 15 cm

**Status da ficha:** `PRECIFÍCÁVEL` — Etapa 2 (peça retangular pré-moldada SINAPI `97734` por m³ × volume do prisma).  
**Custo direto total (hipótese A, não desonerado, sem BDI):** **R$ 90,19 / UN**  
**Isto não é código SINAPI específico de bate-roda 70 × 20 × 15 cm.** A peça é a composição `97734` (peça retangular pré-moldada, 10 a 30 litros), medida em m³.  
**Não entra em catálogo oficial.** Artefato avulso. Não altera `FONTES_DADOS.json`. Sem COT. Sem 41679. Sem e-mail.

---

## 0. Preflight do repositório

```bash
python3 scripts/validate_repository.py
```

Resultado (2026-09-17T09:43:05.166989+00:00): `gate` **`LIBERADO`**, 5 restrições P1. SINAPI BA 2026-07 `LIBERADA`.

---

## 1. Identificação

| Campo | Valor |
|---|---|
| Código sugerido | `PRP-BTR-001` |
| Descrição oficial proposta | `BATE-RODA DE CONCRETO PRÉ-MOLDADO 70 × 20 × 15 CM — FORNECIMENTO (PEÇA RETANGULAR PRÉ-MOLDADA) E ASSENTAMENTO COM ARGAMASSA, SOBRE PISO EXISTENTE` |
| Unidade da CPU | `UN` |
| Dimensão | 70 × 20 × 15 cm |
| Volume | **0,021 m³** = 0,70 × 0,20 × 0,15 = **21 litros** |
| Peça SINAPI | `97734` — PEÇA RETANGULAR PRÉ-MOLDADA, VOLUME DE CONCRETO DE 10 A 30 LITROS, TAXA DE AÇO APROXIMADA DE 30KG/M³. AF_03/2024 |
| Unidade do 97734 | **M3** |
| Faixa da 97734 vs peça | 21 L está **dentro** de 10 a 30 L |
| Regime da ficha | **não desonerado** (desonerado no anexo) |
| UF / competência | BA / 2026-07 |

---

## 2. Cascata

| Etapa | Resultado |
|---|---|
| **1 — SINAPI exato** | Não há bate-roda de concreto. `103734` é resina sobre asfalto, SEM PREÇO. |
| **2 — SINAPI adaptável** | **Adotada.** Peça = `97734` (m³ × 0,021). Assentamento = MO `88309`/`88316` e argamassa `88629` da `94275`. |
| **41679 / meio-fio** | **Retirado** desta revisão. |
| **7 — Cotação** | Não aplicável: 97734 tem preço BA positivo. |
| **8 — E-mail** | Não enviado. |

---

## 3. Consulta 97734 (evidência CLI)

```bash
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 97734 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 97734 --fonte SINAPI --regime desonerado
```

**Não desonerado:**

```
[FONTE LIBERADA] SINAPI 97734 — PEÇA RETANGULAR PRÉ-MOLDADA, VOLUME DE CONCRETO DE 10 A 30 LITROS, TAXA DE AÇO APROXIMADA DE 30KG/M³. AF_03/2024
UF BA | competência 2026-07 | Unidade: M3 | Grupo: Estruturas Pré-Fabricadas e Pré-Moldadas | R$ 3.607,31
  COMPOSICAO 94971 | M3 | coef. 1.2 | R$ 651,10 | CONCRETO FCK = 25MPA, TRAÇO 1:2,3:2,7 … BETONEIRA 600 L. AF_05/2021
  COMPOSICAO 92767 | KG | coef. 27.8988 | R$ 16,43 | ARMAÇÃO DE LAJE … AÇO CA-60 DE 4,2 MM - MONTAGEM. AF_06/2022
  COMPOSICAO 91693 | CHI | coef. 0.7043 | … SERRA CIRCULAR …
  COMPOSICAO 91692 | CHP | coef. 0.4877 | … SERRA CIRCULAR …
  COMPOSICAO 90587 | CHI | coef. 18.0917 | … VIBRADOR DE IMERSÃO …
  COMPOSICAO 90586 | CHP | coef. 6.635 | … VIBRADOR DE IMERSÃO …
  COMPOSICAO 88316 | H | coef. 31.3499 | R$ 26,14 | SERVENTE COM ENCARGOS COMPLEMENTARES
  COMPOSICAO 88309 | H | coef. 31.3499 | R$ 35,77 | PEDREIRO COM ENCARGOS COMPLEMENTARES
  COMPOSICAO 88261 | H | coef. 5.96 | R$ 34,00 | CARPINTEIRO DE ESQUADRIAS COM ENCARGOS COMPLEMENTARES
  COMPOSICAO 88239 | H | coef. 1.192 | R$ 26,60 | AJUDANTE DE CARPINTEIRO COM ENCARGOS COMPLEMENTARES
  INSUMO 20247 | KG | coef. 0.4365 | … PREGO …
  INSUMO 4517 | M | coef. 5.6283 | … SARRAFO …
  INSUMO 2692 | L | coef. 0.0833 | … DESMOLDANTE …
  INSUMO 1358 | M2 | coef. 1.9404 | … MADEIRITE … E = 17 MM
```

**Desonerado (cabeçalho):** R$ **3.474,15** / M3. Mesmos coeficientes. MO interna: servente R$ 24,91; pedreiro R$ 33,84; carpinteiro R$ 32,17; ajudante R$ 25,31. Concreto 94971: R$ 645,41. Armação 92767: R$ 16,01.

Família AF_03/2024 (SQL, não lançada): `97733` até 10 L; **`97734` 10–30 L**; `97735` 30–100 L; `97736` acima de 100 L. O prisma de 21 L cabe só na 97734.

---

## 4. Perda: 0,021 sem × 1,005

Conta do volume:

\[
V = 0{,}70 \times 0{,}20 \times 0{,}15 = 0{,}021\ \mathrm{m}^{3}/\mathrm{UN} = 21\ \mathrm{L}
\]

**Coeficiente adotado do 97734: `0,021` M3/UN.**

Não se multiplica 1,005. Motivo (analítico da própria 97734, não inventado):

1. A 97734 já é **fornecimento/fabricação da peça pré-moldada** (concreto + aço + forma + MO de moldagem), unidade **M3 da peça acabada**.
2. Perda de fabricação já está **dentro** do preço: concreto `94971` entra com **coef. 1,2** (20% a mais de concreto por m³ de peça). Em 0,021 m³ de peça isso remunera 0,0252 m³ de concreto preparado.
3. O 1,005 da `94275` é perda de **insumo de meio-fio acabado em UN** (41679) no assentamento de guia. A 41679 foi retirada. Transferir 0,5% para o m³ da 97734 seria misturar duas perdas de famílias diferentes (AF_01/2024 guia vs AF_03/2024 peça pré-moldada) sem evidência no analítico da 97734.

Se alguém aplicasse 0,021 × 1,005 = 0,021105, seria extra sem suporte na 97734. **Não adotado.**

Caderno AF_03/2024 desta família **não** está em `02-CADERNOS_TECNICOS/`. A decisão usa só o analítico CLI.

---

## 5. MO da 94275 não duplica a 97734

A 97734 **inclui** pedreiro e servente (31,3499 H/m³ cada) + carpinteiros, serra, vibrador e forma. Isso é **moldagem da peça**, não assentamento no piso.

A 97734 **não** contém argamassa de assentamento, areia de vala, nem serviço de “assentamento de guia”.

Por isso a hipótese A **mantém**, sem duplicar fabricação:

- `88309` / `88316` coef. **0,2151 H/UN** da `94275` = colocação da peça acabada;
- `88629` coef. **0,0012 m³/UN** = junta de argamassa 1:3.

As horas 31,3499 H/m³ **não** são relançadas: já estão no preço unitário R$ 3.607,31/m³.

Premissa de junta (94275): área 0,70 × 0,20 = 0,14 m², igual à da guia paradigma.

---

## 6. Quadro analítico — hipótese A

**Unidade:** 1 UN · **Regime:** não desonerado · **Fonte:** SINAPI BA 2026-07  
Totais: `ROUND(coeficiente × preço_unitário; 2)` com preços do CLI.

| Tipo | Banco | Código | Descrição (*ipsis verbis*) | Und | Coef. | Origem do coef. | Preço unit. BA | Regime | Competência | Total | Status |
|---|---|---|---|---|---:|---|---:|---|---|---:|---|
| Comp. aux. | SINAPI | `97734` | PEÇA RETANGULAR PRÉ-MOLDADA, VOLUME DE CONCRETO DE 10 A 30 LITROS, TAXA DE AÇO APROXIMADA DE 30KG/M³. AF_03/2024 | M3 | 0,021 | 0,70×0,20×0,15 | R$ 3.607,31 | nao_desonerado | 2026-07 | R$ 75,75 | PRECIFÍCÁVEL |
| MO | SINAPI | `88309` | PEDREIRO COM ENCARGOS COMPLEMENTARES | H | 0,2151 | 94275 (assentamento) | R$ 35,77 | nao_desonerado | 2026-07 | R$ 7,69 | PRECIFÍCÁVEL |
| MO | SINAPI | `88316` | SERVENTE COM ENCARGOS COMPLEMENTARES | H | 0,2151 | 94275 (assentamento) | R$ 26,14 | nao_desonerado | 2026-07 | R$ 5,62 | PRECIFÍCÁVEL |
| Comp. aux. | SINAPI | `88629` | ARGAMASSA TRAÇO 1:3 (EM VOLUME DE CIMENTO E AREIA MÉDIA ÚMIDA), PREPARO MANUAL. AF_07/2026 | M3 | 0,0012 | 94275 | R$ 938,86 | nao_desonerado | 2026-07 | R$ 1,13 | PRECIFÍCÁVEL |

**Custo direto total:** R$ 75,75 + R$ 7,69 + R$ 5,62 + R$ 1,13 = **R$ 90,19 / UN** (sem BDI).

Memória 97734: \(0{,}021 \times 3607{,}31 = 75{,}75351 \rightarrow\) R$ 75,75.

### Fora da CPU A

| Código | Motivo |
|---|---|
| `41679` e demais meio-fios | Retirados. |
| `370` AREIA MEDIA | Leito de vala da 94275; premissa = piso existente. |
| `103734` / `44729` / `44737` | Resina + asfalto. |
| COT | Não usado. |

---

## 7. Premissas e riscos (não bloqueiam preço)

1. Prisma 70 × 20 × 15 cm, 21 L, faixa 10–30 L da 97734.
2. A 97734 traz **aço CA-60 ~30 kg/m³**, forma de madeira e concreto FCK 25. Bate-roda comercial pode ser não armado; a ficha **não desconta** aço (seria inventar).
3. 97734 remunera **fabricação** da peça; assentamento é a parcela 94275.
4. Sem pintura, chumbador, furação de asfalto, vala.
5. Quantidade na planilha = líquida em UN. Perda de concreto da peça = coef. 1,2 interno da 97734.

---

## 8. Evidência da MO de assentamento (94275)

```
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94275 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88309 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88316 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88629 --fonte SINAPI --regime nao_desonerado
```

```
SINAPI 88309 — PEDREIRO COM ENCARGOS COMPLEMENTARES | H | R$ 35,77 | BA 2026-07
SINAPI 88316 — SERVENTE COM ENCARGOS COMPLEMENTARES | H | R$ 26,14 | BA 2026-07
SINAPI 88629 — ARGAMASSA TRAÇO 1:3 … | M3 | R$ 938,86 | BA 2026-07
94275: 88309 coef. 0.2151 | 88316 coef. 0.2151 | 88629 coef. 0.0012
```

---

## 9. Anexo — regime desonerado

| Código | Coef. | Preço unit. desonerado | Total linha |
|---|---:|---:|---:|
| 97734 | 0,021 | R$ 3.474,15 | R$ 72,96 |
| 88309 | 0,2151 | R$ 33,84 | R$ 7,28 |
| 88316 | 0,2151 | R$ 24,91 | R$ 5,36 |
| 88629 | 0,0012 | R$ 923,71 | R$ 1,11 |
| **Custo direto total** | | | **R$ 86,71 / UN** |

97734 desonerado: \(0{,}021 \times 3474{,}15 = 72{,}95715 \rightarrow\) R$ 72,96.

Ficha principal: **não desonerada, R$ 90,19 / UN**.

---

## 10. Hipótese B (moldado in loco) — não fecha o serviço

`94964` (só preparo FCK 20) × 0,021 = R$ 13,42. Forma e lançamento sem paradigma → **BLOQUEADO**. A 97734 já cobre fabricação da peça na hipótese A.

---

## 11. Proveniência

`FONTES_DADOS.json` não alterado.

| Artefato | SHA-256 |
|---|---|
| `base_precos.db` | `a59957251f947dc83f7439d379fbbd1bc1b6d08337fe0cf776d174aff747be34` |
| ZIP SINAPI 2026-07 | `58c131f997560332cf2d7f7f90644790d5c6e2a909a2963b18f136779312b14f` |

Os valores R$ 3.102,95 / R$ 3.274,33 em `01-DISCIPLINAS_MARKDOWN/03_ESTRUTURAS.md` **não** foram usados; prevalece o CLI (R$ 3.607,31 / R$ 3.474,15).

---

## 12. Comandos desta revisão

```bash
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 97734 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 97734 --fonte SINAPI --regime desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 94275 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88309 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88316 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88629 --fonte SINAPI --regime nao_desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88309 --fonte SINAPI --regime desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88316 --fonte SINAPI --regime desonerado
python3 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 88629 --fonte SINAPI --regime desonerado
```

---

## 13. Gate

| Controle | Resultado |
|---|---|
| Peça | **97734**, M3, R$ 3.607,31, coef. **0,021** |
| 41679 / COT | ausentes |
| MO assentamento | 88309 e 88316, 0,2151 H, 94275 |
| Perda 1,005 | não aplicada (perda interna 1,2 no concreto da 97734) |
| Total direto ND | **R$ 90,19 / UN** |
| `FONTES_DADOS` / e-mail | intacto / não enviado |
