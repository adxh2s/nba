#!/bin/bash

# Usage: ./run_script.sh nom_du_script.py [args...]

if [ -z "$1" ]; then
  echo "Usage: $0 script_name.py [args...]"
  exit 1
fi

SCRIPT_NAME="$1"
shift

# Chemin absolu vers le dossier src, en partant du dossier contenant ce script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SRC_DIR="$SCRIPT_DIR/src"

# Nom du module Python sans extension
SCRIPT_MODULE="${SCRIPT_NAME%.py}"

# Se positionner dans src
cd "$SRC_DIR" || { echo "Impossible de trouver le dossier src"; exit 1; }

# Lancer le script avec python -m scripts.nom_module et passer les arguments
python3 -m scripts."$SCRIPT_MODULE" "$@"
