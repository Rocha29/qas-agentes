#!/usr/bin/env python3
"""
generate_dashboard.py — SIGMA-BIZ Dashboard Generator
Lê os resultados de todos os projetos de teste e gera reports/dashboard.md.
Executado automaticamente pelo CI após cada pipeline completo.

Uso:
    python tools/generate_dashboard.py
    python tools/generate_dashboard.py --output reports/dashboard.md
"""

import json
import xml.etree.ElementTree as ET
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ─── Configurações ────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
REPORTS_DIR = ROOT / "reports"
RESULTS_DIR = ROOT / "results"

SOURCES = {
    "playwright": ROOT / "lojinha-tests" / "test-results" / "results.json",
    "gradle":     ROOT / "lojinha-api-tests" / "build" / "test-results",
    "k6_smoke":   RESULTS_DIR / "k6-summary-latest.json",
    "k6_load":    RESULTS_DIR / "k6-load-latest.json",
}

SLA = {
    "p95_ms": 500,
    "p99_ms": 1000,
    "error_rate_pct": 1.0,
}

STATUS_OK    = "✅ Verde"
STATUS_WARN  = "⚠️  Atenção"
STATUS_FAIL  = "❌ Falhou"
STATUS_SKIP  = "⏭️  Sem dados"


# ─── Leitores de resultado ────────────────────────────────────────────────────

def read_playwright(path: Path) -> dict:
    """Lê o JSON de resultados do Playwright."""
    if not path.exists():
        return {"status": STATUS_SKIP, "total": 0, "passed": 0, "failed": 0, "skipped": 0}

    try:
        with open(path) as f:
            data = json.load(f)

        stats = data.get("stats", {})
        total   = stats.get("expected", 0)
        passed  = stats.get("expected", 0) - stats.get("unexpected", 0)
        failed  = stats.get("unexpected", 0)
        skipped = stats.get("skipped", 0)

        status = STATUS_OK if failed == 0 else STATUS_FAIL
        return {
            "status": status,
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "duration_ms": stats.get("duration", 0),
        }
    except Exception as e:
        return {"status": STATUS_WARN, "error": str(e), "total": 0, "passed": 0, "failed": 0}


def read_gradle(path: Path) -> dict:
    """Lê os XMLs JUnit do Gradle."""
    if not path.exists():
        return {"status": STATUS_SKIP, "total": 0, "passed": 0, "failed": 0, "errors": 0}

    total = passed = failed = errors = 0
    xml_files = list(path.rglob("TEST-*.xml"))

    if not xml_files:
        return {"status": STATUS_SKIP, "total": 0, "passed": 0, "failed": 0}

    try:
        for xml_file in xml_files:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            suite_tests   = int(root.attrib.get("tests", 0))
            suite_failed  = int(root.attrib.get("failures", 0))
            suite_errors  = int(root.attrib.get("errors", 0))
            suite_skipped = int(root.attrib.get("skipped", 0))

            total   += suite_tests
            failed  += suite_failed
            errors  += suite_errors
            passed  += suite_tests - suite_failed - suite_errors - suite_skipped

        status = STATUS_OK if (failed + errors) == 0 else STATUS_FAIL
        return {
            "status": status,
            "total": total,
            "passed": passed,
            "failed": failed + errors,
            "suites": len(xml_files),
        }
    except Exception as e:
        return {"status": STATUS_WARN, "error": str(e), "total": 0, "passed": 0, "failed": 0}


def read_k6(path: Path) -> dict:
    """Lê o JSON de summary do k6."""
    if not path.exists():
        return {"status": STATUS_SKIP}

    try:
        with open(path) as f:
            data = json.load(f)

        metrics = data.get("metrics", {})
        duration = metrics.get("http_req_duration", {}).get("values", {})
        failed_rate = metrics.get("http_req_failed", {}).get("values", {})

        p95 = duration.get("p(95)", 0)
        p99 = duration.get("p(99)", 0)
        avg = duration.get("avg", 0)
        error_rate_pct = failed_rate.get("rate", 0) * 100
        vus = data.get("metrics", {}).get("vus_max", {}).get("values", {}).get("max", 0)
        total_reqs = metrics.get("http_reqs", {}).get("values", {}).get("count", 0)

        warnings = []
        if p95 > SLA["p95_ms"]:
            warnings.append(f"p95 {p95:.0f}ms > {SLA['p95_ms']}ms")
        if error_rate_pct > SLA["error_rate_pct"]:
            warnings.append(f"error rate {error_rate_pct:.1f}% > {SLA['error_rate_pct']}%")

        status = STATUS_WARN if warnings else STATUS_OK
        return {
            "status": status,
            "p95_ms": round(p95, 1),
            "p99_ms": round(p99, 1),
            "avg_ms": round(avg, 1),
            "error_rate_pct": round(error_rate_pct, 2),
            "total_requests": int(total_reqs),
            "max_vus": int(vus),
            "warnings": warnings,
        }
    except Exception as e:
        return {"status": STATUS_WARN, "error": str(e)}


