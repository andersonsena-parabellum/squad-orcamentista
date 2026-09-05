# AGENTS.md — Cliente 16. FABIO / FPE Projetos

Regras locais para qualquer IA que trabalhe nesta pasta.  
**Escopo:** `CLIENTES/16. FABIO - FPE/`  
**Atualizado:** 2026-09-04 (arquitetura fail-closed, proveniência de fontes, segregação de funções, gate pré e pós-exportação e scripts versionados)

As regras globais do Anderson (`~/.grok/AGENTS.md` ou equivalente) continuam valendo. Em conflito de detalhe operacional deste cliente, **este arquivo tem precedência**.

---

## 1. O que é esta pasta

Pasta de **cliente/parceiro de orçamentos e projetos** no ecossistema DFE:

| Item | Valor |
|------|--------|
| Identificação da pasta | `16. FABIO - FPE` |
| Cliente / marca nos arquivos | **Fábio Pereira** / **FPE Projetos** (`FPE ENGENHARIA E PROJETOS LTDA`) |
| Papel da DFE / Anderson | Apoio técnico em **orçamento de obras**, levantamentos, cotações, revisões, defesas/respostas técnicas e auditorias preventivas |
| Domínio | Obras e projetos públicos/privados na **BA** (secretarias, prefeituras, órgãos estaduais: SUPAT/SAEB, PGE, SEC, SETRE, ADAB, FUNDAC, SECOM, UEFS, etc.) e empreendimentos privados |
| Volume | Pasta grande (~5k+ arquivos): PDF, XLSX, DWG, RVT, DOCX, RAR/ZIP de envio, IFC |

**Não é repositório genérico de software.** É arquivo de engenharia/orçamentação civil, infraestrutura e instalações. Respeite as estruturas de dados de planilhas e a rastreabilidade métrica.

---

## 2. Como a pasta está organizada

### Raiz

- **Uma subpasta por obra/contrato** (numeradas historicamente e recentes):
  - *Históricas:* `1- CMEI`, `21 - PMFRP MERCADO MUNICIPAL`, `22 - SEPROMI`, `25 - CFA`, `30- P23183 – ADAB…`, `33- P24112 - PGE`, `36 - P24036 - RACK na SECOM`, `38 - P24178- PGE - SONORIZAÇÃO`, …
  - *Recentes / Ativas:*
    - `43- UBS` — Unidade Básica de Saúde (revisão de fundações, implantação CT-098, mapa SDE).
    - `44 - PRAÇA DO HOSPITAL` — Urbanização e praça (IFC, paisagismo, cadernos técnicos SINAPI).
    - `45 - CAB FORMOSA` e `46 - CAB FORMOSA II- CODEX` — Empreendimentos com squad integrado (`_squad/`), extração IFC/BIM, EAP parametrizada e relatórios técnicos.
    - `BIKATO` — Obras comerciais privadas com DRE projetado, controle de margens e propostas vigentes.
- **Hub Central de Governança e Inteligência:**
  - `squad-orcamentista/` — Repositório central de inteligência orçamentária FPE:
    - `01-PROMPTS/` — Instruções mestras padronizadas (Grok, Codex/OpenAI, Antigravity).
    - `02-TEMPLATES/` — Matriz Canônica de 10 Colunas (`TEMPLATE_CANONICO_10_COLUNAS.md`).
    - `03-BASE_DE_PRECOS/` — Banco SQLite oficial `base_precos.db` (12,8 MB), cadernos técnicos SINAPI em Markdown, catálogo de CPUs próprias (`03-CPU_PROPRIAS/`) e scripts de consulta CLI token-eficientes.
    - `04-BASE_CONHECIMENTO_SUPAT/` — Checklist Oficial ITEM 01 a 10, 463 precedentes minerados (`04-DADOS/precedentes.json`), 15 cadernos temáticos (`02-PRECEDENTES/`), `MAPA_RESSALVAS.md` e script de consulta CLI.
- **Outras pastas e arquivos transversais na raiz:**
  - `00-PAGAMENTOS/` — Controle financeiro e pagamentos do relacionamento FPE.
  - `FPE-PARÂMETROS COMPARTILHADOS.txt` — Arquivo de parâmetros compartilhados do Revit (não editar à mão).
  - Propostas contratuais `PR20…` (docx/pdf) e planilhas de acompanhamento.

