#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$DIR/api_server.pid" ] && kill -0 "$(cat "$DIR/api_server.pid")" 2>/dev/null; then
  echo "Deteniendo API server (PID $(cat "$DIR/api_server.pid"))..."
  kill "$(cat "$DIR/api_server.pid")"
  rm -f "$DIR/api_server.pid"
  echo "Detenido."
else
  echo "API server no esta corriendo."
fi
