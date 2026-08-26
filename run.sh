#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

IMAGE="${AUSTRO_TAI_IMAGE:-austro-tai-llm-test}"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "Building Docker image $IMAGE ..."
  docker build -t "$IMAGE" .
fi

if [[ $# -eq 0 ]]; then
  set -- parse
fi

if [[ "$1" == "test" ]]; then
  docker run --rm --entrypoint python -v "$ROOT:/app" -w /app "$IMAGE" -m pytest -q
  exit 0
fi

if [[ "$1" == "shell" ]]; then
  docker run --rm -it --entrypoint bash -v "$ROOT:/app" -w /app "$IMAGE"
  exit 0
fi

docker run --rm \
  -v "$ROOT:/app" \
  -w /app \
  -e PYTHONUNBUFFERED=1 \
  -e NLP_API_URL="${NLP_API_URL:-http://13.229.134.226:5000/chat}" \
  -e NLP_MODEL="${NLP_MODEL:-gpt-4.1}" \
  -e NLP_API_KEY="${NLP_API_KEY:-}" \
  -e NLP_MAX_COMPLETION_TOKENS="${NLP_MAX_COMPLETION_TOKENS:-8000}" \
  -e JUDGE_BATCH_SIZE="${JUDGE_BATCH_SIZE:-15}" \
  -e N_PERMUTATIONS="${N_PERMUTATIONS:-1000}" \
  -e GENEROSITY_THRESHOLD="${GENEROSITY_THRESHOLD:-4}" \
  "$IMAGE" "$@"
