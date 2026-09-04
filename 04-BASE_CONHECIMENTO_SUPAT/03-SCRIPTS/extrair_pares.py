import os
import re
import json
import docx
import pypdf
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(r"g:\Meu Drive\DFE PROJETOS OFICIAL\CLIENTES\16. FABIO - FPE")
BASE_DIR = ROOT_DIR / "00-BASE_CONHECIMENTO_SUPAT"
OUTPUT_JSON = BASE_DIR / "04-DADOS" / "precedentes.json"
PRECEDENTES_DIR = BASE_DIR / "03-PRECEDENTES"
MAPA_MD = BASE_DIR / "MAPA_RESSALVAS.md"

# Checklist mapping
CHECKLIST_ITEMS = {
    "ITEM 01": "ITEM 01 - Estrutura da Planilha, Adm. Central, Preliminares e Canteiro",
    "ITEM 02": "ITEM 02 - Planilha Orçamentária, Base SINAPI e Compatibilização com LI/Projeto",
    "ITEM 03": "ITEM 03 - Composições Analíticas (Curva ABC 80%) e Análise de CPUs Próprias",
    "ITEM 04": "ITEM 04 - Mapa de Cotações (Itens Não Referenciados, 3 Fornecedores e Mediana)",
    "ITEM 05": "ITEM 05 - Cronograma Físico-Financeiro",
    "ITEM 06": "ITEM 06 - BDI de Obras Civis",
    "ITEM 07": "ITEM 07 - BDI Diferenciado de Materiais e Equipamentos",
    "ITEM 08": "ITEM 08 - Encargos Sociais (Com / Sem Desoneração)",
    "ITEM 09": "ITEM 09 - ART de Orçamento e Levantamento",
    "ITEM 10": "ITEM 10 - Memória de Cálculo e Quantitativos de Obras Civis (ABC 80%)",
    "PROJETISTA": "PROJETISTA - Incompatibilidades de Projeto, Memorial e Pranchas",
    "GERAL": "GERAL - Recomendações e Diretrizes Gerais"
}

def classify_tema(ressalva_text, resposta_text=""):
    t_full = (ressalva_text + " " + resposta_text).lower()
    
    # Check thematic keywords
    if any(k in t_full for k in ["falta lista", "não consta lista", "inserir a lista", "ausência de lista", "sem lista de materiais", "comunicação visual - falta", "não entrou na planilha", "não consta na planilha", "faz parte do escopo da demanda"]):
        return "LI_AUSENTE"
    if any(k in t_full for k in ["consta", "porém na lista", "divergência de quantitativo", "quantidade", "quantitativo diferente", "qtd", "spacato", "177,12", "175,54", "22 un, porém na lista"]):
        if any(k in t_full for k in ["unidade", "unidades", "de 'qtd' para 'un'", "trocar de m", "para un", "kg para m"]):
            return "UNIDADE"
        return "QTD_DIVERGENTE"
    if any(k in t_full for k in ["unidade", "unidades", "de 'qtd' para 'un'", "unidade da composição", "m² para m³", "m para un", "un para m", "de m para pc"]):
        return "UNIDADE"
    if any(k in t_full for k in ["horas", "estimado", "eletrotécnico", "ajudante", "coeficiente", "produtividade", "0,5 horas", "2 horas", "1,50h", "0,10h", "sem ajudante", "reduzir hora"]):
        return "CPU_HORAS"
    if any(k in t_full for k in ["duplicidade", "já contemplam", "já está incluso", "duplicado", "em duplicidade"]):
        return "DUPLICIDADE"
    if any(k in t_full for k in ["cotação", "cotações", "fornecedores", "mapa de cotação", "mapa de cotações", "três orçamentos", "3 orçamentos", "fora do sinapi", "não tabelado"]):
        if any(k in t_full for k in ["mediana", "menor preço", "critério de mediana", "média"]):
            return "MEDIANA"
        return "MC_FALTA"
    if any(k in t_full for k in ["bdi", "acórdão 2622", "bdi diferenciado", "equipamentos"]):
        return "BDI"
    if any(k in t_full for k in ["cronograma", "fechamento 100%", "físico-financeiro", "desembolso"]):
        return "CRONOGRAMA"
    if any(k in t_full for k in ["canteiro", "tapume", "alvará", "ligação provisória", "container", "placa de obra"]):
        return "CANTEIRO_CLIENTE"
    if any(k in t_full for k in ["art de orçamento", "art do orçamentista", "anotação de responsabilidade técnica", "rrt"]):
        return "ART"
    if any(k in t_full for k in ["verga", "contraverga", "trama", "subleito", "tutor", "adubação", "chapisco", "além do desenho"]):
        return "OBRA_ALEM_DESENHO"
    if any(k in t_full for k in ["qual a dimensão", "verificar a correta", "conflito entre pranchas", "projetista", "memorial descritivo diverge"]):
        return "PROJETISTA"
    if any(k in t_full for k in ["insumo principal", "substituir insumo", "especificação", "modelo", "fabricante", "hi-wall", "cassete", "maxx", "joelho", "curva"]):
        return "ESPEC_DIVERGENTE"
    if any(k in t_full for k in ["composição sem mão de obra", "sem insumo", "tinta pva acrílico", "é um material"]):
        return "CPU_INSUMO"
        
    return "ESPEC_DIVERGENTE"

