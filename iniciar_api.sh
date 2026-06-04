#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$DIR/api_server.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "API server ya esta corriendo (PID $(cat "$PID_FILE"))"
  echo "  http://127.0.0.1:9180"
  exit 0
fi

cd "$DIR"
nohup python3 api_server.py > api_server.log 2>&1 &
echo $! > "$PID_FILE"
sleep 1
echo "API server iniciado (PID $!)"
echo "  http://127.0.0.1:9180"
echo "  Log: $DIR/api_server.log"
echo ""
echo "Para probar:"
echo "  curl http://127.0.0.1:9180/persona/48213083"