### Dentro de cada obra (padrão recorrente)

| Subpasta / padrão | Uso |
|-------------------|-----|
| `ORÇAMENTO/` ou `00- Orçamento/` | Planilhas oficiais da revisão vigente e anteriores (`DC-001` a `DC-007` e `EC-001`/`EC-002`) |
| `COTAÇÃO/` / `COTAÇÕES/` / `COTAÇÕES E MC/` | Fichas técnicas, cotações de mercado e Mapas de Cotação (`DC-007`) |
| `ENVIO/` / `ENVIOS/` | Pacotes selados já entregues (frequentemente espelhados em `.rar`/`.zip` datados) |
| `R00` … `R06` (ou pastas de revisão) | Revisões de trabalho do pacote orçamentário — use a **maior R** como candidata à vigente, confirmando data do ENVIO |
| `PROJETO/` / `PROJETOS/` / disciplinas | Pranchas (DWG/PDF), modelos IFC/BIM, memoriais e **Listas de Insumos/Materiais (LI)** por disciplina |
| `_squad/` | Pasta de trabalho colaborativo do Squad FPE (EAP, `dwg_inventario.json`, `estado.json`, IFCs extraídos, `RELATORIO-SQUAD.docx` e pareceres `ANA-*.md`, `CARLOS-*.md`, `LEVI-*.md`, `OTAVIO-*.md`) |
| `RESPOSTAS-*.docx` / `RT-001` | Respostas formais da orçamentista à análise crítica do órgão fiscalizador |

**Regra de ouro:** pacote `.rar`/`.zip` de ENVIO e pasta `Rxx` coexistem. Para “o que foi mandado”, prefira o **ENVIO datado mais recente**; para editar, trabalhe na pasta de revisão descompactada e **suba revisão (`R+1`)** (nunca sobrescreva o envio antigo).

---

## 3. Convenção de nomes de arquivo

Padrão observado:

```text
P{código}-{ÓRGÃO}-{DISCIPLINA|ETAPA}-{TIPO}-R{rev}[ - DESCRIÇÃO].{ext}
```

Exemplos reais:
- `P23087-SEPROMI-ORÇ-EC-001-R00- ORÇAMENTO.xlsx`
- `P23087-SEPROMI-ORÇ-EC-002-R00- CRUVA ABC.xlsx` (typo histórico “CRUVA” = Curva ABC — **não renomear arquivos antigos**)
- `P23201-SETRE-ORC-DC-001-R06.xlsx`
- `P23183-ADAB-ORC-DC-004-R06.xlsx`
- `P20055-SEC-IMP_ELE-LI-R05.pdf`
- `RESPOSTAS - P23201-SETRE-ORÇ_-RT-001-R05.docx`

### Códigos de tipo (leitura rápida)

| Trecho no nome | Significado típico |
|----------------|--------------------|
| `ORC` / `ORÇ` | Pacote / documento de orçamento |
| `LI` | Lista de Insumos / Lista de Materiais (fonte de quantitativo do **projeto**) |
| `EC-00n` / `DC-00n` | Numeração interna do documento no pacote |
| `CURVA ABC` / `CRUVA ABC` | Curva ABC de serviços |
| `COMPOSI` / `COMPOSIÇÃO` | Composições analíticas |
| `CRONOGRAMA` | Cronograma físico-financeiro |
| `BDI` | Demonstrativo de BDI |
| `ENCARGOS` | Encargos sociais |
| `MC` | Mapa de cotação |
| `RESPOSTAS` / `RT-001` | Resposta a análise crítica / ressalvas |
| `ENVIO` + data | Pacote oficial entregue ao cliente/órgão |

### Disciplinas comuns em LI

Elétrica (`ELE`), hidráulica/hidrossanitário (`HDR`, `HAP`, `HAG`, `HEG`), SPDA, combate a incêndio (`PCIP`), estrutura (`EST`), climatização (`CLIM`), sonorização/AV, CFTV, cabeamento estruturado, paisagismo, impermeabilização, etc.  
Se a pasta da disciplina existe no projeto mas **não há LI legível**, marque a disciplina formalmente como **não auditada** no `RELATORIO-SQUAD.docx` — nunca como “OK por omissão”.

