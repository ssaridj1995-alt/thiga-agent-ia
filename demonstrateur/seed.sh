#!/bin/sh
set -eu
export OLLAMA_HOST=127.0.0.1:11434
cd /root/.ollama/models 2>/dev/null || { mkdir -p /root/.ollama/models; cd /root/.ollama/models; }
manifest=manifests/registry.ollama.ai/library/qwen3.5/9b-q4_K_M
digest=56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90
wrapper=7dd7bb310c1f18ad132c7fd72e73d4f6cff2e916c596a818701d2a1269037c7f
source=/model-reference/qwen-manifest.json
hash() { sha256sum "$1" | cut -d' ' -f1; }
[ "$(hash "$source")" = "$digest" ]
if [ ! -f "$manifest" ]; then
  ollama serve >/dev/null 2>&1 &
  pid=$!
  trap 'kill "$pid" 2>/dev/null || true' EXIT INT TERM
  i=0
  until ollama list >/dev/null 2>&1; do i=$((i+1)); [ "$i" -lt 60 ]; sleep 1; done
  echo '{"event":"model_seed_pull_started"}'
  ollama pull qwen3.5:9b-q4_K_M >/dev/null 2>&1 || { echo '{"event":"model_seed_pull_failed"}'; exit 1; }
  kill "$pid"
  wait "$pid" || true
  trap - EXIT INT TERM
else
  echo '{"event":"model_seed_existing"}'
fi
[ ! -L "$manifest" ]
actual=$(hash "$manifest")
case "$actual" in
  "$digest") ;;
  "$wrapper") [ "$(hash "blobs/sha256-$digest")" = "$digest" ] ;;
  *) echo '{"event":"model_manifest_divergence"}'; exit 1 ;;
esac
sha256sum --strict --quiet -c /model-reference/qwen-blobs.sha256
if [ "$actual" = "$wrapper" ]; then
  tmp=$(mktemp "${manifest}.pending.XXXXXX")
  trap 'rm -f "$tmp"' EXIT INT TERM
  cp "$source" "$tmp"
  sync "$tmp"
  mv -f "$tmp" "$manifest"
  trap - EXIT INT TERM
  echo '{"event":"model_seed_wrapper_normalized"}'
fi
[ "$(hash "$manifest")" = "$digest" ]
echo '{"event":"model_seed_complete","reference_digest":"56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90"}'
