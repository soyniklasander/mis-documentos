#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -z "$1" ]; then
  echo "Uso: $0 <DNI>"
  echo "Ej:  $0 48213083"
  exit 1
fi
python3 -c "
from tacto_client import TACTO
import json, sys
api = TACTO(token_file='$DIR/tacto_token.json')
r = api.get_person(sys.argv[1])
print(json.dumps(r, indent=2, ensure_ascii=False))
" "$1"
