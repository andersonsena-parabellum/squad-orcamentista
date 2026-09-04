#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
consultar_composicao.py — Consulta rápida de composições e insumos SINAPI e ORSE
Uso:
  python consultar_composicao.py <codigo_ou_termo>
Exemplos:
  python consultar_composicao.py 93680
  python consultar_composicao.py 94195
  python consultar_composicao.py 98511
  python consultar_composicao.py 104658
  python consultar_composicao.py 88256
  python consultar_composicao.py "intertravado"
"""

import sqlite3
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Uso: python consultar_composicao.py <codigo_ou_termo>")
        sys.exit(1)
        
    query = sys.argv[1].strip()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "base_precos.db")
    if not os.path.exists(db_path):
        db_path = os.path.join(r"g:\Meu Drive\DFE PROJETOS OFICIAL\CLIENTES\16. FABIO - FPE\00-BASE_DE_PRECOS_SINAPI_ORSE", "base_precos.db")
        
    if not os.path.exists(db_path):
        print(f"Erro: Banco de dados não encontrado em {db_path}")
        sys.exit(1)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Tentar busca exata por código de composição
    cur.execute("SELECT fonte, codigo, descricao, unidade, grupo, custo_deson, custo_nao_deson FROM composicoes WHERE codigo = ?", (query,))
    comp_row = cur.fetchone()
    
    # 2. Se não achou como composição, tentar como insumo exato
    if not comp_row:
        cur.execute("SELECT fonte, codigo, descricao, unidade, tipo, preco_deson, preco_nao_deson FROM insumos WHERE codigo = ?", (query,))
        ins_row = cur.fetchone()
        if ins_row:
            fonte, cod, desc, unid, tipo, p_d, p_nd = ins_row
            print("\n" + "="*80)
            print(f"[{fonte}] INSUMO: {cod} — {desc}")
            print("="*80)
            print(f"Unidade: {unid} | Tipo: {tipo}")
            print(f"Preço Desonerado (BA):     R$ {p_d:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            print(f"Preço Não Desonerado (BA): R$ {p_nd:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            print("="*80 + "\n")
            conn.close()
            return
            
    # 3. Se não achou código exato, buscar composições por texto
    if not comp_row:
        cur.execute("""
            SELECT fonte, codigo, descricao, unidade, grupo, custo_deson, custo_nao_deson 
            FROM composicoes 
            WHERE descricao LIKE ? OR codigo LIKE ?
            LIMIT 10
        """, (f"%{query}%", f"%{query}%"))
        results = cur.fetchall()
        if results:
            print("\n" + "="*80)
            print(f"RESULTADOS DA BUSCA POR TERMO: '{query}' ({len(results)} encontrados)")
            print("="*80)
            for r in results:
                f, c, d, u, g, cd, cnd = r
                print(f"[{f}] `{c}` — {d[:85]}... ({u}) | Deson: R$ {cd:.2f} | Não Deson: R$ {cnd:.2f}")
            print("="*80)
            print("Para ver o analítico completo, consulte com o código exato (ex.: python consultar_composicao.py <codigo>)")
            print("="*80 + "\n")
            conn.close()
            return
        else:
            print(f"Nenhuma composição ou insumo encontrado para: '{query}'")
            conn.close()
            return

    # Exibir Composição Encontrada
    fonte, cod, desc, unid, grupo, c_deson, c_nao_deson = comp_row
    print("\n" + "="*90)
    print(f"[{fonte}] COMPOSIÇÃO: {cod} — {desc}")
    print("="*90)
    print(f"Unidade: {unid} | Subgrupo: {grupo}")
    print(f"Custo Unitário Desonerado (BA):     R$ {c_deson:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print(f"Custo Unitário Não Desonerado (BA): R$ {c_nao_deson:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print("-" * 90)
    print(f"{'TIPO':<12} | {'CÓDIGO':<8} | {'DESCRIÇÃO DO ITEM':<42} | {'UN':<3} | {'COEFICIENTE':<11} | {'PU (R$)':<8} | {'TOTAL (R$)'}")
    print("-" * 90)
    
    # Buscar itens analíticos da composição
    cur.execute("""
        SELECT tipo_item, codigo_item, descricao, unidade, coeficiente 
        FROM composicao_itens 
        WHERE codigo_composicao = ?
    """, (cod,))
    itens = cur.fetchall()
    
    if not itens:
        print("  (Composição sem detalhamento de itens cadastrado no banco analítico)")
    else:
        for it in itens:
            tipo_it, cod_it, desc_it, unid_it, coef_it = it
            
            p_unit = 0.0
            if tipo_it == 'INSUMO':
                cur.execute("SELECT preco_deson FROM insumos WHERE codigo = ?", (cod_it,))
                p_row = cur.fetchone()
                if p_row:
                    p_unit = p_row[0]
            else:
                cur.execute("SELECT custo_deson FROM composicoes WHERE codigo = ?", (cod_it,))
                p_row = cur.fetchone()
                if p_row:
                    p_unit = p_row[0]
                    
            v_total = p_unit * coef_it if p_unit > 0 else 0.0
            desc_short = desc_it[:40] if len(desc_it) > 40 else desc_it
            p_str = f"{p_unit:.2f}" if p_unit > 0 else "-"
            t_str = f"{v_total:.2f}" if v_total > 0 else "-"
            
            print(f"{tipo_it:<12} | {cod_it:<8} | {desc_short:<42} | {unid_it:<3} | {coef_it:<11.4f} | {p_str:<8} | {t_str}")
            
    print("="*90 + "\n")
    conn.close()

if __name__ == "__main__":
    main()
