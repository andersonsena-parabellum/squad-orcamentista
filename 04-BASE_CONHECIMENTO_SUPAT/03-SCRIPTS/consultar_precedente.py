import sys
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "04-DADOS" / "precedentes.json"
MAP_FILE = BASE_DIR / "MAPA_RESSALVAS.md"

def load_precedents():
    if not DATA_FILE.exists():
        print(f"Erro: Arquivo de precedentes não encontrado em {DATA_FILE}")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def print_help(precedents):
    print("=" * 80)
    print(" CONSULTA TOKEN-EFICIENTE DE PRECEDENTES E RESSALVAS SUPAT / SAEB")
    print("=" * 80)
    print(f"Base carregada: {len(precedents)} precedentes minerados.\n")
    print("Uso:")
    print("  python consultar_precedente.py <TEMA | PALAVRA-CHAVE> [--limit N]\n")
    
    # Count by theme
    by_tema = {}
    for p in precedents:
        t = p.get("tema", "OUTROS")
        by_tema[t] = by_tema.get(t, 0) + 1
        
    print("Temas Disponíveis:")
    for tema, count in sorted(by_tema.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {tema:<20} ({count:>3} casos)")
        
    print("\nExemplos:")
    print("  python consultar_precedente.py LI_AUSENTE")
    print("  python consultar_precedente.py CPU_HORAS")
    print("  python consultar_precedente.py 'ar-condicionado'")
    print("  python consultar_precedente.py 'rack' --limit 3")
    print("=" * 80)

def search_precedents(query, limit=10):
    precedents = load_precedents()
    q_lower = query.lower().strip()
    
    # Check if query matches a theme exactly or as substring
    matches = []
    for p in precedents:
        tema = p.get("tema", "").lower()
        ressalva = p.get("texto_ressalva", "").lower()
        resposta = p.get("resposta_fpe", "").lower()
        orgao = p.get("orgao", "").lower()
        pcode = p.get("pcode", "").lower()
        
        # Match by theme
        if q_lower == tema:
            matches.append((p, 100)) # Exact theme match
        elif q_lower in tema:
            matches.append((p, 80))
        elif q_lower in ressalva or q_lower in resposta:
            matches.append((p, 50))
        elif q_lower in orgao or q_lower in pcode:
            matches.append((p, 30))
            
    # Sort matches by score
    matches.sort(key=lambda x: x[1], reverse=True)
    results = [m[0] for m in matches[:limit]]
    
    print("=" * 80)
    print(f" RESULTADO DA CONSULTA SUPAT: '{query}' ({len(matches)} encontrados, exibindo {len(results)})")
    print("=" * 80)
    
    if not results:
        print(f"Nenhum precedente encontrado para o termo '{query}'.")
        print("Tente buscar por um tema ou palavra-chave mais genérica.")
        return
        
    for i, p in enumerate(results, 1):
        print(f"\n--- [CASO {i:02d}] {p.get('orgao', 'ÓRGÃO')} ({p.get('pcode', 'N/A')}) | Rev: {p.get('revisao_analise', 'R00')} | Tema: {p.get('tema', 'GERAL')} ---")
        print(f"• Item Checklist: {p.get('item_checklist', 'ITEM 02')}")
        print(f"• Arquivo:        {p.get('arquivo_origem', 'N/A')}")
        print(f"• Ressalva SUPAT: \"{p.get('texto_ressalva', '').strip()}\"")
        print(f"• Resposta FPE:   {p.get('resposta_fpe', '').strip()}")
        print(f"• Ação Auditor:   {p.get('acao_auditor', '').strip()}")
        print(f"• Status Ciclo:   {p.get('status_ciclo', 'atendido_na_R_seguinte')}")
        
    print("\n" + "=" * 80)

def main():
    if len(sys.argv) < 2:
        precedents = load_precedents()
        print_help(precedents)
        return
        
    limit = 10
    args = sys.argv[1:]
    if "--limit" in args:
        idx = args.index("--limit")
        if idx + 1 < len(args):
            try:
                limit = int(args[idx + 1])
            except ValueError:
                pass
            args = args[:idx] + args[idx+2:]
            
    query = " ".join(args)
    search_precedents(query, limit=limit)

if __name__ == "__main__":
    main()