---

## 4. Repositório Central de Preços e Consulta Token-Eficiente

Base oficial consolidada: `squad-orcamentista/03-BASE_DE_PRECOS/`
- **Consulta via CLI / Token-Eficiente:**
  ```bash
  python "squad-orcamentista/03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py" <CODIGO> --fonte SINAPI --regime <desonerado|nao_desonerado>
  python "squad-orcamentista/03-BASE_DE_PRECOS/04-SCRIPTS/consultar_orse_oficial.py" <CODIGO_OU_DESCRICAO>
  python "squad-orcamentista/03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py" <CODIGO_OU_DESCRICAO>
  ```
  *(Exige fonte e regime explícitos e exibe o detalhamento de coeficientes e insumos sem estourar a janela de contexto).*

- **Cascata Obrigatória do Orçamentista (0 a 8):**
  1. *Etapa 0 (Fontes):* LI, Memorial Descritivo e Projeto 2D/3D (quantidade líquida na unidade da CPU).
  2. *Etapa 1 (SINAPI Exato):* Consulta exata no banco SINAPI (BA) desonerado/não desonerado.
  3. *Etapa 2 (SINAPI Adaptável):* Copia mão de obra e coeficientes do caderno técnico; troca apenas o insumo material específico.
  4. *Etapa 2b (Sugestão ao Projetista):* Adequação leve de especificação comercial para item tabelado.
  5. *Etapa 3 (ORSE Paradigma):* Consulte o portal oficial, grave a evidência local e use `REF. ORSE xxxxx`. Conversões para SINAPI e uso de preço fora de SE exigem justificativa; nada é substituído automaticamente.
  6. *Etapa 4 (CPU do Catálogo):* Reutilização como modelo das composições próprias catalogadas (`03-CPU_PROPRIAS/CATALOGO_CPU_PROPRIAS.json`), com revalidação integral para a obra atual.
  7. *Etapa 5 (Adaptar CPU):* Adaptação de composição do catálogo.
  8. *Etapa 6 (CPU Nova Copiando Caderno):* Cópia de composição auxiliar de cadernos técnicos SINAPI (`02-CADERNOS_TECNICOS/`).
  9. *Etapa 7 (Cotação Internet):* Pesquisa de 3 fornecedores válidos com CNPJ adotando a **MEDIANA (FOB)** no Mapa `DC-007`.
  10. *Etapa 8 (Rascunho de E-mail):* Minuta padronizada de solicitação de cotação (sem envio autônomo).

### Regra Anti-Paralisia / De-Para Funcional
> [!IMPORTANT]
> **É TERMINANTEMENTE PROIBIDO marcar materiais comerciais comuns/padronizados como `DEFINIR_COMPOSICAO`.**  
> Faça o **De-Para funcional**: `[Material + Função + Dimensão]` contra a base SINAPI Bahia.  
> *Exemplo clássico:* Veto à adoção de Luva de Correr (103996) quando se trata de Luva Soldável simples (94663).

---

## 5. Base Central de Conhecimento SUPAT e Precedentes

Base histórica de inteligência e ressalvas: `squad-orcamentista/04-BASE_CONHECIMENTO_SUPAT/`. O checklist deve ser confrontado com a versão aplicável do órgão. O corpus legado está `QUARENTENADO` em `FONTES_PRECEDENTES.json` até revisão caso a caso; ele não prova, por si só, exigência ou aceite oficial.
- **Índice Geral de Temas:** `MAPA_RESSALVAS.md`
- **Checklist Oficial:** `02-CHECKLIST_OFICIAL_SUPAT.md` (ITEM 01 a ITEM 10)
- **Precedentes Temáticos (15 cadernos):** `02-PRECEDENTES/*.md`
- **Banco Estruturado de Precedentes (463 casos minerados):** `04-DADOS/precedentes.json`
- **Consulta via CLI:**
  ```bash
  python "squad-orcamentista/04-BASE_CONHECIMENTO_SUPAT/03-SCRIPTS/consultar_precedente.py" <TEMA | TERMO> [--limit N]
  ```
  *(Exemplos: `LI_AUSENTE`, `CPU_HORAS`, `MEDIANA`, `DUPLICIDADE`, `OBRA_ALEM_DESENHO`, `UNIDADE`).*

