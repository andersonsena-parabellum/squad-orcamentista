#!/usr/bin/env python3
"""Cliente minimo e rastreavel para as consultas publicas do ORSE/CEHOP."""

from __future__ import annotations

import hashlib
import http.cookiejar
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parents[1]
REGISTRY_PATH = BASE_DIR / "FONTES_DADOS.json"
OFFICIAL_DIR = BASE_DIR / "00-FONTES_OFICIAIS" / "ORSE-2026-06"
CACHE_DIR = OFFICIAL_DIR / "cache"
RAW_DIR = OFFICIAL_DIR / "raw"
PORTAL = "https://orse.cehop.se.gov.br"
CODE_RE = re.compile(r"^(\d{1,5})(?:/ORSE)?$", re.IGNORECASE)


def _registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["fontes"]["ORSE"]


def _period() -> tuple[int, int, int]:
    record = _registry()
    year, month = (int(part) for part in record["competencia"].split("-"))
    return year, month, int(record.get("ordem_periodo", 1))


def _decode(raw: bytes) -> str:
    # A pagina atual chega em UTF-8, embora o HTML legado nem sempre o declare.
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def _fetch(url: str, data: bytes | None = None, opener: Any | None = None) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": "DFE-FPE-Squad/1.1 (+auditoria; consulta pontual)"},
    )
    if opener is None:
        response_context = urllib.request.urlopen(request, timeout=30)
    else:
        response_context = opener.open(request, timeout=30)
    with response_context as response:
        raw = response.read()
        return raw, response.geturl()


def _number(value: str) -> float:
    cleaned = value.strip().replace(".", "").replace(",", ".")
    return float(Decimal(cleaned))


def _rows(table: Any) -> list[list[str]]:
    result = []
    for tr in table.find_all("tr", recursive=False):
        cells = [" ".join(td.get_text(" ", strip=True).split()) for td in tr.find_all(["td", "th"], recursive=False)]
        if cells:
            result.append(cells)
    return result


def composition_url(code: str) -> str:
    match = CODE_RE.fullmatch(code.strip())
    if not match:
        raise ValueError("codigo ORSE invalido")
    year, month, order = _period()
    query = urllib.parse.urlencode(
        {
            "font_sg_fonte": "ORSE",
            "serv_nr_codigo": int(match.group(1)),
            "peri_nr_ano": year,
            "peri_nr_mes": month,
            "peri_nr_ordem": order,
        }
    )
    return f"{PORTAL}/composicao.asp?{query}"


def parse_composition(raw: bytes, url: str) -> dict[str, Any]:
    soup = BeautifulSoup(_decode(raw), "html.parser")
    tables = [_rows(table) for table in soup.find_all("table")]
    service_rows = next((rows for rows in tables if rows and rows[0] == ["Serviço"]), None)
    analytic_rows = next((rows for rows in tables if rows and rows[0] == ["Composição de Preço"]), None)
    detail_rows = next((rows for rows in tables if rows and rows[0] == ["Relação Detalhada de Insumos"]), None)
    totals_rows = next((rows for rows in tables if rows and rows[0] == ["Totais"]), None)
    if not service_rows or len(service_rows) < 3 or len(service_rows[2]) < 3:
        raise ValueError("pagina ORSE sem composicao identificavel")
    code_label, description, unit = service_rows[2][:3]
    match = re.match(r"(\d+)/ORSE", code_label, re.IGNORECASE)
    if not match:
        raise ValueError("pagina retornou fonte/codigo inesperado")

    analytic = []
    for row in (analytic_rows or [])[2:]:
        if len(row) < 7 or not re.match(r"\d+/(?:ORSE|SINAPI)$", row[1], re.IGNORECASE):
            continue
        child_code, child_source = row[1].split("/", 1)
        analytic.append(
            {
                "tipo": "COMPOSICAO_AUXILIAR",
                "codigo": child_code.lstrip("0") or "0",
                "fonte": child_source.upper(),
                "descricao": row[2],
                "unidade": row[3],
                "coeficiente": _number(row[4]),
                "custo_unitario_orse_se": _number(row[5]),
                "custo_total_orse_se": _number(row[6]),
            }
        )

    detailed = []
    for row in (detail_rows or [])[2:]:
        if len(row) < 7 or not re.match(r"\d+/(?:ORSE|SINAPI)$", row[1], re.IGNORECASE):
            continue
        item_code, item_source = row[1].split("/", 1)
        detailed.append(
            {
                "classe_orse": row[0],
                "codigo": item_code.lstrip("0") or "0",
                "fonte": item_source.upper(),
                "descricao": row[2],
                "unidade": row[3],
                "coeficiente": _number(row[4]),
                "custo_unitario_orse_se": _number(row[5]),
                "custo_total_orse_se": _number(row[6]),
            }
        )

    totals: dict[str, float] = {}
    if totals_rows and len(totals_rows) >= 3:
        totals = {key: _number(value) for key, value in zip(totals_rows[1], totals_rows[2])}
    return {
        "schema_version": "1.0.0",
        "fonte": "ORSE",
        "uf": "SE",
        "competencia": _registry()["competencia"],
        "codigo": match.group(1).lstrip("0") or "0",
        "codigo_exibicao": code_label,
        "descricao": description,
        "unidade": unit,
        "custo_total_orse_se": totals.get("Valor Total"),
        "composicoes_auxiliares": analytic,
        "insumos_detalhados": detailed,
        "totais": totals,
        "proveniencia": {
            "url": url,
            "sha256_html": hashlib.sha256(raw).hexdigest(),
            "capturado_em": datetime.now(timezone.utc).isoformat(),
            "aviso": "Custos do ORSE/SE; uso como preço direto fora de SE exige autorização e justificativa expressas.",
        },
    }