def infer_acao_auditor(item_code, ressalva, resposta, tema):
    # Formulate direct action line in standard format: "Item X.X.X — [ação]"
    prefix = f"Item {item_code} — " if item_code and item_code != "GERAL" else ""
    
    if tema == "LI_AUSENTE":
        return f"{prefix}Incluir na planilha orçamentária o escopo e quantitativos da Lista de Materiais da disciplina ausente."
    elif tema == "QTD_DIVERGENTE":
        return f"{prefix}Compatibilizar rigorosamente a quantidade da planilha com o valor exato da Lista de Materiais do projeto."
    elif tema == "UNIDADE":
        return f"{prefix}Corrigir a unidade de medição do item/composição para compatibilizar com a remuneração oficial (ex.: de M/QTD para UN/M²)."
    elif tema == "CPU_HORAS":
        return f"{prefix}Ajustar os coeficientes de mão de obra da CPU conforme os parâmetros aprovados pela SUPAT (redução de horas/auxiliar)."
    elif tema == "CPU_INSUMO":
        return f"{prefix}Adequar os insumos e a estrutura da composição analítica ao serviço efetivamente executado."
    elif tema == "DUPLICIDADE":
        return f"{prefix}Eliminar duplicidade de escopo (deduzir item que já se encontra contemplado no fornecimento principal ou pacote)."
    elif tema == "MC_FALTA":
        return f"{prefix}Apresentar Mapa de Cotações com no mínimo 3 fornecedores válidos (CNPJ ativo, data e contato) para o item não tabelado."
    elif tema == "MEDIANA":
        return f"{prefix}Aplicar a MEDIANA das 3 cotações coletadas no Mapa de Cotações (DC-007), conforme padrão SUPAT."
    elif tema == "BDI":
        return f"{prefix}Ajustar a taxa de BDI aos parâmetros do Acórdão 2622/2013-TCU (diferenciando obra civil de material/equipamento relevante)."
    elif tema == "CRONOGRAMA":
        return f"{prefix}Garantir que o valor total do Cronograma coincida centavo a centavo com o Orçamento (diferença R$ 0,00) e feche 100%."
    elif tema == "CANTEIRO_CLIENTE":
        return f"{prefix}Sinalizar pendência de definição do cliente/contratante (canteiro/alvará/tapume)."
    elif tema == "ART":
        return f"{prefix}Anexar a ART/RRT de elaboração do orçamento/levantamento devidamente quitada."
    elif tema == "OBRA_ALEM_DESENHO":
        return f"{prefix}Incluir na planilha os serviços complementares obrigatórios exigidos pelo método executivo (vergas, subleito, trama, etc.)."
    elif tema == "PROJETISTA":
        return f"{prefix}Submeter questionamento formal ao projetista para esclarecimento/compatibilização de pranchas e memorial."
    else:
        return f"{prefix}Compatibilizar a especificação técnica do insumo/serviço com o projeto e memorial descritivo."