---

## 6. Squad de Orçamento FPE e Operação dos Agentes

A elaboração, revisão e auditoria nesta pasta são operadas pelo **Squad de Orçamento FPE** (orquestrado pela skill `squad-orcamento-obra`):

| Agente | Persona | Gatilho / Escopo Principal | O que NUNCA Faz |
|---|---|---|---|
| **`@sofia-squad`** | **Sofia Squad Orçamento** | Coordena obras inteiras, novas revisões (`Rxx`) ou relatórios de análise de órgãos. Inventaria tipologia/regime, despacha o squad e redige o `RELATORIO-SQUAD.docx` (documento interno). | Não orça, não altera células de planilha, não audita e não sela envio. |
| **`@levi-levantador`** | **Levi Levantador** | Extração de quantitativos: **Rota A** (cruzar LI × Projeto 2D/3D), **Rota B** (takeoff do zero), **Rota C** (delta de revisão de projeto). Garante quantidade líquida. | Não precifica, não inventa medidas e não coloca notas de processo nas descrições de envio. |
| **`@elias-eap`** | **Elias EAP** | WBS PMBOK de 3 níveis no padrão Fábio (`_squad/eap.md` **antes** do Otávio). Capítulos de execução, não pasta BIM. Parede e≈15 cm → bloco 9 cm + chapisco + emboço. Implícitos: verga, subleito, trama, tutor, demolições prévias. | Não precifica, não usa `ARQ/EST` como N1, não solta Otávio sobre dump IFC bruto. |
| **`@orcamentista`** | **Otávio Orçamentista** | Precificação pela cascata 1–6 da Fábrica de Preços. Dono do `DC-001` a `DC-006` e quadros OrçaFascio `EC-001`/`EC-002`. Aplica a Matriz Canônica de 10 Colunas. | Proibido lançar código de memória; não altera números sem rodar script de consulta. |
| **`@carlos-cotacao`** | **Carlos Cotação** | Cotações fora de tabela (etapas 7 e 8), âncora técnica idêntica nos 3 fornecedores com CNPJ, Mapa `DC-007` adotando estritamente a **MEDIANA** em regime FOB. | Não pesquisa termos genéricos sem spec âncora; não envia e-mails sozinhos; não usa média aritmética. |
| **`@auditor`** | **Ana Auditora** | Gate de auditoria somente leitura: **Modo A** (simulação SUPAT ITEM 01 a 10 com `amostrar_codigos.py` e deep review na Faixa A da Curva ABC sem BDI) e **Modo B** (redige o `RT-001/RESPOSTAS.docx`). | Não orça, não edita planilhas ou preços, não corrige o que audita, não aceita "CORRIGIDO" sem abrir célula e recusa descrições contaminadas. |
| **`@eduardo-exportador`** | **Eduardo Exportador** | Montagem das 7 pastas oficiais em **área de staging**, em par XLSX+PDF no layout institucional FPE. Sanitiza a coluna Descrição e remove/oculta bastidores. | Não declara o pacote final liberado e não publica em `ENVIO/`; aguarda verificação independente pós-exportação. |
| **`@verificador-exportacao`** | **Verificador de Pacote** | Confere os 7 pares XLSX/PDF já exportados, conteúdo, contagem de páginas, descrições e hashes; emite o gate pós-exportação. | Não altera planilhas, PDFs, preços ou quantitativos e não aprova pacote sem hash e autorização humana registrada. |
| **`@estruturalista`** | **Engenheiro Estrutural** | Apoio especializado em projetos de estruturas, contenções, fundações e laudos SPT vs sapatas/estacas. | Não precifica itens civis gerais. |

### Anti-Alucinação Mecânica de Códigos
1. **Validação Mecânica 100%:** O script `amostrar_codigos.py` valida SINAPI no SQLite e ORSE no cache oficial por `fonte + código`, exige correspondência normalizada de descrição/unidade e bloqueia capacidade não liberada. Código ORSE deve ser cacheado antes da auditoria; uso direto requer a declaração explícita correspondente.
2. **Deep Review na Faixa A:** O auditor inspeciona 100% das falhas apontadas pelo script, 100% dos serviços na Faixa A da Curva ABC sem BDI e até 5 CPUs próprias sorteadas.

