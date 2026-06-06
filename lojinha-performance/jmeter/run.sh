#!/usr/bin/env bash
# FLUX — Lojinha Performance Tests | Modo CI (sem GUI)
# Uso: ./run.sh [smoke|load|stress|all]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[FLUX]${NC} $*"; }
ok()  { echo -e "${GREEN}[OK]${NC} $*"; }
warn(){ echo -e "${YELLOW}[WARN]${NC} $*"; }
err() { echo -e "${RED}[ERRO]${NC} $*"; }

# Verifica se JMeter está instalado
check_jmeter() {
  if ! command -v jmeter &> /dev/null; then
    err "JMeter não encontrado. Instale com: brew install jmeter"
    exit 1
  fi
  local version
  version=$(jmeter --version 2>&1 | head -1)
  ok "JMeter encontrado: $version"
}

# Executa um plano de teste
run_test() {
  local name="$1"
  local jmx="$2"
  local jtl_file="$3"
  local report_dir="$4"

  log "Iniciando: $name"
  log "Plano: $jmx"
  log "Resultados: $jtl_file"
  log "Relatório HTML: $report_dir"

  # Remove relatório anterior se existir
  if [ -d "$report_dir" ]; then
    warn "Removendo relatório anterior em: $report_dir"
    rm -rf "$report_dir"
  fi

  # Remove JTL anterior se existir
  if [ -f "$jtl_file" ]; then
    rm -f "$jtl_file"
  fi

  # Executa JMeter em modo não-GUI
  jmeter -n \
    -t "$jmx" \
    -l "$jtl_file" \
    -e -o "$report_dir" \
    -Jjmeter.save.saveservice.output_format=csv \
    -Jjmeter.save.saveservice.print_field_names=true

  local exit_code=$?

  if [ $exit_code -eq 0 ]; then
    ok "$name concluído com sucesso!"
    ok "Relatório HTML disponível em: $report_dir/index.html"
  else
    err "$name falhou com código de saída: $exit_code"
    return $exit_code
  fi
}

# Parser de resultados do JTL (extrai métricas chave)
parse_results() {
  local jtl_file="$1"
  local test_name="$2"

  if [ ! -f "$jtl_file" ]; then
    warn "Arquivo JTL não encontrado: $jtl_file"
    return
  fi

  echo ""
  echo "============================================================"
  echo "  FLUX — Resultados: $test_name"
  echo "============================================================"

  # Usa awk para calcular métricas do CSV JTL
  awk -F',' 'NR > 1 {
    total++
    elapsed = $2
    success = $8
    sum += elapsed
    if (elapsed < min || min == 0) min = elapsed
    if (elapsed > max) max = elapsed
    if (success == "false") errors++

    # Armazena para percentis
    times[total] = elapsed

  } END {
    if (total == 0) { print "Sem dados"; exit }

    # Ordena os tempos (bubble sort simples para awk)
    n = total
    for (i = 1; i <= n; i++) {
      for (j = 1; j <= n - i; j++) {
        if (times[j] > times[j+1]) {
          tmp = times[j]; times[j] = times[j+1]; times[j+1] = tmp
        }
      }
    }

    avg = sum / total
    error_rate = (errors / total) * 100
    p90 = times[int(n * 0.90)]
    p95 = times[int(n * 0.95)]
    p99 = times[int(n * 0.99)]

    printf "  Requisições totais : %d\n", total
    printf "  Erros              : %d (%.2f%%)\n", errors, error_rate
    printf "  Tempo médio        : %.0f ms\n", avg
    printf "  Tempo mínimo       : %d ms\n", min
    printf "  Tempo máximo       : %d ms\n", max
    printf "  p90                : %d ms\n", p90
    printf "  p95                : %d ms\n", p95
    printf "  p99                : %d ms\n", p99
  }' "$jtl_file"

  # Threshold check
  echo ""
  echo "  --- Validação de Thresholds ---"
  awk -F',' 'NR > 1 {
    total++
    elapsed = $2
    success = $8
    sum += elapsed
    if (success == "false") errors++
    times[total] = elapsed
  } END {
    if (total == 0) exit
    n = total
    for (i = 1; i <= n; i++)
      for (j = 1; j <= n - i; j++)
        if (times[j] > times[j+1]) { tmp = times[j]; times[j] = times[j+1]; times[j+1] = tmp }

    p95 = times[int(n * 0.95)]
    error_rate = (errors / total) * 100

    if (p95 < 500) print "  [PASS] p95 < 500ms   :", p95, "ms"
    else           print "  [FAIL] p95 >= 500ms  :", p95, "ms"

    if (error_rate < 1) print "  [PASS] Erro < 1%     :", error_rate, "%"
    else                print "  [FAIL] Erro >= 1%    :", error_rate, "%"
  }' "$jtl_file"

  echo "============================================================"
  echo ""
}

# Main
main() {
  local mode="${1:-smoke}"

  check_jmeter
  mkdir -p "$RESULTS_DIR"

  case "$mode" in
    smoke)
      run_test \
        "Smoke Test (1 usuário, 1 min)" \
        "$SCRIPT_DIR/lojinha-smoke.jmx" \
        "$RESULTS_DIR/smoke.jtl" \
        "$RESULTS_DIR/smoke-report"
      parse_results "$RESULTS_DIR/smoke.jtl" "Smoke Test"
      ;;

    load)
      run_test \
        "Load Test (10 usuários, ramp 1m + load 3m + down 1m)" \
        "$SCRIPT_DIR/lojinha-load.jmx" \
        "$RESULTS_DIR/load.jtl" \
        "$RESULTS_DIR/load-report"
      parse_results "$RESULTS_DIR/load.jtl" "Load Test"
      ;;

    stress)
      run_test \
        "Stress Test (5→50 usuários, +5 a cada 30s)" \
        "$SCRIPT_DIR/lojinha-stress.jmx" \
        "$RESULTS_DIR/stress.jtl" \
        "$RESULTS_DIR/stress-report"
      parse_results "$RESULTS_DIR/stress.jtl" "Stress Test"
      ;;

    all)
      log "Executando todos os testes em sequência..."
      run_test "Smoke" "$SCRIPT_DIR/lojinha-smoke.jmx" "$RESULTS_DIR/smoke.jtl" "$RESULTS_DIR/smoke-report"
      parse_results "$RESULTS_DIR/smoke.jtl" "Smoke Test"

      run_test "Load" "$SCRIPT_DIR/lojinha-load.jmx" "$RESULTS_DIR/load.jtl" "$RESULTS_DIR/load-report"
      parse_results "$RESULTS_DIR/load.jtl" "Load Test"

      run_test "Stress" "$SCRIPT_DIR/lojinha-stress.jmx" "$RESULTS_DIR/stress.jtl" "$RESULTS_DIR/stress-report"
      parse_results "$RESULTS_DIR/stress.jtl" "Stress Test"
      ;;

    *)
      echo "Uso: $0 [smoke|load|stress|all]"
      echo ""
      echo "  smoke  — 1 usuário, 1 minuto (validação básica)"
      echo "  load   — 10 usuários, fluxo CRUD completo"
      echo "  stress — 5→50 usuários, +5 a cada 30s"
      echo "  all    — executa os três em sequência"
      exit 1
      ;;
  esac
}

main "$@"
