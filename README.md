# Squad de Orçamento DFE / FPE Projetos

Arquitetura operacional auditável para levantamento, orçamento, cotação, auditoria e exportação de pacotes de obras. O fluxo é **fail-closed**: falta de evidência, fonte não liberada ou fórmula sem valor calculado resulta em bloqueio.

## Situação operacional

- O estado original está preservado no GitHub pela tag `v0.1.0-baseline`.
- Os gates mecânicos ausentes foram recuperados das skills locais e endurecidos.
- O SINAPI oficial CAIXA, Bahia, competência `2026-07`, está `LIBERADA` nos regimes desonerado e não desonerado; o ZIP bruto e seu SHA-256 integram a cadeia de custódia.
- A base ORSE continua `QUARENTENADA` porque o XML disponível apresenta descrições genéricas incompatíveis com uma tabela oficial. Essa restrição não paralisa orçamentos que usem somente SINAPI/CPU/cotação válidos.
- O corpus legado de precedentes está `QUARENTENADO` porque mistura transcrições, respostas FPE e inferências sem revisão por caso.
- Enquanto uma fonte efetivamente usada no orçamento não estiver `LIBERADA`, o pacote não pode receber veredito final de envio.
- Registros oficiais SINAPI sem preço positivo na Bahia permanecem consultáveis para validar existência/descrição, mas seu uso em precificação é bloqueado item a item.

## Fluxo controlado

`FONTES_CONGELADAS → QTO_PRONTO → EAP_PRONTA → PRECIFICACAO_PRONTA → COTACOES_PRONTAS → AUDITORIA_PENDENTE → AUDITORIA_APROVADA → EXPORTACAO_STAGING → POS_EXPORTACAO_OK → AUTORIZADO → SELADO`

Ana audita sem alterar o orçamento e, quando tudo está conforme, emite `PRE_LIBERADO`. Eduardo exporta para *staging*. Um verificador independente compara o pacote final e registra os hashes; depois da autorização humana, o selo muda o gate final para `LIBERADO`.

## Comandos principais

```powershell
python -m pip install -r requirements.txt
python scripts/iniciar_squad.py --help
python scripts/atualizar_estado.py --help
python scripts/build_handoff.py --help
python scripts/amostrar_codigos.py --help
python scripts/simulate_supat_preenvio.py --help
python scripts/verify_export_package.py --help
python scripts/importar_sinapi.py --help
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

Consulta de preços, exigindo fonte e regime explícitos:

```powershell
python 03-BASE_DE_PRECOS/04-SCRIPTS/consultar_composicao.py --help
```

## Estrutura

- `01-PROMPTS/`: prompts mínimos; `AGENTS.md` é a fonte normativa.
- `SKILL.md`: entrypoint da skill Codex instalada por junction para este runtime versionado.
- `02-TEMPLATES/`: matriz canônica do orçamento.
- `03-BASE_DE_PRECOS/`: SQLite, proveniência das fontes, cadernos e CPUs.
- `04-BASE_CONHECIMENTO_SUPAT/`: checklist, registro de proveniência, precedentes em quarentena e calibração independente.
- `scripts/`: orquestração, validação, auditoria e gate pós-exportação.
- `schemas/`: contratos dos handoffs entre agentes.
- `tests/`: testes automatizados dos controles críticos.
