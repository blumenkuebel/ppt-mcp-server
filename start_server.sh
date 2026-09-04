#!/usr/bin/env bash
#
# Startet den Office-PowerPoint-MCP-Server im HTTP-Modus.
# Beendet zuvor einen evtl. laufenden Prozess auf dem Port.
#
# Nutzung:
#   ./start_server.sh            # Standard-Port 8001
#   ./start_server.sh 8002       # eigener Port
#
# Optionaler API-Key-Schutz für /upload, /download, /files:
#   MCP_API_KEY=geheim ./start_server.sh
#   curl -H "X-API-Key: geheim" -F "file=@deck.pptx" http://host:8001/upload
#
set -euo pipefail

# In das Verzeichnis dieses Skripts wechseln
cd "$(dirname "$0")"

PORT="${1:-8001}"
HOST="${MCP_HOST:-0.0.0.0}"
VENV=".venv"

# --- venv sicherstellen -----------------------------------------------------
if [ ! -d "$VENV" ]; then
  echo "==> Kein venv gefunden. Erstelle $VENV ..."
  python3 -m venv "$VENV"
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
else
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
fi

# --- Port freimachen --------------------------------------------------------
PIDS="$(lsof -ti tcp:"$PORT" || true)"
if [ -n "$PIDS" ]; then
  echo "==> Beende Prozess(e) auf Port $PORT: $PIDS"
  # shellcheck disable=SC2086
  kill $PIDS 2>/dev/null || true
  sleep 1
  PIDS="$(lsof -ti tcp:"$PORT" || true)"
  if [ -n "$PIDS" ]; then
    # shellcheck disable=SC2086
    kill -9 $PIDS 2>/dev/null || true
  fi
else
  echo "==> Port $PORT ist frei."
fi

# --- Server starten ---------------------------------------------------------
echo "==> Starte MCP-Server auf http://$HOST:$PORT/mcp"
export PPT_TEMPLATE_PATH="$(pwd)/templates"
exec python ppt_mcp_server.py --transport http --port "$PORT"