### Proveniência das Bases

- `03-BASE_DE_PRECOS/FONTES_DADOS.json` registra competência, UF, regime, arquivo bruto, hash e status de cada fonte.
- A liberação é por capacidade. Fonte, arquivo bruto e hash devem estar válidos; `paradigma_cpu` não equivale a `preco_direto`.
- ORSE oficial está liberada como paradigma e referência de custo em SE. Preço direto fora de SE depende de autorização e justificativa expressas.
- CPU catalogada está liberada como modelo estrutural; preço e uso direto dependem de revalidação na obra.
- `QUARENTENADA`, `NAO_VERIFICADA`, arquivo ausente ou divergência de hash bloqueiam a transição do orçamento.
- A SQLite é índice de consulta; não substitui o arquivo bruto oficial nem sua cadeia de custódia.

---

## 7. Regras Duras e Princípios Inegociáveis

1. **Não inventar:** Quantitativos, preços unitários, BDIs, códigos SINAPI/ORSE, municípios, órgãos, números de contrato ou “o que o órgão aceita”.
2. **Números auditáveis:** Conferir célula a célula via `openpyxl` (`data_only=True` para valores calculados). Cuidado com truncamento de casas decimais.
3. **Unidades ambíguas:** (`par` vs `un`, `m²` vs `m³`, `kg` vs `m`): sinalizar formalmente; nunca decidir sozinho.
4. **Duas colunas na LI:** Identificar qual unidade a composição oficial remunera antes de validar o quantitativo.
5. **Preservação de histórico:** Preservar `R00`, `R01`… Não sobrescrever arquivos de ENVIO já datados; gerar `R+1` para novas emissões.
6. **Acentos e R$:** Manter nomes de municípios e órgãos com acentuação correta; valores monetários formatados em **R$** no artefato final.
7. **Separação oficial vs próprio:** Em relatórios de auditoria, rotular sempre: `Analista` (exigência oficial do órgão) vs `Auditor` (apontamento interno preventivo).
8. **Drive / Google:** Arquivos `.gsheet`/`.gdoc` podem ser atalhos online. Se ilegíveis localmente, solicitar exportação `.xlsx`/`.docx`/`.pdf`.
9. **Segredos e credenciais:** Não copiar certificados (`.pfx`), senhas ou chaves para dentro do repositório ou de artefatos Markdown.
10. **Comunicação externa:** Envio real de e-mails para fornecedores, clientes ou órgãos somente com confirmação explícita do Anderson.
11. **Qtd na planilha = líquida:** Perdas técnicas (10%/15%) pertencem exclusivamente aos coeficientes das composições (CPUs próprias). Não inflar composições oficiais SINAPI (93680, 94195, 103318 já possuem corte e perdas inclusas).
12. **Todas as disciplinas + obra além do desenho:** Não orçar apenas o item explícito do desenho. Paisagismo (98511) requer adubação e tutores; intertravado (93680) requer regularização e subleito; esquadrias requerem vergas/contravergas; telhados requerem trama de apoio.
13. **Reformas e Demolições Prévias:** Ao orçar reformas ou forros novos, a EAP e o levantamento devem obrigatoriamente incluir a remoção prévia de luminárias, grelhas, aparelhos e demolições/desmontagens prévias necessárias.

---

## 8. Diretrizes de Documentos Word: Interno vs. Oficial

### 1. `RELATORIO-SQUAD.docx` (Sofia — Documento Interno)
- **Destinatário:** Anderson e diretoria técnica DFE/FPE.
- **Conteúdo:** Panorama global da obra, matriz de disciplinas auditadas vs não auditadas por ausência de LI, lacunas de projeto, pontos de atenção e decisões pendentes de julgamento técnico.
- **Regra:** **NUNCA** faz parte do pacote entregue ao cliente ou órgão fiscalizador.

