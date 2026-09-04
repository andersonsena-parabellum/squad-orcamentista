# MAPA MESTRE DE COMPOSIÇÕES E PREÇOS: SINAPI & ORSE

**Repositório Central de Engenharia de Custos — Cliente 16. FABIO / FPE Projetos**  
**Escopo:** Base oficial consolidada para orçamentação e criação de Composições Próprias (CPUs analíticas) com estrita aderência aos critérios da **SUPAT / SAEB / PGE / SEC / SETRE**.

---

## 1. Como a IA Deve Consultar Esta Base (Economia Máxima de Tokens)

Para evitar consumo excessivo de tokens e garantir precisão cirúrgica:
1. **NÃO leia todos os arquivos de uma vez.**
2. Identifique na tabela abaixo qual é a **Disciplina correspondente ao serviço desejado**.
3. Abra **apenas o arquivo `.md` específico** da pasta `03-DISCIPLINAS_MARKDOWN/` (exemplo: para piso porcelanato, abra somente `09_PAVIMENTACOES.md`).
4. Localize o código do serviço e rode o script de consulta para extrair o analítico completo:
   ```bash
   python "00-BASE_DE_PRECOS_SINAPI_ORSE/06-SCRIPTS/consultar_composicao.py" <codigo>
   ```

---

## 2. Índice Geral das 15 Disciplinas por Palavra-Chave