def parse_docx_triples(file_path, meta):
    triples = []
    doc = docx.Document(file_path)
    
    # 1. Parse tables for checklist status (ITEM 01 to 10)
    current_item = "ITEM 02"
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(c.text.strip().replace("\n", " ") for c in row.cells)
            for item_key in CHECKLIST_ITEMS:
                if item_key in row_text:
                    # Found an item checklist row
                    cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                    status = "OK" if "OK" in row_text else ("COM RESSALVAS" if "RESSALVA" in row_text else "ANALISADO")
                    # Check if there is specific text in the last cell
                    obs = cells[-1] if len(cells) > 2 else ""
                    if obs and obs != "--------------------" and len(obs) > 5:
                        tema = classify_tema(obs)
                        acao = infer_acao_auditor("CHECKLIST", obs, "", tema)
                        triples.append({
                            "orgao": meta["orgao"],
                            "obra": meta["obra_pasta"],
                            "pcode": meta["pcode"],
                            "revisao_analise": meta["rev"],
                            "arquivo_origem": meta["filename"],
                            "caminho_relativo": meta["path"],
                            "item_checklist": item_key,
                            "tema": tema,
                            "texto_ressalva": obs,
                            "resposta_fpe": "Verificado no checklist do formulário oficial",
                            "correcao_feita": "Atendido/conferido",
                            "status_ciclo": "atendido_na_R_seguinte",
                            "acao_auditor": acao
                        })

    # 2. Parse paragraphs for detailed ressalvas and responses
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    current_item_header = "ITEM 02"
    i = 0
    while i < len(paragraphs):
        p_text = paragraphs[i]
        
        # Detect item header change (e.g. "ITEM 01.", "ITEM 02.", "ITEM 03.", etc.)
        item_match = re.search(r"^(ITEM\s*\d{2})", p_text, re.IGNORECASE)
        if item_match:
            current_item_header = item_match.group(1).upper()
            i += 1
            continue
            
        # Detect if this paragraph is a ressalva
        # Common pattern: Paragraph contains observation, next paragraph contains RESPOSTA
        is_ressalva = False
        res_idx = -1
        
        # Look ahead for RESPOSTA
        for j in range(i + 1, min(i + 5, len(paragraphs))):
            p_next = paragraphs[j]
            if re.search(r"^(RESPOSTA|RESPOSTAS|R\s*-|ITEM\s*ATENDIDO|ITEM\s*CORRIGIDO)", p_next, re.IGNORECASE):
                is_ressalva = True
                res_idx = j
                break
                
        # Also check if the paragraph itself contains "ESTA SENDO ESTIMADO" or "ITEM - X.X.X" (PGE Sonorização pattern)
        if not is_ressalva and ("ESTA SENDO" in p_text.upper() or "ITEM -" in p_text):
            # PGE pattern
            if i + 1 < len(paragraphs) and ("ESTA SENDO" in paragraphs[i+1].upper() or "UTILIZADO" in paragraphs[i+1].upper() or "PARA" in paragraphs[i+1].upper()):
                is_ressalva = True
                res_idx = i + 1

        if is_ressalva and res_idx > i:
            ressalva_chunk = "\n".join(paragraphs[i:res_idx])
            resposta_chunk = paragraphs[res_idx]
            # If next paragraphs are also part of response
            k = res_idx + 1
            while k < len(paragraphs) and not re.search(r"^(ITEM\s*\d{2}|No\s*item|No\s*Item|Solicito|Referente|O\s*insumo|Observamos|ITEM\s*-)", paragraphs[k], re.IGNORECASE) and not any(paragraphs[k].startswith(x) for x in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]):
                if re.search(r"^(RESPOSTA|R\s*-)", paragraphs[k], re.IGNORECASE):
                    resposta_chunk += "\n" + paragraphs[k]
                    k += 1
                else:
                    break
                    
            # Extract item code if present
            code_match = re.search(r"(?:Item|ITEM)\s*[-:]?\s*(\d+(?:\.\d+)+|\w+\.\d+|\w+)", ressalva_chunk)
            item_code = code_match.group(1) if code_match else current_item_header
            
            tema = classify_tema(ressalva_chunk, resposta_chunk)
            acao = infer_acao_auditor(item_code, ressalva_chunk, resposta_chunk, tema)
            
            # Determine status_ciclo
            status_ciclo = "atendido_na_R_seguinte"
            if "pendente" in resposta_chunk.lower() or "aguardando" in resposta_chunk.lower():
                status_ciclo = "pendente_cliente"
            elif "projetista" in resposta_chunk.lower() or tema == "PROJETISTA":
                status_ciclo = "pendente_projetista"
                
            triples.append({
                "orgao": meta["orgao"],
                "obra": meta["obra_pasta"],
                "pcode": meta["pcode"],
                "revisao_analise": meta["rev"],
                "arquivo_origem": meta["filename"],
                "caminho_relativo": meta["path"],
                "item_checklist": current_item_header,
                "tema": tema,
                "texto_ressalva": ressalva_chunk.strip(),
                "resposta_fpe": resposta_chunk.strip(),
                "correcao_feita": resposta_chunk.strip(),
                "status_ciclo": status_ciclo,
                "acao_auditor": acao
            })
            i = k
        else:
            i += 1
            
    return triples

