# Mapa de Composições

Os arquivos legados diretamente em `01-DISCIPLINAS_MARKDOWN/` permanecem em quarentena. A publicação SINAPI válida é consultada no SQLite; a ORSE válida é consultada no portal oficial/cache rastreável. A carga ORSE genérica foi isolada sob `ORSE_LEGADO_QUARENTENA`.

Consulte o status e as capacidades em `FONTES_DADOS.json`. `paradigma_cpu` e `preco_direto` são permissões diferentes.

Consultas válidas:

```powershell
python 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py 93680 --fonte SINAPI --regime nao_desonerado
python 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_orse_oficial.py "caixa de drenagem"
python 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_cpu_propria.py pergolado
```
