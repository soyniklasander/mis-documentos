#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
USO="Uso: $0 <consulta> [tipo]
Tipos: sbs, afp, rcc, placa, soat, licencia, telefono, ruc
Ejemplos:
  $0 48213083 sbs
  $0 ABC123   placa
  $0 999888777 telefono
  $0 20123456789 ruc"

TIPO="${2:-persona}"
PARAM="$1"
if [ -z "$PARAM" ]; then
  echo "$USO"
  exit 1
fi

case "$TIPO" in
  persona)   M="get_person('$PARAM')" ;;
  sbs)       M="get_sbs('$PARAM')" ;;
  afp)       M="get_afp('$PARAM')" ;;
  rcc)       M="get_rcc('$PARAM')" ;;
  placa)     M="get_plate('$PARAM')" ;;
  soat)      M="get_soat('$PARAM')" ;;
  licencia)  M="get_licence('$PARAM')" ;;
  telefono)  M="get_phone('$PARAM')" ;;
  ruc)       M="get_sunat('$PARAM')" ;;
  *)         echo "Tipo no valido: $TIPO"; exit 1 ;;
esac

python3 -c "
from tacto_client import TACTO
import json
api = TACTO(token_file='$DIR/tacto_token.json')
r = $M
print(json.dumps(r, indent=2, ensure_ascii=False))
"
