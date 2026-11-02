#!/usr/bin/env bash
set -Eeuo pipefail
release="$1"
[[ "$release" =~ ^[0-9a-f]{40}$ ]]
base="$HOME/hello-station"
new="$base/releases/$release"
previous="$(cat "$base/current" 2>/dev/null || true)"
cd "$new"
export RELEASE_ID="$release"
docker compose -p hello-station build
rollback() {
  echo 'Deployment failed; attempting rollback' >&2
  if [[ "$previous" =~ ^[0-9a-f]{40}$ ]] && [[ -d "$base/releases/$previous" ]]; then
    (cd "$base/releases/$previous" && RELEASE_ID="$previous" docker compose -p hello-station up -d --no-build) || true
  fi
}
trap rollback ERR
docker compose -p hello-station up -d --no-build
healthy=false
for attempt in {1..30}; do
  if curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then healthy=true; break; fi
  sleep 2
done
if [[ "$healthy" != true ]]; then echo 'Health check failed' >&2; false; fi
printf '%s\n' "$release" > "$base/current"
trap - ERR
echo "Deployed $release"
