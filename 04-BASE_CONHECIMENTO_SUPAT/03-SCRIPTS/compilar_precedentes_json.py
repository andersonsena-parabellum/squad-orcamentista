import os
import re
import json
from pathlib import Path

base_dir = Path(r"g:\Meu Drive\DFE PROJETOS OFICIAL\CLIENTES\16. FABIO - FPE\squad-orcamentista\04-BASE_CONHECIMENTO_SUPAT")
prec_dir = base_dir / "02-PRECEDENTES"
out_dir = base_dir / "04-DADOS"
out_file = out_dir / "precedentes.json"

precedents = []
if prec_dir.exists():
    for f in sorted(prec_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        m_tema = re.search(r"#\s*Precedentes\s+SUPAT:\s*(\w+)", content)
        tema = m_tema.group(1) if m_tema else f.stem
        
        cases = re.split(r"###\s+Caso\s+\d+:\s*", content)[1:]
        for c in cases:
            header_m = re.search(r"\[(.*?) - (.*?)\]\s*(.*?)\s*\(Rev:\s*(.*?)\)", c)
            orgao = header_m.group(1).strip() if header_m else ""
            pcode = header_m.group(2).strip() if header_m else ""
            obra = header_m.group(3).strip() if header_m else ""
            revisao = header_m.group(4).strip() if header_m else ""
            
            item_m = re.search(r"-\s*\*\*Item do Checklist:\*\*\s*`?(.*?)`?\n", c)
            item_chk = item_m.group(1).strip("` ") if item_m else ""
            
            arq_m = re.search(r"-\s*\*\*Arquivo Origem:\*\*\s*`?(.*?)`?\n", c)
            arq = arq_m.group(1).strip("` ") if arq_m else ""
            
            res_m = re.search(r'-\s*\*\*Texto da Ressalva do Analista:\*\*\s*\n\s*>\s*\*\"(.*?)\"\*', c, re.DOTALL)
            ressalva = res_m.group(1).strip() if res_m else ""
            if not ressalva:
                res_m2 = re.search(r"-\s*\*\*Texto da Ressalva do Analista:\*\*\s*\n\s*>\s*(.*?)(?=\n-|\Z)", c, re.DOTALL)
                ressalva = res_m2.group(1).strip() if res_m2 else ""
                
            resp_m = re.search(r"-\s*\*\*Resposta da FPE:\*\*\s*\n\s*>\s*(.*?)(?=\n-|\Z)", c, re.DOTALL)
            resposta = resp_m.group(1).strip() if resp_m else ""
            
            acao_m = re.search(r"-\s*\*\*Ação Obrigatória do Auditor:\*\*\s*`?(.*?)`?\n", c)
            acao = acao_m.group(1).strip("` ") if acao_m else ""
            
            status_m = re.search(r"-\s*\*\*Status do Ciclo:\*\*\s*`?(.*?)`?(?:\n|\Z)", c)
            status = status_m.group(1).strip("` ") if status_m else ""
            
            precedents.append({
                "tema": tema,
                "orgao": orgao,
                "pcode": pcode,
                "obra": obra,
                "revisao_analise": revisao,
                "item_checklist": item_chk,
                "arquivo_origem": arq,
                "texto_ressalva": ressalva,
                "resposta_fpe": resposta,
                "acao_auditor": acao,
                "status_ciclo": status
            })

out_dir.mkdir(parents=True, exist_ok=True)
with open(out_file, "w", encoding="utf-8") as fp:
    json.dump(precedents, fp, indent=2, ensure_ascii=False)

print(f"Sucesso: {len(precedents)} precedentes exportados para {out_file}")
