# TEMPLATE CANÔNICO DE 10 COLUNAS (DC-001 / EC-001)
Faixa Oficial de Envio ($A:$J):
- Col A: Item (EAP 3 níveis)
- Col B: Código (SINAPI / ORSE / CPU)
- Col C: Banco (SINAPI, ORSE, FPE, COT)
- Col D: Descrição Oficial (Ipsis Verbis)
- Col E: Und (M, M2, M3, UN, KG, CJ)
- Col F: Quant. (Líquida)
- Col G: Valor Unit (sem BDI)
- Col H: Valor Unit c/ BDI (=ROUND(G_row*(1+$BDI$), 2))
- Col I: Total (=ROUND(F_row*H_row, 2))
- Col J: Peso % (=ROUND((I_row/$TOTAL_GERAL$)*100, 2))

Faixa de Bastidores (Oculta na Exportação):
- Col K: Status Interno (VALIDADO, COTACAO_PENDENTE...)
- Col L: Observação Interna (Notas e dúvidas de projeto)
