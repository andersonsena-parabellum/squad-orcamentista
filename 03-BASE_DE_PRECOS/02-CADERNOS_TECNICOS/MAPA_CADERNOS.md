# MAPA DE CADERNOS TÉCNICOS E CRITÉRIOS DE MEDIÇÃO SINAPI

**Guia de Consulta de Regras Oficiais da Caixa Econômica Federal — Cliente 16. FABIO / FPE**  
**Objetivo:** Permitir que o Engenheiro Orçamentista e a IA copiem exatamente os critérios de medição, produtividade, inclusões e exclusões de cada família sem estimativas arbitrárias.

---

## 1. Famílias Documentadas e Arquivos de Regras

| Família SINAPI | Arquivo de Critérios (.md) | Famílias de Códigos | Itens Críticos de Atenção (O que NÃO está incluso) |
| :--- | :--- | :--- | :--- |
| **PAVI / INTE** | [`CADERNO_PAVI_INTE_PISOS.md`](md/CADERNO_PAVI_INTE_PISOS.md) | `93680` a `93690`, `88476` | `93680` NÃO inclui base de BGS, regularização de subleito nem meio-fio de contenção lateral. |
| **PAIS** | [`CADERNO_PAIS_PAISAGISMO.md`](md/CADERNO_PAIS_PAISAGISMO.md) | `98504` a `98525` | `98511` (plantio de árvore) NÃO inclui abertura de cova (`98519`/`98520`), adubação nem tutor de madeira. |
| **COBE** | [`CADERNO_COBE_COBERTURAS.md`](md/CADERNO_COBE_COBERTURAS.md) | `94195` a `94220`, `92541` | `94195` já tem perda de telha e transporte vertical; NÃO inclui trama de madeira/aço, cumeeira nem calha. |
| **ALVE** | [`CADERNO_ALVE_ALVENARIAS.md`](md/CADERNO_ALVE_ALVENARIAS.md) | `87495` a `87540`, `93580` | Vãos $\le 2 m^2$ não descontam; vãos $> 2 m^2$ descontam excedente; vergas e contravergas à parte. |
| **REVE** | [`CADERNO_REVE_REVESTIMENTOS.md`](md/CADERNO_REVE_REVESTIMENTOS.md) | `87267`, `87775`, `87878` | Mão de obra correta = Azulejista `88256`; argamassa AC-II/AC-III e rejunte calibrados conforme formato. |

---

## 2. Como a IA Deve Consultar os Cadernos
1. Identifique a família do serviço em questão.
2. Abra **apenas o arquivo correspondente** na pasta `05-CADERNOS_TECNICOS_SINAPI/md/`.
3. Verifique a seção **"O que NÃO ESTÁ INCLUSO"** para lançar as composições complementares necessárias na planilha orçamentária (evitando orçamentos incompletos e ressalvas em auditoria).
