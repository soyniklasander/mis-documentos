#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"

if [ $# -lt 1 ]; then
  echo "Uso: $0 <archivo_con_dnis.txt>"
  echo ""
  echo "El archivo debe tener un DNI por linea (o separado por comas):"
  echo "  48213083"
  echo "  40825702"
  echo "  45647771"
  exit 1
fi

ARCHIVO="$1"
if [ ! -f "$ARCHIVO" ]; then
  echo "Archivo no encontrado: $ARCHIVO"
  exit 1
fi

python3 -c "
from tacto_client import TACTO
import json, sys, re

api = TACTO(token_file='$DIR/tacto_token.json')
contenido = open('$ARCHIVO').read()
dnis = re.findall(r'[0-9]{8}', contenido)

print(f'Consultando {len(dnis)} documentos...')
print()

for i, dni in enumerate(dnis, 1):
    try:
        r = api.get_person(dni)
        p = r.get('person', r)
        print(f'{i:4}. {dni} | {p.get(\"fullName\",\"-\"):40s} | {p.get(\"address\",\"-\"):30s} | {p.get(\"birthdate\",\"-\")}')
    except Exception as e:
        print(f'{i:4}. {dni} | ERROR: {e}')
"
