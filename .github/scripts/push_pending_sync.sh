#!/usr/bin/env bash
# Commitea y pushea cambios en pending_sync/ (candidatos guardados porque
# Redis no respondio, o candidatos ya recuperados y borrados). Con reintento
# porque hasta 40 jobs de MuRongPIG en paralelo pueden intentar pushear al
# mismo tiempo - un rebase + reintento simple alcanza para este volumen.
set -euo pipefail

if git status --porcelain pending_sync 2>/dev/null | grep -q .; then
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git add pending_sync

  for attempt in 1 2 3 4 5; do
    if git commit -m "pending_sync: actualizar candidatos sin sincronizar [skip ci]" 2>/dev/null; then
      :
    fi
    if git push; then
      echo "pending_sync sincronizado (intento $attempt)"
      exit 0
    fi
    echo "push rechazado, reintentando (intento $attempt)..."
    git fetch origin
    git rebase origin/main || { git rebase --abort || true; git pull --rebase origin main || true; }
    sleep $((RANDOM % 5 + 1))
  done
  echo "no se pudo pushear pending_sync tras varios intentos - no es fatal, la proxima corrida lo vuelve a intentar"
else
  echo "sin cambios en pending_sync/"
fi
