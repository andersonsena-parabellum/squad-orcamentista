import os
import re
import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(r"g:\Meu Drive\DFE PROJETOS OFICIAL\CLIENTES\16. FABIO - FPE")
OUTPUT_MD = ROOT_DIR / "00-BASE_CONHECIMENTO_SUPAT" / "01-INVENTARIO_CORPUS.md"
OUTPUT_JSON = ROOT_DIR / "00-BASE_CONHECIMENTO_SUPAT" / "04-DADOS" / "inventario_corpus.json"

# Regex patterns for matching
RE_PCODE = re.compile(r"(P\d{4,5})", re.IGNORECASE)
RE_REV = re.compile(r"[-_\s]R(\d{2})", re.IGNORECASE)
RE_ORGAO = re.compile(r"(SEPROMI|SETRE|CFA|FUNDAC|PGE|ADAB|SECOM|SEC|PMFRP|SAC|SDE|MAB|IPAC|SECULT|AGERBA|FUNCEB|SETUR|SUPREV|UEFS|EMAC|CMDV)", re.IGNORECASE)

ANALYSIS_KEYWORDS = [
    "analise", "análise", "parecer", "supat", "ressalva", "critica", "crítica", 
    "analises orcamentacao", "analise orcamento", "analise quantitativo", "relatorio de analise"
]

RESPONSE_FPE_KEYWORDS = [
    "resposta", "respostas", "rt-001", "rt_001", "rt001", "relatorio resposta", 
    "relatório resposta", "resposta analise", "resposta análise", "respostas analise",
    "respostas análise", "resposta de questionamentos", "resposta questionamentos"
]

DESIGNER_KEYWORDS = [
    "projetista", "incompatib", "questionamento", "duvida projeto", "dúvida projeto"
]