### 2. `RT-001 / RESPOSTAS.docx` (Ana — Documento Oficial do Modo B)
- **Destinatário:** Fiscal e comissão técnica do órgão público (SUPAT, SAEB, SEC, SETRE, etc.).
- **Padrão de Resposta:**
  - *Bloco do Analista:* Transcrição exata da ressalva numerada.
  - *Bloco da Resposta:* `RESPOSTA:` formal e objetiva. Se corrigido, declarar no padrão `De -> Para` indicando item, arquivo, valor anterior, valor corrigido e fonte técnica. Se não corrigido, fundamentar em norma ou caderno de encargos.
- **Regra:** Sem observações de bastidores, sem dúvidas e sem remeter a decisão para fora do pacote.

---

## 9. Matriz Canônica de 10 Colunas, Sanitização e Faixa de Bastidores

### Matriz Canônica de 10 Colunas (Faixa Oficial de Envio: Colunas A a J)
Toda planilha sintética oficial (`DC-001` / `EC-001`) DEVE conter exatamente estas 10 colunas:
- **Col A:** Item (EAP 3 níveis, ex.: `01.02.001`)
- **Col B:** Código (SINAPI / ORSE / CPU / COT)
- **Col C:** Banco (SINAPI, ORSE, FPE, COT)
- **Col D:** Descrição Oficial (*Ipsis Verbis* da base oficial, rigorosamente sanitizada)
- **Col E:** Und (`M`, `M2`, `M3`, `UN`, `KG`, `CJ`, etc.)
- **Col F:** Quant. (Líquida)
- **Col G:** Valor Unit (sem BDI)
- **Col H:** Valor Unit com BDI (`=ROUND(G_row*(1+$BDI$), 2)`)
- **Col I:** Total (`=ROUND(F_row*H_row, 2)`)
- **Col J:** Peso % (`=ROUND((I_row/$TOTAL_GERAL$)*100, 2)`)

### Faixa de Bastidores (Colunas K e L — Oculta na Exportação)
- **Col K:** Status Interno (`VALIDADO`, `COTACAO_PENDENTE`, `REVISAR_QUANTITATIVO`...)
- **Col L:** Observação Interna (Notas e dúvidas de projeto, notas de processo)

> [!CAUTION]
> **É TERMINANTEMENTE PROIBIDO incluir anotações de processo na coluna Descrição (Col D) da planilha de envio.**  
> Exemplos de contaminação vetados:
> - `(UFC não conseguiu quantificar)`
> - `(Estrutura - está faltando algum item)`
> - `(revisar)`, `(confirmar)`, `(ver memorial)`, `(ver relatório)`, `(pendente)`, `(DEFINIR_COMPOSICAO)`
> - Comentários internos ou respostas a análises fiscais.

- **Validação:** O Eduardo sanitiza as descrições via regex antes de gerar o pacote final. Se houver anotação de processo na Coluna D, o envio é bloqueado.

---

## 10. BDI, Cronograma e Curva ABC sem BDI

### BDI de Obras Civis vs. Diferenciado
- **BDI de Obras Civis:** Não existe taxa universal. Deve ser calculado pela fórmula paramétrica aplicável, com parâmetros rastreáveis do edital, regime tributário, localidade, riscos e justificativas, observando o **Acórdão 2622/2013-TCU**.
- **BDI Diferenciado (Reduzido):** Também não possui percentual automático. Só pode ser calculado e aplicado quando houver mero fornecimento de materiais/equipamentos de alta relevância desmembrados da montagem e quando os pressupostos jurídicos e econômicos estiverem documentados, à luz da Súmula 253 do TCU.
- Se a obra **não** possuir fornecimento relevante de equipamentos, **não** criar coluna extra nem citar BDI diferenciado no `DC-001`.

### Curva ABC sem BDI (Custo Direto)
- A Curva ABC (`DC-002`) deve ser ranqueada pelo **custo direto**:
  $$\text{Valor Total Direto} = \text{Quantidade} \times \text{Valor Unitário sem BDI}$$
- As faixas **A (80%)**, **B (15%)** e **C (5%)** são calculadas sobre a soma **sem BDI**.
- A Faixa A desta curva determina os itens obrigatórios para o **ITEM 03** (Composições Analíticas `DC-003`), **ITEM 04** (Cotações no Mapa `DC-007`) e **ITEM 10** (Memória de Cálculo).