| Nº | Arquivo Markdown | Disciplina / Escopo | Palavras-Chave Principais | Qtd. SINAPI | Qtd. ORSE |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **01** | [`01_SERVICOS_PRELIMINARES.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/01_SERVICOS_PRELIMINARES.md) | **SERVIÇOS PRELIMINARES** | Demolição, locação, gabarito, tapume, barracão, canteiro, limpeza de terreno, bota-fora | **1328** | **70** |
| **02** | [`02_INFRAESTRUTURA_E_FUNDACOES.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/02_INFRAESTRUTURA_E_FUNDACOES.md) | **INFRAESTRUTURA E FUNDAÇÕES** | Escavação, estaca hélice/raiz/broca, sapata, baldrame, radier, bloco, contenção, rebaixamento | **836** | **70** |
| **03** | [`03_ESTRUTURAS.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/03_ESTRUTURAS.md) | **ESTRUTURAS DE CONCRETO, AÇO E MADEIRA** | Forma compensada/madeira, aço CA-50/CA-60, concreto usinado/fck, laje pré-moldada, viga, pilar, perfil metálico | **2017** | **70** |
| **04** | [`04_PAREDES_E_PAINEIS.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/04_PAREDES_E_PAINEIS.md) | **PAREDES, ALVENARIAS E PAINÉIS** | Alvenaria cerâmica, bloco concreto, drywall, gesso acartonado, divisória naval, verga, contraverga | **141** | **70** |
| **05** | [`05_ESQUADRIAS_E_FERRAGENS.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/05_ESQUADRIAS_E_FERRAGENS.md) | **ESQUADRIAS, FERRAGENS E VIDROS** | Porta madeira/alumínio, janela correr/maxim-ar, vidro temperado/laminado, brise, fechadura, dobradiça | **234** | **70** |
| **06** | [`06_COBERTURAS_E_PROTECOES.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/06_COBERTURAS_E_PROTECOES.md) | **COBERTURAS E ESTRUTURAS DE TELHADO** | Telha cerâmica/fibrocimento/metálica/EPS, estrutura metálica/madeira para telhado, calha, rufo, condutor | **152** | **70** |
| **07** | [`07_IMPERMEABILIZACOES.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/07_IMPERMEABILIZACOES.md) | **IMPERMEABILIZAÇÕES E TRATAMENTOS** | Manta asfáltica, argamassa polimérica, impermeabilização flexível/rígida, pintura asfáltica, junta de dilatação | **29** | **70** |
| **08** | [`08_REVESTIMENTOS_PAREDES_TETOS.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/08_REVESTIMENTOS_PAREDES_TETOS.md) | **REVESTIMENTOS DE PAREDES E TETOS** | Chapisco, emboço, reboco, massa única, gesso liso, forro PVC/gesso, azulejo, pastilha, revestimento cerâmico | **432** | **70** |
| **09** | [`09_PAVIMENTACOES.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/09_PAVIMENTACOES.md) | **PAVIMENTAÇÕES E PISOS** | Contrapiso, piso cerâmico, porcelanato retificado/polido, piso intertravado, paralelepípedo, podotátil, granitina | **235** | **70** |
| **10** | [`10_INSTALACOES_HIDROSSANITARIAS.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/10_INSTALACOES_HIDROSSANITARIAS.md) | **INSTALAÇÕES HIDRÁULICAS E SANITÁRIAS** | Tubo PVC água fria, tubo esgoto, PPR água quente, tubo cobre, caixa sifonada, fossa séptica, lavatório, vaso, torneira | **2169** | **70** |
| **11** | [`11_INSTALACOES_ELETRICAS.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/11_INSTALACOES_ELETRICAS.md) | **INSTALAÇÕES ELÉTRICAS E TELECOMUNICAÇÕES** | Eletroduto PVC/aço, cabo flexível 750V/1kV, disjuntor DIN, quadro de distribuição, tomada, interruptor, luminária LED, eletrocalha | **726** | **70** |
| **12** | [`12_SPDA_E_COMBATE_A_INCENDIO.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/12_SPDA_E_COMBATE_A_INCENDIO.md) | **SPDA E COMBATE A INCÊNDIO** | SPDA, para-raios Franklin, cabo de cobre nu, haste aterramento, hidrante, extintor pó químico/CO2/água, alarme incêndio | **965** | **70** |
| **13** | [`13_PINTURAS.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/13_PINTURAS.md) | **PINTURAS E ACABAMENTOS** | Pintura látex acrílica, látex PVA, esmalte sintético, verniz marítimo/copal, textura rústica/grafiato, epóxi piso | **95** | **70** |
| **14** | [`14_PAISAGISMO_E_COMPLEMENTARES.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/14_PAISAGISMO_E_COMPLEMENTARES.md) | **SERVIÇOS COMPLEMENTARES E PAISAGISMO** | Grama esmeralda/batatais, plantio muda/árvore, tutor, adubação, cerca arame/alambrado, gradil, parque infantil, trave/quadra | **64** | **70** |
| **15** | [`15_URBANIZACAO_E_VIAS.md`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/15_URBANIZACAO_E_VIAS.md) | **URBANIZAÇÃO E PAVIMENTAÇÃO VIÁRIA** | Meio-fio/guia, sarjeta, calçada passeio, asfalto CBUQ, pavimentação asfáltica, drenagem pluvial, aduela, bueiro, sinalização viária | **230** | **70** |

---

## 3. Regras Mandatórias de Criação de CPU Própria (Padrão SUPAT / FPE)

Ao montar uma composição própria que utilize referência paradigmática no ORSE ou fora do SINAPI:

1. **Mão de Obra Obrigatória com Encargos Complementares SINAPI:**
   - `88316`: Servente com encargos complementares
   - `88309`: Pedreiro com encargos complementares
   - `88264`: Eletricista com encargos complementares
   - `88247`: Auxiliar de eletricista com encargos complementares
   - `88267`: Encanador ou bombeiro hidráulico com encargos complementares
   - `88248`: Auxiliar de encanador com encargos complementares
   - `88256`: Azulejista ou ladrilhista com encargos complementares
   - `88314`: Pintor com encargos complementares
   - `88262`: Carpinteiro de formas com encargos complementares
   - `88245`: Armador com encargos complementares
   - `88278`: Montador de estrutura metálica com encargos complementares
   - `93565`: Engenheiro civil de obra júnior

2. **Insumos Básicos:** Adotar sempre o insumo similar do SINAPI (ex.: cimento `00001379`, areia `00000370`, argamassa colante AC-III `00037595`).
3. **Insumos Específicos:** Apenas itens não existentes no SINAPI manterão código/preço do ORSE ou cotação formal de 3 fornecedores com menor preço apurado.
