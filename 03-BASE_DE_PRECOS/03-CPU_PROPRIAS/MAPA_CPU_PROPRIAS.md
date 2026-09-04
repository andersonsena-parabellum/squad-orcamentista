# MAPA GERAL DE COMPOSIÇÕES PRÓPRIAS (CPUs CATALOGADAS)

**Repositório de CPUs Próprias da DFE / FPE Projetos**  
**Regra de Ouro:** Este catálogo indexa **apenas as composições próprias salvas oficialmente nesta pasta (`04-CPU_PROPRIAS/_ORIGINAIS/`)**.

---

## 1. Diretriz de Reutilização de Preço e Estrutura

Ao reaproveitar uma CPU deste catálogo:

1. **Estrutura (`ESTRUTURA_OK`):** A estrutura de mão de obra (funções, coeficientes de produtividade) e a lista de materiais podem ser integralmente reaproveitadas.
2. **Status do Preço:**
   - `VIGENTE`: Preço com cotação formal há menos de 180 dias.
   - `PRECO_VENCIDO`: Cotação com data > 180 dias. **Requer recotação dos insumos cotados (`INS.xxx`)**.
   - `PRECO_SEM_DATA`: CPU sem registro temporal de cotação. **Obrigatório recotar fornecedores**.
3. **Substituição por Insumos Oficiais SINAPI:** Se o material próprio (`INS.xxx` / `PRP-xxx`) agora já existir no SINAPI (ex.: madeira de assento `00006182`, seixo rolado `00004734`, argamassa AC-III `00037595`), **descarte o insumo próprio** e adote o código oficial.

---

## 2. Índice de CPUs Próprias Catalogadas

| Código CPU | Descrição do Serviço | Un | Disciplina | Ref. Paradigmática | Data Cotação | Status do Preço | Arquivo da Ficha |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `PRP-001-TI` | Rack 19 pol 44U padrão telecom com acessórios | UN | 11 - Elétrica / TI | REF. SINAPI 93565 | 2026-06-15 | `VIGENTE` | [`por_disciplina/CPU_PRP_001_RACK_44U.md`](por_disciplina/CPU_PRP_001_RACK_44U.md) |
| `PRP-002-AV` | Sonofletor de embutir 30W com transformador de linha | UN | 11 - Elétrica / TI | REF. ORSE 10940 | 2026-05-20 | `VIGENTE` | [`por_disciplina/CPU_PRP_002_SONOFLETOR.md`](por_disciplina/CPU_PRP_002_SONOFLETOR.md) |
| `PRP-003-EST`| Estrutura metálica treliçada em perfis dobrados galvanizados | KG | 03 - Estruturas | REF. SINAPI 100776 | 2026-04-10 | `VIGENTE` | [`por_disciplina/CPU_PRP_003_ESTRUTURA_MET.md`](por_disciplina/CPU_PRP_003_ESTRUTURA_MET.md) |

---

## 3. Como Adicionar Novas CPUs ao Catálogo
1. Salve a planilha ou documento da composição própria em: `04-CPU_PROPRIAS/_ORIGINAIS/`.
2. Execute o script de catalogação automática:
   ```bash
   python "00-BASE_DE_PRECOS_SINAPI_ORSE/06-SCRIPTS/catalogar_cpu_propria.py"
   ```