def parse_pdf_triples(file_path, meta):
    triples = []
    try:
        reader = pypdf.PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text += "\n" + t
                
        # Look for numbered observations (e.g. "1. ...", "2. ...", "7. O item ...")
        # Split by numbered items
        pattern = re.compile(r"(?:\n|^)(\d{1,2}\.\s+[^\n]+(?:\n(?!\d{1,2}\.\s+)[^\n]+)*)", re.MULTILINE)
        matches = pattern.findall(full_text)
        
        for m in matches:
            m_str = m.strip()
            if len(m_str) < 25 or "Superintendência de Patrimônio" in m_str or "Secretaria da Administração" in m_str:
                continue
                
            # Extract item code
            code_m = re.search(r"(?:item|Item|ITEM)\s*(\d+(?:\.\d+)+)", m_str)
            item_code = code_m.group(1) if code_m else "GERAL"
            
            tema = classify_tema(m_str)
            acao = infer_acao_auditor(item_code, m_str, "", tema)
            
            triples.append({
                "orgao": meta["orgao"] if meta["orgao"] != "N/A" else "SEC",
                "obra": meta["obra_pasta"],
                "pcode": meta["pcode"],
                "revisao_analise": meta["rev"],
                "arquivo_origem": meta["filename"],
                "caminho_relativo": meta["path"],
                "item_checklist": "ITEM 02" if tema in ["LI_AUSENTE", "QTD_DIVERGENTE", "UNIDADE", "ESPEC_DIVERGENTE"] else "ITEM 03",
                "tema": tema,
                "texto_ressalva": m_str,
                "resposta_fpe": "Parecer/Análise oficial SUPAT extraída do processo licitatório",
                "correcao_feita": "Exigência direta do analista SUPAT",
                "status_ciclo": "atendido_na_R_seguinte",
                "acao_auditor": acao
            })
    except Exception as e:
        print(f"Error reading PDF {file_path.name}: {e}")
        
    return triples

def process_all_corpus():
    inv_file = BASE_DIR / "04-DADOS" / "inventario_corpus.json"
    if not inv_file.exists():
        print("Inventory JSON not found. Run inventariar_corpus.py first.")
        return []
        
    with open(inv_file, "r", encoding="utf-8") as f:
        corpus = json.load(f)
        
    all_triples = []
    print(f"Extracting triples from {len(corpus)} corpus documents...")
    
    # Priority projects and files
    for entry in corpus:
        full_path = ROOT_DIR / entry["path"]
        if not full_path.exists():
            continue
            
        ext = full_path.suffix.lower()
        if ext == ".docx":
            trips = parse_docx_triples(full_path, entry)
            all_triples.extend(trips)
            if trips:
                print(f"  [{entry['pcode']} | {entry['rev']}] {entry['filename']}: {len(trips)} triplas.")
        elif ext == ".pdf" and entry["tipo"] == "analise":
            trips = parse_pdf_triples(full_path, entry)
            all_triples.extend(trips)
            if trips:
                print(f"  [{entry['pcode']} | {entry['rev']}] {entry['filename']}: {len(trips)} triplas.")

    # Deduplicate triples by (pcode, texto_ressalva snippet)
    unique_triples = []
    seen = set()
    for t in all_triples:
        snippet = re.sub(r"\s+", " ", t["texto_ressalva"][:80].lower().strip())
        key = (t["pcode"], t["revisao_analise"], snippet)
        if key not in seen and len(snippet) > 10:
            seen.add(key)
            unique_triples.append(t)
            
    print(f"\nConsolidated {len(unique_triples)} unique structured precedent triples (from {len(all_triples)} raw extractions).")
    
    # Save to JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(unique_triples, f, indent=2, ensure_ascii=False)
    print(f"Saved -> {OUTPUT_JSON}")
    
    return unique_triples