### Cronograma Físico-Financeiro (`DC-004`)
- Células com desembolso $>0\%$ destacadas em azul suave (`#D9E1F2`) e negrito; meses zerados limpos.
- **Regra de Ouro:** **Valor do Orçamento (com BDI) = Valor do Cronograma (diferença R$ 0,00 centavo a centavo)**.

---

## 11. Padrão Oficial de Layout e Exportação de Pacotes (DC-001 a DC-007)

Ao gerar, reexportar ou formatar pacotes oficiais de envio de orçamentos (pastas `ENVIO/Rxx-DD.MM.AAAA/`):

### Estrutura das 7 Pastas Oficiais (Par XLSX + PDF)
1. `01-ORÇAMENTO` / `DC-001 - ORÇAMENTO`: Planilha sintética de 10 colunas padrão (`Item`, `Código`, `Banco`, `Descrição`, `Und`, `Quant.`, `Valor Unit`, `Valor Unit com BDI`, `Total`, `Peso %`). Fórmulas dinâmicas ativas (`ROUND`, `SUM`).
2. `02-CURVA ABC` / `DC-002 - CURVA ABC`: Curva ABC de Serviços gerada **sem BDI** (Faixas A/B/C 80/15/5%), coluna de descrição larga com `wrap_text=True`.
3. `03-COMPOSIÇÕES ANALÍTICAS` / `DC-003 - COMPOSIÇÕES ANALÍTICAS`: Caderno de composições principais e auxiliares para os itens da Faixa A e CPUs próprias.
4. `04-CRONOGRAMA FÍSICO-FINANCEIRO` / `DC-004 - CRONOGRAMA`: Cronograma por macroetapas com destaque `#D9E1F2` e fechamento exato em R$ 0,00 de diferença.
5. `05-BDI` / `DC-005 - BDI`: Demonstrativo analítico do BDI (Acórdão 2622/2013-TCU) em página única com parâmetros oficiais.
6. `06-ENCARGOS SOCIAIS` / `DC-006 - ENCARGOS`: Demonstrativo analítico dos encargos sociais (Horista e Mensalista - Grupos A, B, C e D).
7. `07-MAPA DE COTAÇÃO` / `DC-007 - MAPA DE COTAÇÃO`: Mapa em 7 colunas padrão, $\ge 3$ fornecedores com CNPJ e critério exclusivo da **MEDIANA (FOB)**.

### Identidade Visual Institucional FPE
- **Cabeçalho de Colunas:** Fundo azul escuro `#1F4E79`, fonte Calibri branca em negrito.
- **Capítulos Principais (Nível 1):** Fundo cinza `#D9D9D9`, texto em negrito.
- **Sub-etapas (Nível 2):** Fundo verde suave `#C6EFCE`, texto em negrito.
- **Cabeçalho Superior de Página:**
  - *Esquerda (Col A/B):* Brasão / Logotipo do **Órgão ou Prefeitura Contratante**.
  - *Centro (Col C a H):* Título do projeto, contrato e objeto da obra.
  - *Direita (Col I):* Logomarca oficial da **FPE (FP Fábio Pereira)**.
  - *Extremo Direito (Col J):* Data-base da revisão (`DD/MM/AAAA`).
  - *Altura dos logos:* ~35–45px, proporcionais, sem sobrepor células ou textos.

### Regras Institucionais
- Pacote emitido em nome exclusivo da **FPE** (`FPE ENGENHARIA E PROJETOS LTDA` / `FPE Projetos`).
- **NUNCA** incluir nome pessoal do Anderson ou da equipe nos rodapés ou assinaturas da entrega externa.
- Preservar o número da revisão contratada (ex.: `R00`) em todas as peças e cabeçalhos.
- Configurar impressão (`PageSetup.FitToPagesWide = 1`, `FitToPagesTall = 1` para folhas únicas).

---

## 12. Skills, Scripts e Ferramentas Úteis

