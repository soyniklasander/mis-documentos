#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"

if [ $# -lt 1 ]; then
  echo "Uso: $0 <archivo.csv> [tipo]"
  echo ""
  echo "Tipos:"
  echo "  personas   - DNI (una columna, 8 digitos)  [por defecto]"
  echo "  telefonos  - Numeros de telefono"
  echo "  ruc        - RUC (11 digitos)"
  echo ""
  echo "Ejemplos:"
  echo "  $0 dnis.csv"
  echo "  $0 telefonos.csv telefonos"
  echo "  $0 empresas.csv ruc"
  exit 1
fi

ARCHIVO="$1"
TIPO="${2:-personas}"

if [ ! -f "$ARCHIVO" ]; then
  echo "Archivo no encontrado: $ARCHIVO"
  exit 1
fi

python3 -c "
from tacto_client import TACTO
import sys

api = TACTO(token_file='$DIR/tacto_token.json')
print(f'Subiendo {sys.argv[1]} como tipo \"{sys.argv[2]}\"...')
resp = api.massive_upload(sys.argv[1], sys.argv[2])

if 'application/json' in resp.headers.get('Content-Type', ''):
    print(resp.json())
else:
    out = 'resultado.xlsx'
    with open(out, 'wb') as f:
        f.write(resp.content)
    print(f'Descargado: {out} ({len(resp.content)} bytes)')
" "$ARCHIVO" "$TIPO"
