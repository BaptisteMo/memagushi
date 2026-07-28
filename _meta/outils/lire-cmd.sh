#!/usr/bin/env bash
# Wrapper de la commande /lire.
#
# Par défaut on génère un .m4a et on l'ouvre dans le lecteur : la session rend
# la main tout de suite, et on récupère pause, vitesse et retour arrière — ce
# que `say` seul ne donne pas.
#
# --direct parle immédiatement, en tâche de fond pour ne pas bloquer la session.

set -uo pipefail

SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lire.py"

if [[ $# -eq 0 ]]; then
  echo "Usage : /lire <fiche> [-s section] [--direct]"
  echo
  python3 "$SCRIPT" --voix
  exit 0
fi

direct=0
args=()
for a in "$@"; do
  case "$a" in
    --direct|--parle) direct=1 ;;
    *) args+=("$a") ;;
  esac
done

# --voix, --texte et -f pilotent eux-mêmes leur sortie : on les laisse passer.
for a in "${args[@]}"; do
  case "$a" in
    --voix|-t|--texte|-f|--fichier)
      exec python3 "$SCRIPT" "${args[@]}" ;;
  esac
done

if (( direct )); then
  nohup python3 "$SCRIPT" "${args[@]}" >/tmp/lire-direct.log 2>&1 &
  pid=$!
  sleep 1
  head -1 /tmp/lire-direct.log 2>/dev/null
  echo "Lecture en cours (PID $pid). Pour couper : kill $pid"
else
  python3 "$SCRIPT" "${args[@]}" -f
fi
