#!/usr/bin/env bash
# Script de deploy da Task API com Docker Compose.
#
# Uso:
#   bash scripts/deploy.sh up     # sobe a aplicação e executa o smoke test
#   bash scripts/deploy.sh logs   # mostra os logs do contêiner
#   bash scripts/deploy.sh down   # encerra e remove o ambiente
#
# Variáveis opcionais:
#   IMAGE / TAG  imagem publicada no registro (ex.: ghcr.io/dono/repo e abc1234).
#                Sem elas, a imagem é construída localmente a partir do Dockerfile.
#   HOST_PORT    porta no host (padrão 8000).
set -euo pipefail

cd "$(dirname "$0")/.."

HOST_PORT="${HOST_PORT:-8000}"
BASE_URL="http://localhost:${HOST_PORT}"
export HOST_PORT

deploy() {
  if [ -n "${IMAGE:-}" ]; then
    echo ">> Baixando a imagem ${IMAGE}:${TAG:-local}"
    docker compose pull
    docker compose up -d --no-build
  else
    echo ">> Construindo a imagem localmente"
    docker compose up -d --build
  fi
}

wait_for_health() {
  echo ">> Aguardando a aplicação ficar saudável"
  for attempt in $(seq 1 30); do
    if curl -fsS "${BASE_URL}/health" >/dev/null 2>&1; then
      echo "Aplicação saudável após ${attempt} tentativa(s)."
      return 0
    fi
    sleep 1
  done
  echo "ERRO: a aplicação não ficou saudável a tempo." >&2
  docker compose logs --no-color >&2 || true
  return 1
}

smoke_test() {
  echo ">> Smoke test: criando e listando uma tarefa"
  curl -fsS -X POST "${BASE_URL}/tasks" \
    -H "Content-Type: application/json" \
    -d '{"title": "deploy ok"}' >/dev/null
  curl -fsS "${BASE_URL}/tasks" | grep -q '"deploy ok"'
  echo "Smoke test aprovado."
}

case "${1:-up}" in
  up)
    deploy
    wait_for_health
    smoke_test
    ;;
  logs)
    docker compose logs --no-color
    ;;
  down)
    docker compose down --remove-orphans
    ;;
  *)
    echo "Uso: bash scripts/deploy.sh [up|logs|down]" >&2
    exit 2
    ;;
esac
