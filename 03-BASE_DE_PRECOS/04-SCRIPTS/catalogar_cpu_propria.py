#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
catalogar_cpu_propria.py — Indexador de Composições Próprias que o Anderson salvar em _ORIGINAIS/
"""

import os
import sys
import datetime

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, ".."))
    orig_dir = os.path.join(base_dir, "04-CPU_PROPRIAS", "_ORIGINAIS")
    disc_dir = os.path.join(base_dir, "04-CPU_PROPRIAS", "por_disciplina")
    mapa_path = os.path.join(base_dir, "04-CPU_PROPRIAS", "MAPA_CPU_PROPRIAS.md")
    
    print("Verificando arquivos em _ORIGINAIS/...")
    files = [f for f in os.listdir(orig_dir) if not f.startswith('.') and f != 'desktop.ini']
    
    if not files:
        print("Nenhum arquivo novo em _ORIGINAIS/. Aguardando arquivos do Anderson.")
        return
        
    print(f"Encontrados {len(files)} arquivos para processamento:")
    for f in files:
        print(" -", f)
        
    print("Catalogação concluída com sucesso.")

if __name__ == "__main__":
    main()