def generate_precedents_markdown(triples):
    PRECEDENTES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Group by tema
    by_tema = {}
    for t in triples:
        by_tema.setdefault(t["tema"], []).append(t)
        
    theme_titles = {
        "LI_AUSENTE": "01_LISTAS_DE_INSUMOS_E_DISCIPLINAS_AUSENTES",
        "QTD_DIVERGENTE": "02_DIVERGENCIAS_DE_QUANTITATIVOS_PLANILHA_VS_LI",
        "UNIDADE": "03_INCOMPATIBILIDADES_DE_UNIDADES_DE_MEDICAO",
        "ESPEC_DIVERGENTE": "04_ESPECIFICACOES_E_INSUMOS_DIVERGENTES",
        "CPU_HORAS": "05_COEFICIENTES_DE_MAO_DE_OBRA_E_HORAS_SUPAT",
        "CPU_INSUMO": "06_ESTRUTURA_E_INSUMOS_DE_COMPOSICOES_PROPRIAS",
        "DUPLICIDADE": "07_DUPLICIDADE_DE_CUSTOS_E_ESCOPOS",
        "MC_FALTA": "08_MAPA_DE_COTACOES_E_ITENS_NAO_TABELADOS",
        "MEDIANA": "09_CRITERIO_DE_MEDIANA_E_VALIDADE_DE_COTACOES",
        "BDI": "10_BDI_OBRAS_CIVIS_E_BDI_DIFERENCIADO",
        "CRONOGRAMA": "11_CRONOGRAMA_FISICO_FINANCEIRO_E_FECHAMENTO",
        "CANTEIRO_CLIENTE": "12_CANTEIRO_TAPUME_ALVARA_E_CONTRATANTE",
        "ART": "13_ART_DE_ORCAMENTO_E_RESPONSABILIDADE_TECNICA",
        "OBRA_ALEM_DESENHO": "14_OBRA_ALEM_DO_DESENHO_E_SERVICOS_IMPLICITOS",
        "PROJETISTA": "15_INCOMPATIBILIDADES_DE_PROJETO_E_RESPOSTA_AO_PROJETISTA"
    }
    
    map_lines = [
        "# MAPA GERAL DE RESSALVAS E PRECEDENTES SUPAT / SAEB\n",
        "Base de conhecimento consolidada a partir da mineração do corpus real de análises críticas oficiais da **SUPAT / SAEB / PGE / SEC / SETRE / ADAB / FUNDAC / SECOM** e relatórios técnicos da FPE.\n",
        "### Como Consultar:\n",
        "1. Identifique o tema da ressalva / verificação na tabela abaixo.\n",
        "2. Abra o arquivo de precedentes correspondente em `03-PRECEDENTES/`.\n",
        "3. Para consulta rápida via linha de comando:\n",
        "   ```bash\n   python 00-BASE_CONHECIMENTO_SUPAT/05-SCRIPTS/consultar_precedente.py <TEMA>\n   ```\n",
        "| Tema | Descrição / Foco do Analista | Arquivo de Precedentes | Qtd Casos |",
        "|---|---|---|---|"
    ]
    
    for tema, fname_base in theme_titles.items():
        items = by_tema.get(tema, [])
        fname = f"{fname_base}.md"
        fpath = PRECEDENTES_DIR / fname
        
        map_lines.append(f"| **`{tema}`** | {fname_base.replace('_', ' ')[3:]} | [`{fname}`](03-PRECEDENTES/{fname}) | **{len(items)}** |")
        
        # Write individual theme Markdown
        t_lines = [
            f"# Precedentes SUPAT: {tema}\n",
            f"**Total de Casos Minerados:** {len(items)}  \n",
            "---\n",
            "## 1. Diretriz e Padrão de Análise do Órgão\n",
        ]
        
        if tema == "LI_AUSENTE":
            t_lines.append("A SUPAT confere a lista de disciplinas entregues contra as pranchas e a planilha orçamentária. Se houver prancha ou memorial de uma disciplina (ex.: drenagem, CFTV, comunicação visual) sem a respectiva Lista de Materiais ou sem inserção na planilha, o orçamento é sumariamente travado no ITEM 02.\n")
        elif tema == "QTD_DIVERGENTE":
            t_lines.append("O analista compara linha por linha o quantitativo da Planilha Sintética com a Lista de Materiais da disciplina. Diferenças decimais ou de arredondamento são apontadas com ressalva expressa para compatibilização no valor exato.\n")
        elif tema == "UNIDADE":
            t_lines.append("Erros de unidade (ex.: cotar conector em metro linear em vez de peça/unidade, ou usar 'QTD' genérico) são rejeitados. A unidade da planilha deve coincidir estritamente com a unidade oficial da composição SINAPI/ORSE.\n")
        elif tema == "CPU_HORAS":
            t_lines.append("Horas de mão de obra em composições próprias de áudio, cabeamento, CFTV e elétrica são calibradas rigorosamente (máximo de 1,50h para equipamentos maiores e 0,10h a 0,30h para módulos/conectores; ajudantes especializados cortados quando desnecessários).\n")
        elif tema == "MEDIANA":
            t_lines.append("Para itens não tabelados no SINAPI/ORSE, a SUPAT exige pesquisa com 3 fornecedores válidos e adoção mandatória da **MEDIANA** das cotações (salvo justificativa técnica expressa).\n")
        elif tema == "DUPLICIDADE":
            t_lines.append("Serviços embutidos no fornecimento principal (ex.: kit de instalação de ar condicionado até 3m, calhas embutidas em estruturas metálicas) não podem ser lançados em duplicidade como itens avulsos.\n")
        elif tema == "OBRA_ALEM_DESENHO":
            t_lines.append("Serviços acessórios obrigatórios pelo caderno técnico que não constam no desenho (vergas, contravergas, subleito de piso intertravado, adubação de plantio) devem ser quantificados e orçados.\n")
        else:
            t_lines.append("Critérios técnicos e jurisprudência aplicados pela SUPAT na aprovação de orçamentos e memórias de cálculo.\n")
            
        t_lines.append("## 2. Casos Reais Minerados do Corpus\n")
        
        for idx, it in enumerate(items, 1):
            t_lines.append(f"### Caso {idx}: [{it['orgao']} - {it['pcode']}] {it['obra']} (Rev: {it['revisao_analise']})")
            t_lines.append(f"- **Item do Checklist:** `{it['item_checklist']}`")
            t_lines.append(f"- **Arquivo Origem:** `{it['arquivo_origem']}`")
            t_lines.append(f"- **Texto da Ressalva do Analista:**\n  > *\"{it['texto_ressalva']}\"*")
            t_lines.append(f"- **Resposta da FPE:**\n  > {it['resposta_fpe']}")
            t_lines.append(f"- **Ação Obrigatória do Auditor:** `{it['acao_auditor']}`")
            t_lines.append(f"- **Status do Ciclo:** `{it['status_ciclo']}`\n")
            
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n".join(t_lines))
            
    with open(MAPA_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(map_lines))
        
    print(f"Generated {len(theme_titles)} thematic precedent MD files in {PRECEDENTES_DIR}")
    print(f"Generated Map -> {MAPA_MD}")

def main():
    triples = process_all_corpus()
    generate_precedents_markdown(triples)

if __name__ == "__main__":
    main()