| Ferramenta / Skill | Comando / Arquivo | Finalidade Principal |
|---|---|---|
| **`squad-orcamento-obra`** | `@sofia-squad` | Orquestração do Squad FPE para obras completas, novas revisões e loops integrados. |
| **`auditoria-orcamento-obra`** | `@auditor` | Simulação oficial SUPAT ITEM 01 a 10 (Modo A) e redação de respostas técnicas RT-001 (Modo B). |
| **`orcamentista-obras`** | `@orcamentista` | Elaboração de planilhas sintéticas/analíticas, BDI, encargos e cronogramas. |
| **`composicao-propria-obra`** | `build_cpu_workbook.py` / `validate_cpu.py` | Criação, parametrização e auditoria de CPUs próprias analíticas. |
| **`levantamento-quantitativos`** | `build_memoria_calculo.py` | Extração 2D/BIM/IFC com compatibilização estrita de unidades e desconto de vãos. |
| **Consulta Preços (CLI)** | `python "03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py" --fonte SINAPI --regime nao_desonerado <CODIGO>` | Consulta por fonte e regime explícitos; fonte não liberada é bloqueada. |
| **Consulta Precedentes (CLI)** | `python "04-BASE_CONHECIMENTO_SUPAT/03-SCRIPTS/consultar_precedente.py" --diagnostico <TEMA>` | Localização diagnóstica no corpus legado; confirmar cada texto no documento de origem antes de citar. |
| **Simulação Pré-ENVIO** | `python "scripts/simulate_supat_preenvio.py" <pasta_obra> --regime <regime> --evidencias <checkpoints.json> --out <auditoria.json>` | Automação fail-closed do checklist ITEM 01 a 10 antes da exportação. |
| **Validação Mecânica** | `python "scripts/amostrar_codigos.py" <planilha> --regime <regime>` | Validação por fonte+código, descrição, unidade, preço e fórmulas calculadas. |
| **Verificação Pós-Exportação** | `python "scripts/verify_export_package.py" <pasta_staging> --estado <estado.json> --out <verificacao.json>` | Confere os 7 pares, XLSX/PDF e hashes antes da liberação final. |

---

## 13. Checklist Rápido antes de "Pronto" e Gate de Envio

- [ ] Obra e **revisão (`Rxx`)** identificadas e declaradas formalmente.
- [ ] Fonte de quantitativos citada (prancha, memorial, LI por disciplina com Rxx).
- [ ] Quantitativos na planilha rigorosamente **líquidos** na unidade exata da CPU.
- [ ] Varredura completa de **100% das disciplinas** de projeto e inclusão de **obra além do desenho** e demolições prévias.
- [ ] Códigos SINAPI/ORSE validados mecanicamente no script SQLite (zero alucinação e zero `DEFINIR_COMPOSICAO`).
- [ ] Mapa de Cotações (`DC-007`) com $\ge 3$ fornecedores com CNPJ adotando estritamente a **MEDIANA (FOB)**.
- [ ] Curva ABC (`DC-002`) gerada **sem BDI** para sustentação dos itens 03, 04 e 10.
- [ ] Cronograma Físico-Financeiro (`DC-004`) com **Orçamento = Cronograma (diferença R$ 0,00 centavo a centavo)**.
- [ ] Estrutura na **Matriz Canônica de 10 Colunas (A a J)** com notas de bastidores isoladas em K e L.
- [ ] Descrições em `DC-001` e `EC-001` **rigorosamente sanitizadas** (zero anotações de processo entre parênteses).
- [ ] Identidade visual FPE aplicada: cabeçalhos `#1F4E79`, brasão à esquerda, FPE à direita, sem nomes pessoais.
- [ ] Pacote montado nas **7 pastas numeradas (`01` a `07`)** em par `.xlsx` + `.pdf`.
- [ ] Gate pré-exportação atingiu `PRE_LIBERADO`, com auditoria somente leitura e checkpoints humanos assinados.
- [ ] Eduardo gerou os arquivos em staging, sem publicar sobre envio anterior.
- [ ] Verificador independente conferiu os 7 pares XLSX/PDF, registrou hashes e emitiu gate pós-exportação.
- [ ] Gate de Envio atingiu **`LIBERADO`**. Pendência de terceiro permanece bloqueio até evidência e autorização formal registradas; não há liberação implícita.

---

*Ao estabilizar um padrão novo (órgão, checklist, regra de medição, tabela), atualize este arquivo em vez de deixá-lo disperso no chat.*