def fetch_composition(code: str, save: bool = True) -> dict[str, Any]:
    url = composition_url(code)
    raw, final_url = _fetch(url)
    result = parse_composition(raw, final_url)
    requested = (CODE_RE.fullmatch(code.strip()).group(1).lstrip("0") or "0")  # type: ignore[union-attr]
    if result["codigo"] != requested:
        raise ValueError(f"ORSE devolveu codigo {result['codigo']} para a consulta {requested}")
    if save:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        padded = requested.zfill(5)
        raw_path = RAW_DIR / f"composicao-{padded}.html"
        json_path = CACHE_DIR / f"composicao-{padded}.json"
        raw_path.write_bytes(raw)
        result["proveniencia"]["arquivo_html"] = str(raw_path.relative_to(BASE_DIR)).replace("\\", "/")
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def load_cached_composition(code: str) -> dict[str, Any] | None:
    match = CODE_RE.fullmatch(code.strip())
    if not match:
        return None
    path = CACHE_DIR / f"composicao-{(match.group(1).lstrip('0') or '0').zfill(5)}.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_rel = data.get("proveniencia", {}).get("arquivo_html")
    if not raw_rel:
        return None
    raw_path = BASE_DIR / raw_rel
    if not raw_path.is_file() or hashlib.sha256(raw_path.read_bytes()).hexdigest() != data["proveniencia"].get("sha256_html"):
        return None
    if data.get("competencia") != _registry()["competencia"]:
        return None
    expected_url = composition_url(code)
    if data.get("proveniencia", {}).get("url") != expected_url:
        return None
    # Reconstroi os numeros da evidencia bruta: o JSON editavel nao e a fonte.
    verified = parse_composition(raw_path.read_bytes(), expected_url)
    if verified["codigo"] != (match.group(1).lstrip("0") or "0"):
        return None
    verified["proveniencia"].update({
        "modo": "CACHE_LOCAL",
        "arquivo_html": raw_rel,
        "capturado_em": data["proveniencia"].get("capturado_em"),
    })
    return verified


def search_compositions(description: str, page: int = 1) -> dict[str, Any]:
    if not description.strip():
        raise ValueError("informe uma descricao para evitar varredura massiva do portal")
    year, month, order = _period()
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    data = urllib.parse.urlencode(
        {
            "sltFonte": "ORSE",
            "sltPeriodo": f"{year}-{month}-{order}",
            "sltGrupoServico": "0",
            "rdbCriterio": "2",
            "txtDescricao": description,
            "Submit": "Consultar",
        }
    ).encode("ascii")
    raw, _ = _fetch(f"{PORTAL}/servicosargumento.asp?tarefa=consultar", data=data, opener=opener)
    if page > 1:
        raw, _ = _fetch(f"{PORTAL}/servicosargumento.asp?tarefa=consultar&page={page}", opener=opener)
    soup = BeautifulSoup(_decode(raw), "html.parser")
    found: dict[str, dict[str, Any]] = {}
    for link in soup.find_all("a", href=True):
        href = str(link["href"])
        if not href.lower().startswith("composicao.asp?"):
            continue
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(href).query)
        code = (query.get("serv_nr_codigo") or [""])[0]
        if not code or code in found:
            continue
        row = link.find_parent("tr")
        cells = _rows(row.find_parent("table")) if row else []
        row_cells = [" ".join(td.get_text(" ", strip=True).split()) for td in row.find_all("td", recursive=False)] if row else []
        if len(row_cells) >= 4:
            found[code] = {
                "codigo": code,
                "descricao": row_cells[1],
                "unidade": row_cells[2],
                "custo_total_orse_se": _number(row_cells[3]),
                "url": urllib.parse.urljoin(PORTAL + "/", href),
            }
    text = " ".join(soup.get_text(" ", strip=True).split())
    total_match = re.search(r"Total de Serviços\s+(\d+)\s+-\s+Página\s+(\d+)\s+de\s+(\d+)", text)
    return {
        "fonte": "ORSE",
        "uf": "SE",
        "competencia": _registry()["competencia"],
        "consulta": description,
        "pagina": page,
        "total": int(total_match.group(1)) if total_match else len(found),
        "paginas": int(total_match.group(3)) if total_match else 1,
        "resultados": list(found.values()),
    }