def classify_file(filename: str, path_str: str):
    f_lower = filename.lower()
    p_lower = path_str.lower()
    
    # Exclude temporary, backup, or non-document files
    if f_lower.startswith("~$") or f_lower.endswith(".tmp") or f_lower.endswith(".bak"):
        return None
    if not any(f_lower.endswith(ext) for ext in [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt"]):
        return None
        
    # Check for designer response/questionnaire
    for kw in DESIGNER_KEYWORDS:
        if kw in f_lower or kw in p_lower:
            return "resposta_projetista"
            
    # Check for FPE response
    for kw in RESPONSE_FPE_KEYWORDS:
        if kw in f_lower:
            return "resposta_fpe"
            
    # Check for official analysis
    for kw in ANALYSIS_KEYWORDS:
        if kw in f_lower or "analises orcamentacao" in p_lower:
            # If it says 'resposta' in filename, it's FPE response, not analysis
            if "resposta" in f_lower or "rt-001" in f_lower or "rt_001" in f_lower:
                return "resposta_fpe"
            return "analise"
            
    return None

def scan_corpus():
    entries = []
    project_folders = [d for d in ROOT_DIR.iterdir() if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("00-")]
    
    print(f"Scanning {len(project_folders)} project directories in {ROOT_DIR.name}...")
    
    for folder in sorted(project_folders, key=lambda x: x.name):
        folder_name = folder.name
        folder_entries = []
        
        try:
            # Walk directory
            for root, dirs, files in os.walk(folder):
                # skip git or cache dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
                for f in files:
                    file_path = Path(root) / f
                    classification = classify_file(f, str(file_path))
                    if classification:
                        rel_path = file_path.relative_to(ROOT_DIR)
                        
                        # Extract P-code
                        pcode_m = RE_PCODE.search(f) or RE_PCODE.search(folder_name)
                        pcode = pcode_m.group(1).upper() if pcode_m else "N/A"
                        
                        # Extract Revision
                        rev_m = RE_REV.search(f) or RE_REV.search(str(file_path))
                        rev = f"R{rev_m.group(1)}" if rev_m else "R00"
                        
                        # Extract Organ
                        orgao_m = RE_ORGAO.search(f) or RE_ORGAO.search(folder_name)
                        orgao = orgao_m.group(1).upper() if orgao_m else "N/A"
                        
                        # File stats
                        try:
                            stat = file_path.stat()
                            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                            size_kb = round(stat.st_size / 1024, 1)
                        except Exception:
                            mtime = "N/A"
                            size_kb = 0
                            
                        # Build entry
                        entry = {
                            "obra_pasta": folder_name,
                            "pcode": pcode,
                            "orgao": orgao,
                            "tipo": classification,
                            "rev": rev,
                            "filename": f,
                            "path": str(rel_path).replace("\\", "/"),
                            "size_kb": size_kb,
                            "mtime": mtime,
                        }
                        folder_entries.append(entry)
        except Exception as e:
            print(f"Error scanning {folder_name}: {e}")
            
        print(f"[{folder_name}] Found {len(folder_entries)} corpus items.")
        entries.extend(folder_entries)
        
    # Deduplicate and create pairs
    # A pair connects an analysis with an FPE response or designer response
    pairs = {}
    for item in entries:
        # Key by (pcode, orgao, rev) or (obra_pasta, rev)
        pair_key = f"{item['pcode']}_{item['orgao']}_{item['rev']}" if item['pcode'] != "N/A" else f"{item['obra_pasta']}_{item['rev']}"
        item['par_id'] = pair_key
        
    return entries

def generate_inventory_md(entries):
    lines = []
    lines.append("# 01 - INVENTÁRIO DO CORPUS SUPAT / FPE\n")
    lines.append(f"**Data de Geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Total de Documentos Minerados:** {len(entries)}  \n")
    lines.append("---\n")
    
    # Group by Obra / Pasta
    grouped = {}
    for e in entries:
        folder = e["obra_pasta"]
        grouped.setdefault(folder, []).append(e)
        
    lines.append("## Resumo por Pasta de Obra\n")
    lines.append("| Pasta da Obra | Código | Órgão | Análises Oficiais | Respostas FPE | Respostas Projetista | Total |")
    lines.append("|---|---|---|---|---|---|---|")
    
    for folder, items in sorted(grouped.items()):
        pcode = items[0]["pcode"]
        orgao = items[0]["orgao"]
        n_analise = sum(1 for x in items if x["tipo"] == "analise")
        n_fpe = sum(1 for x in items if x["tipo"] == "resposta_fpe")
        n_proj = sum(1 for x in items if x["tipo"] == "resposta_projetista")
        lines.append(f"| `{folder}` | **{pcode}** | **{orgao}** | {n_analise} | {n_fpe} | {n_proj} | **{len(items)}** |")
        
    lines.append("\n---\n")
    lines.append("## Detalhamento Completo do Corpus\n")
    lines.append("| ID Par | Tipo | Rev | Órgão / Obra | Arquivo | Data Modif. | Tamanho | Caminho Relativo |")
    lines.append("|---|---|---|---|---|---|---|---|")
    
    for e in sorted(entries, key=lambda x: (x["obra_pasta"], x["rev"], x["tipo"])):
        tipo_badge = {
            "analise": "🔴 **ANÁLISE OFICIAL**",
            "resposta_fpe": "🟢 **RESPOSTA FPE**",
            "resposta_projetista": "🔵 **PROJETISTA**"
        }.get(e["tipo"], e["tipo"])
        
        lines.append(f"| `{e['par_id']}` | {tipo_badge} | `{e['rev']}` | {e['orgao']} (`{e['pcode']}`) | `{e['filename']}` | {e['mtime']} | {e['size_kb']} KB | `{e['path']}` |")
        
    return "\n".join(lines)

def main():
    entries = scan_corpus()
    
    # Save JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print(f"Saved corpus JSON -> {OUTPUT_JSON} ({len(entries)} items)")
    
    # Save Markdown
    md_content = generate_inventory_md(entries)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved corpus Markdown -> {OUTPUT_MD}")

if __name__ == "__main__":
    main()