# ─── Gerador de dashboard ─────────────────────────────────────────────────────

def overall_status(results: dict) -> str:
    statuses = [v.get("status", STATUS_SKIP) for v in results.values()]
    if any(STATUS_FAIL in s for s in statuses):
        return "🔴 CRÍTICO"
    if any(STATUS_WARN in s for s in statuses):
        return "🟡 ATENÇÃO"
    if all(STATUS_SKIP in s for s in statuses):
        return "⚪ SEM DADOS"
    return "🟢 SAUDÁVEL"


def generate_dashboard(output_path: Path, results: dict, generated_at: str) -> str:
    pw  = results["playwright"]
    gr  = results["gradle"]
    k6s = results["k6_smoke"]
    k6l = results["k6_load"]

    overall = overall_status(results)

    lines = [
        f"# Dashboard de Qualidade — QA Agents",
        f"",
        f"**Gerado em:** {generated_at}  ",
        f"**Status geral:** {overall}",
        f"",
        f"---",
        f"",
        f"## Resumo por Camada",
        f"",
        f"| Camada | Agente | Status | Passaram | Falharam | Total |",
        f"|--------|--------|--------|----------|----------|-------|",
        f"| Web E2E | ARIA-WEB | {pw['status']} | {pw.get('passed', '-')} | {pw.get('failed', '-')} | {pw.get('total', '-')} |",
        f"| API | NEXUS-API | {gr['status']} | {gr.get('passed', '-')} | {gr.get('failed', '-')} | {gr.get('total', '-')} |",
        f"| Performance (smoke) | FLUX-PERF | {k6s['status']} | — | — | {k6s.get('total_requests', '-')} reqs |",
        f"| Performance (load) | FLUX-PERF | {k6l['status']} | — | — | {k6l.get('total_requests', '-')} reqs |",
        f"",
        f"---",
        f"",
        f"## Web E2E — ARIA-WEB (Playwright)",
        f"",
    ]

    if pw["status"] == STATUS_SKIP:
        lines.append("> Sem dados. Rode: `cd lojinha-tests && npx playwright test --reporter=json`")
    else:
        dur = pw.get("duration_ms", 0)
        lines += [
            f"| Indicador | Valor |",
            f"|-----------|-------|",
            f"| Testes passando | {pw.get('passed', 0)}/{pw.get('total', 0)} |",
            f"| Testes falhando | {pw.get('failed', 0)} |",
            f"| Testes ignorados | {pw.get('skipped', 0)} |",
            f"| Duração total | {dur/1000:.1f}s |",
            f"| Taxa de aprovação | {(pw.get('passed',0)/max(pw.get('total',1),1)*100):.1f}% |",
        ]

    lines += [
        f"",
        f"---",
        f"",
        f"## API — NEXUS-API (RestAssured + Gradle)",
        f"",
    ]

    if gr["status"] == STATUS_SKIP:
        lines.append("> Sem dados. Rode: `cd lojinha-api-tests && ./gradlew test`")
    else:
        lines += [
            f"| Indicador | Valor |",
            f"|-----------|-------|",
            f"| Suítes executadas | {gr.get('suites', '-')} |",
            f"| Testes passando | {gr.get('passed', 0)}/{gr.get('total', 0)} |",
            f"| Testes falhando | {gr.get('failed', 0)} |",
            f"| Taxa de aprovação | {(gr.get('passed',0)/max(gr.get('total',1),1)*100):.1f}% |",
        ]

    lines += [
        f"",
        f"---",
        f"",
        f"## Performance — FLUX-PERF (k6)",
        f"",
        f"### Smoke Test",
        f"",
    ]

    if k6s["status"] == STATUS_SKIP:
        lines.append("> Sem dados. Rode: `cd lojinha-performance/k6 && k6 run smoke.js --summary-export=../../results/k6-summary-latest.json`")
    else:
        sla_p95  = "✅" if k6s.get("p95_ms", 999) <= SLA["p95_ms"]  else "❌"
        sla_p99  = "✅" if k6s.get("p99_ms", 999) <= SLA["p99_ms"]  else "❌"
        sla_err  = "✅" if k6s.get("error_rate_pct", 99) <= SLA["error_rate_pct"] else "❌"

        lines += [
            f"| Métrica | Valor | SLA | Status |",
            f"|---------|-------|-----|--------|",
            f"| p95 response time | {k6s.get('p95_ms', '-')}ms | < {SLA['p95_ms']}ms | {sla_p95} |",
            f"| p99 response time | {k6s.get('p99_ms', '-')}ms | < {SLA['p99_ms']}ms | {sla_p99} |",
            f"| Avg response time | {k6s.get('avg_ms', '-')}ms | — | — |",
            f"| Error rate | {k6s.get('error_rate_pct', '-')}% | < {SLA['error_rate_pct']}% | {sla_err} |",
            f"| Total requests | {k6s.get('total_requests', '-')} | — | — |",
            f"| Max VUs | {k6s.get('max_vus', '-')} | — | — |",
        ]

        if k6s.get("warnings"):
            lines += ["", "**Alertas de SLA:**"]
            for w in k6s["warnings"]:
                lines.append(f"- ⚠️  {w}")

    lines += [
        f"",
        f"### Load Test",
        f"",
    ]

    if k6l["status"] == STATUS_SKIP:
        lines.append("> Sem dados de load test.")
    else:
        lines += [
            f"| Métrica | Valor |",
            f"|---------|-------|",
            f"| p95 | {k6l.get('p95_ms', '-')}ms |",
            f"| Total requests | {k6l.get('total_requests', '-')} |",
            f"| Error rate | {k6l.get('error_rate_pct', '-')}% |",
        ]

    # Alertas e ações recomendadas
    alerts = []
    actions = []

    if pw.get("failed", 0) > 0:
        alerts.append(f"{pw['failed']} teste(s) E2E falhando — revisar com ARIA-WEB")
        actions.append("Ativar ARIA-WEB e investigar os testes falhos: `claude --system-prompt agents/ARIA-WEB.md`")

    if gr.get("failed", 0) > 0:
        alerts.append(f"{gr['failed']} teste(s) de API falhando — revisar com NEXUS-API")
        actions.append("Ativar NEXUS-API: `claude --system-prompt agents/NEXUS-API.md`")

    for w in k6s.get("warnings", []):
        alerts.append(f"Performance: {w}")
        actions.append("Ativar FLUX-PERF para análise: `claude --system-prompt agents/FLUX-PERF.md`")

    lines += ["", "---", "", "## Alertas e Ações Recomendadas", ""]

    if not alerts:
        lines.append("Nenhum alerta. Todos os indicadores dentro dos limites esperados.")
    else:
        lines.append("### Alertas")
        for a in alerts:
            lines.append(f"- 🚨 {a}")
        lines += ["", "### Ações"]
        for i, a in enumerate(actions, 1):
            lines.append(f"{i}. {a}")

    lines += [
        f"",
        f"---",
        f"",
        f"## Como atualizar este dashboard",
        f"",
        f"```bash",
        f"# Manualmente",
        f"python tools/generate_dashboard.py",
        f"",
        f"# Automaticamente — após cada CI (ver .github/workflows/)",
        f"# O dashboard é gerado e commitado pelo pipeline",
        f"```",
        f"",
        f"*Gerado por `tools/generate_dashboard.py` — SIGMA-BIZ Dashboard Generator*",
    ]

    content = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return content


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Gera dashboard de qualidade em Markdown")
    parser.add_argument("--output", default=str(REPORTS_DIR / "dashboard.md"))
    args = parser.parse_args()

    output_path = Path(args.output)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("🔍 Lendo resultados dos testes...")

    results = {
        "playwright": read_playwright(SOURCES["playwright"]),
        "gradle":     read_gradle(SOURCES["gradle"]),
        "k6_smoke":   read_k6(SOURCES["k6_smoke"]),
        "k6_load":    read_k6(SOURCES["k6_load"]),
    }

    for name, result in results.items():
        status = result.get("status", STATUS_SKIP)
        print(f"  {name:15} → {status}")

    print(f"\n📝 Gerando dashboard em {output_path}...")
    generate_dashboard(output_path, results, generated_at)
    print(f"✅ Dashboard gerado com sucesso!")

    # Exit code 1 se houver falhas — útil para CI
    has_failures = any(
        STATUS_FAIL in r.get("status", "") for r in results.values()
    )
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
