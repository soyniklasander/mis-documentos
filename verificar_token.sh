#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -c "
from tacto_client import TACTO
api = TACTO(token_file='$DIR/tacto_token.json')
r = api.get_person('48213083')
p = r.get('person', r)
print('Token: ACTIVO')
print(f'Sesion: {p[\"fullName\"]}')
" 2>&1 || echo "Token: INACTIVO (se relogueara automaticamente al consultar)"
