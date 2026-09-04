#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gerar_indices_md.py — Regenera os 15 arquivos Markdown e o MAPA_COMPOSICOES.md
a partir do banco SQLite base_precos.db.
"""

import sqlite3
import os
import re

base_dir = r"g:\Meu Drive\DFE PROJETOS OFICIAL\CLIENTES\16. FABIO - FPE\00-BASE_DE_PRECOS_SINAPI_ORSE"
db_path = os.path.join(base_dir, "base_precos.db")
out_md_dir = os.path.join(base_dir, "03-DISCIPLINAS_MARKDOWN")
os.makedirs(out_md_dir, exist_ok=True)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Disciplinas
disc_info = [
    (1, "01_SERVICOS_PRELIMINARES.md", "SERVIÇOS PRELIMINARES", "Demolições, remoções, locação de obra, instalações provisórias, canteiro e movimentação de terra preliminar."),
    (2, "02_INFRAESTRUTURA_E_FUNDACOES.md", "INFRAESTRUTURA E FUNDAÇÕES", "Escavações, sapatas, estacas, blocos de coroamento, vigas baldrame, radiers, contenções e rebaixamento de lençol."),
    (3, "03_ESTRUTURAS.md", "ESTRUTURAS DE CONCRETO, AÇO E MADEIRA", "Formas, escoramentos, armações em aço CA-50/60, concretagem usinada e moldada in loco, estruturas metálicas e lajes."),
    (4, "04_PAREDES_E_PAINEIS.md", "PAREDES, ALVENARIAS E PAINÉIS", "Alvenarias de vedação cerâmica e blocos de concreto, drywall, painéis termoacústicos, vergas e contravergas."),
    (5, "05_ESQUADRIAS_E_FERRAGENS.md", "ESQUADRIAS, FERRAGENS E VIDROS", "Portas e janelas em alumínio, madeira, aço e PVC, vidros temperados/laminados, brises, fachadas pele de vidro e ferragens."),
    (6, "06_COBERTURAS_E_PROTECOES.md", "COBERTURAS E ESTRUTURAS DE TELHADO", "Estruturas metálicas e de madeira para telhados, telhas cerâmicas, metálicas, termoacústicas, calhas, rufos e condutores."),
    (7, "07_IMPERMEABILIZACOES.md", "IMPERMEABILIZAÇÕES E TRATAMENTOS", "Mantas asfálticas, argamassas poliméricas impermeabilizantes, hidrofugantes, pinturas asfálticas e tratamento de juntas."),
    (8, "08_REVESTIMENTOS_PAREDES_TETOS.md", "REVESTIMENTOS DE PAREDES E TETOS", "Chapisco, emboço, reboco, massas, forros de gesso/PVC/mineral, placas cerâmicas, azulejos e pastilhas de fachada."),
    (9, "09_PAVIMENTACOES.md", "PAVIMENTAÇÕES E PISOS", "Contrapisos, pisos cerâmicos, porcelanatos, pisos intertravados de concreto, paralelepípedos, granitina e pisos podotáteis."),
    (10, "10_INSTALACOES_HIDROSSANITARIAS.md", "INSTALAÇÕES HIDRÁULICAS E SANITÁRIAS", "Tubulações de água fria/quente em PVC, CPVC, PPR e Cobre, esgoto predial, caixas sifonadas, louças, metais e bombas."),
    (11, "11_INSTALACOES_ELETRICAS.md", "INSTALAÇÕES ELÉTRICAS E TELECOMUNICAÇÕES", "Eletrodutos, cabos flexíveis, quadros de distribuição, disjuntores, tomadas, interruptores, luminárias LED, dados e subestações."),
    (12, "12_SPDA_E_COMBATE_A_INCENDIO.md", "SPDA E COMBATE A INCÊNDIO", "Sistema de proteção contra descargas atmosféricas (para-raios), aterramentos, tubulações galvanizadas, hidrantes e extintores."),
    (13, "13_PINTURAS.md", "PINTURAS E ACABAMENTOS", "Pinturas internas e externas látex PVA/acrílica, esmaltes sintéticos sobre madeira/metal, vernizes, texturas e epóxi."),
    (14, "14_PAISAGISMO_E_COMPLEMENTARES.md", "SERVIÇOS COMPLEMENTARES E PAISAGISMO", "Plantio de gramas e mudas, cercas, gradis, alambrados, mobiliário urbano, quadras poliesportivas e limpeza final da obra."),
    (15, "15_URBANIZACAO_E_VIAS.md", "URBANIZAÇÃO E PAVIMENTAÇÃO VIÁRIA", "Guias e sarjetas, calçadas de concreto, pavimentação asfáltica CBUQ, drenagem pluvial urbana (bueiros/aduelas) e sinalização viária.")
]

# Regras de classificação de grupos SINAPI para as 15 Macro-Disciplinas
def map_sinapi_group_to_disc(grp_name, desc):
    g = grp_name.lower()
    d = desc.lower()
    
    if any(k in g for k in ['demoli', 'remo', 'loca', 'canteiro', 'transporte de materiais dentro', 'transporte, carga e descarga', 'limpeza de obra', 'supress', 'livro sinapi']):
        return 1
    if any(k in g for k in ['estaca', 'funda', 'escava', 'aterro', 'reaterro', 'escoramento e preparo de fundo', 'esgotamento', 'tubul', 'cortinas e muros de arrimo', 'grampo para solo', 'tirantes', 'lastro']):
        return 2
    if any(k in g for k in ['arma', 'concreta', 'produ', 'f', 'estruturas pr', 'lajes pr', 'estruturas de madeira', 'solda de topo', 'usinagens']) and not any(k in g for k in ['pavimento', 'passeio']):
        return 3
    if any(k in g for k in ['alvenaria', 'drywall', 'divis', 'vergas, contravergas']):
        return 4
    if any(k in g for k in ['esquadrias', 'portas', 'janelas', 'brises', 'pele de vidro', 'vidros e espelhos', 'guarda-corpo, corrim']):
        return 5
    if any(k in g for k in ['cobertura', 'telha', 'estrutura e trama']):
        return 6
    if any(k in g for k in ['impermeabili', 'junta']):
        return 7
    if any(k in g for k in ['chapisco', 'massa', 'monocapa', 'forros', 'gesso', 'revestimentos cer', 'fachadas com placas']):
        return 8
    if any(k in g for k in ['contrapiso', 'pisos', 'pavimento intertravado', 'pavimenta', 'pedras poli', 'podot', 'acessibilidade', 'radier, piso']):
        return 9
    if any(k in g for k in ['hidr', 'esgoto', 'gua fria', 'gua quente', 'guas pluviais', 'lou', 'v', 'bombas hidr', 'caixas de', 'caixas enterradas', 'fossas e sumidouros', 'liga']):
        return 10
    if any(k in g for k in ['el', 'eletrocalhas', 'cabos', 'quadros', 'transformadores', 'energia solar', 'telefonia', 'luz', 'ilumina', 'postes de concreto e met']):
        return 11
    if any(k in g for k in ['spda', 'descargas atmosf', 'inc', 'g']):
        return 12
    if any(k in g for k in ['pintura']):
        return 13
    if any(k in g for k in ['paisagismo', 'cercas, protetores e alambrados', 'parquinhos', 'quadras', 'mobili', 'equipamentos de prote']):
        return 14
    if any(k in g for k in ['asfalto', 'guias e sarjetas', 'passeios de concreto', 'sinaliza', 'bueiros', 'aduelas', 'drenagem', 'drenos', 'dutos', 'po', 'redes de', 'dragagem', 'perfora']):
        return 15
        
    return 1

# Mapear ORSE para disciplinas
def map_orse_group_to_disc(grp_str, desc):
    m = re.search(r'(\d+)', grp_str)
    if m:
        g_num = int(m.group(1))
        if 1 <= g_num <= 15:
            return g_num
    return 1

sinapi_by_disc = {i: [] for i in range(1, 16)}
orse_by_disc = {i: [] for i in range(1, 16)}

# 1. Carregar SINAPI
cur.execute("SELECT codigo, descricao, unidade, grupo, custo_deson, custo_nao_deson FROM composicoes WHERE fonte = 'SINAPI'")
for r in cur.fetchall():
    cod, desc, unid, grp, c_d, c_nd = r
    d_id = map_sinapi_group_to_disc(grp, desc)
    sinapi_by_disc[d_id].append({
        'codigo': cod,
        'descricao': desc,
        'unidade': unid,
        'grupo': grp,
        'custo_deson': c_d,
        'custo_nao_deson': c_nd
    })

# 2. Carregar ORSE
cur.execute("SELECT codigo, descricao, unidade, grupo, custo_deson, custo_nao_deson FROM composicoes WHERE fonte = 'ORSE'")
for r in cur.fetchall():
    cod, desc, unid, grp, c_d, c_nd = r
    d_id = map_orse_group_to_disc(grp, desc)
    orse_by_disc[d_id].append({
        'codigo': cod,
        'descricao': desc,
        'unidade': unid,
        'grupo': grp,
        'preco': c_nd # Preço do ORSE
    })

print("Gerando arquivos Markdown segmentados...")
for d_id, fn, titulo, desc_d in disc_info:
    md_path = os.path.join(out_md_dir, fn)
    s_items = sinapi_by_disc.get(d_id, [])
    o_items = orse_by_disc.get(d_id, [])
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Disciplina {d_id:02d}: {titulo}\n\n")
        f.write(f"> **Escopo:** {desc_d}\n")
        f.write(f"> **Data-Base SINAPI:** Bahia (BA) — 03/2025 (Com e Sem Desoneração)  \n")
        f.write(f"> **Data-Base ORSE:** Sergipe / CEHOP — Junho/2026  \n\n")
        
        f.write("## Diretriz de Uso para a IA (Padrão SUPAT / FPE)\n")
        f.write("1. **1ª Prioridade (SINAPI Oficial):** Se o serviço constar na **Tabela 1 (SINAPI)** abaixo, adote o código e execute `python 06-SCRIPTS/consultar_composicao.py <codigo>` para ver o analítico completo.\n")
        f.write("2. **2ª Prioridade (CPU Própria com Referência ORSE):** Se não existir no SINAPI mas constar na **Tabela 2 (ORSE)**, crie uma **Composição Própria (DC-003)** citando o paradigma (ex.: `REF. ORSE xxxxx`), **substituindo a mão de obra pelos códigos SINAPI com Encargos Complementares (88316, 88309, 88264, etc.)** e insumos básicos SINAPI.\n")
        f.write("3. **3ª Prioridade (ORSE Direto):** Use código ORSE puro apenas quando formalmente autorizado pelo órgão/edital.\n\n")
        f.write("---\n\n")
        
        # Tabela 1: SINAPI
        f.write(f"## 1. COMPOSIÇÕES SINAPI (1ª PRIORIDADE) — [{len(s_items)} itens]\n\n")
        f.write("| Código | Descrição Completa do Serviço SINAPI | Un | Custo Deson. (R$) | Custo Não Deson. (R$) | Subgrupo SINAPI |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :--- |\n")
        for it in s_items:
            c_desc = it['descricao'].replace('|', '/')
            cd_str = f"{it['custo_deson']:.2f}" if it['custo_deson'] > 0 else "Sem custo coletado"
            cnd_str = f"{it['custo_nao_deson']:.2f}" if it['custo_nao_deson'] > 0 else "Sem custo coletado"
            f.write(f"| `{it['codigo']}` | {c_desc} | {it['unidade']} | {cd_str} | {cnd_str} | {it['grupo']} |\n")
            
        f.write("\n---\n\n")
        
        # Tabela 2: ORSE
        f.write(f"## 2. COMPOSIÇÕES ORSE / PARADIGMAS DE REFERÊNCIA (2ª PRIORIDADE - SUPAT) — [{len(o_items)} itens]\n\n")
        f.write("| Código ORSE | Descrição do Serviço ORSE | Un | Preço Unit. (R$) | Diretriz de Conversão SUPAT (Mão de Obra e Insumos SINAPI) |\n")
        f.write("| :---: | :--- | :---: | :---: | :--- |\n")
        for it in o_items:
            o_desc = it['descricao'].replace('|', '/')
            p_str = f"{it['preco']:.2f}" if it['preco'] > 0 else "Sob consulta"
            f.write(f"| `{it['codigo']}` | {o_desc} | {it['unidade']} | {p_str} | Converter MO p/ SINAPI (88xxx) + Insumos Básicos SINAPI |\n")
            
    print(f"Gerado: {fn} ({os.path.getsize(md_path)/1024:.1f} KB)")

# Gerar MAPA_COMPOSICOES.md
mapa_path = os.path.join(base_dir, "MAPA_COMPOSICOES.md")
with open(mapa_path, 'w', encoding='utf-8') as f:
    f.write("# MAPA MESTRE DE COMPOSIÇÕES E PREÇOS: SINAPI & ORSE\n\n")
    f.write("**Repositório Central de Engenharia de Custos — Cliente 16. FABIO / FPE Projetos**  \n")
    f.write("**Escopo:** Base oficial consolidada para orçamentação e criação de Composições Próprias (CPUs analíticas) com estrita aderência aos critérios da **SUPAT / SAEB / PGE / SEC / SETRE**.\n\n")
    f.write("---\n\n")
    
    f.write("## 1. Como a IA Deve Consultar Esta Base (Economia Máxima de Tokens)\n\n")
    f.write("Para evitar consumo excessivo de tokens e garantir precisão cirúrgica:\n")
    f.write("1. **NÃO leia todos os arquivos de uma vez.**\n")
    f.write("2. Identifique na tabela abaixo qual é a **Disciplina correspondente ao serviço desejado**.\n")
    f.write("3. Abra **apenas o arquivo `.md` específico** da pasta `03-DISCIPLINAS_MARKDOWN/` (exemplo: para piso porcelanato, abra somente `09_PAVIMENTACOES.md`).\n")
    f.write("4. Localize o código do serviço e rode o script de consulta para extrair o analítico completo:\n")
    f.write("   ```bash\n")
    f.write("   python \"00-BASE_DE_PRECOS_SINAPI_ORSE/06-SCRIPTS/consultar_composicao.py\" <codigo>\n")
    f.write("   ```\n\n")
    f.write("---\n\n")
    
    f.write("## 2. Índice Geral das 15 Disciplinas por Palavra-Chave\n\n")
    f.write("| Nº | Arquivo Markdown | Disciplina / Escopo | Palavras-Chave Principais | Qtd. SINAPI | Qtd. ORSE |\n")
    f.write("| :---: | :--- | :--- | :--- | :---: | :---: |\n")
    
    for d_id, fn, titulo, desc_d in disc_info:
        qtd_s = len(sinapi_by_disc.get(d_id, []))
        qtd_o = len(orse_by_disc.get(d_id, []))
        kw = {
            1: "Demolição, locação, gabarito, tapume, barracão, canteiro, limpeza de terreno, bota-fora",
            2: "Escavação, estaca hélice/raiz/broca, sapata, baldrame, radier, bloco, contenção, rebaixamento",
            3: "Forma compensada/madeira, aço CA-50/CA-60, concreto usinado/fck, laje pré-moldada, viga, pilar, perfil metálico",
            4: "Alvenaria cerâmica, bloco concreto, drywall, gesso acartonado, divisória naval, verga, contraverga",
            5: "Porta madeira/alumínio, janela correr/maxim-ar, vidro temperado/laminado, brise, fechadura, dobradiça",
            6: "Telha cerâmica/fibrocimento/metálica/EPS, estrutura metálica/madeira para telhado, calha, rufo, condutor",
            7: "Manta asfáltica, argamassa polimérica, impermeabilização flexível/rígida, pintura asfáltica, junta de dilatação",
            8: "Chapisco, emboço, reboco, massa única, gesso liso, forro PVC/gesso, azulejo, pastilha, revestimento cerâmico",
            9: "Contrapiso, piso cerâmico, porcelanato retificado/polido, piso intertravado, paralelepípedo, podotátil, granitina",
            10: "Tubo PVC água fria, tubo esgoto, PPR água quente, tubo cobre, caixa sifonada, fossa séptica, lavatório, vaso, torneira",
            11: "Eletroduto PVC/aço, cabo flexível 750V/1kV, disjuntor DIN, quadro de distribuição, tomada, interruptor, luminária LED, eletrocalha",
            12: "SPDA, para-raios Franklin, cabo de cobre nu, haste aterramento, hidrante, extintor pó químico/CO2/água, alarme incêndio",
            13: "Pintura látex acrílica, látex PVA, esmalte sintético, verniz marítimo/copal, textura rústica/grafiato, epóxi piso",
            14: "Grama esmeralda/batatais, plantio muda/árvore, tutor, adubação, cerca arame/alambrado, gradil, parque infantil, trave/quadra",
            15: "Meio-fio/guia, sarjeta, calçada passeio, asfalto CBUQ, pavimentação asfáltica, drenagem pluvial, aduela, bueiro, sinalização viária"
        }[d_id]
        f.write(f"| **{d_id:02d}** | [`{fn}`](file:///g:/Meu%20Drive/DFE%20PROJETOS%20OFICIAL/CLIENTES/16.%20FABIO%20-%20FPE/00-BASE_DE_PRECOS_SINAPI_ORSE/03-DISCIPLINAS_MARKDOWN/{fn}) | **{titulo}** | {kw} | **{qtd_s}** | **{qtd_o}** |\n")
        
    f.write("\n---\n\n")
    
    f.write("## 3. Regras Mandatórias de Criação de CPU Própria (Padrão SUPAT / FPE)\n\n")
    f.write("Ao montar uma composição própria que utilize referência paradigmática no ORSE ou fora do SINAPI:\n\n")
    f.write("1. **Mão de Obra Obrigatória com Encargos Complementares SINAPI:**\n")
    f.write("   - `88316`: Servente com encargos complementares\n")
    f.write("   - `88309`: Pedreiro com encargos complementares\n")
    f.write("   - `88264`: Eletricista com encargos complementares\n")
    f.write("   - `88247`: Auxiliar de eletricista com encargos complementares\n")
    f.write("   - `88267`: Encanador ou bombeiro hidráulico com encargos complementares\n")
    f.write("   - `88248`: Auxiliar de encanador com encargos complementares\n")
    f.write("   - `88256`: Azulejista ou ladrilhista com encargos complementares\n")
    f.write("   - `88314`: Pintor com encargos complementares\n")
    f.write("   - `88262`: Carpinteiro de formas com encargos complementares\n")
    f.write("   - `88245`: Armador com encargos complementares\n")
    f.write("   - `88278`: Montador de estrutura metálica com encargos complementares\n")
    f.write("   - `93565`: Engenheiro civil de obra júnior\n\n")
    f.write("2. **Insumos Básicos:** Adotar sempre o insumo similar do SINAPI (ex.: cimento `00001379`, areia `00000370`, argamassa colante AC-III `00037595`).\n")
    f.write("3. **Insumos Específicos:** Apenas itens não existentes no SINAPI manterão código/preço do ORSE ou cotação formal de 3 fornecedores com menor preço apurado.\n")

conn.close()
print(f"MAPA_COMPOSICOES.md gerado com sucesso em: {mapa_path} ({os.path.getsize(mapa_path)/1024:.1f} KB)")
