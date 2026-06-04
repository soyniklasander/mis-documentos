GUIA RAPIDA - SOLUCIONESE RICHI
================================

Escenario: servidor 207.244.230.123 -> tacto.ucvox.com
Token ya almacenado, sesion activa. No necesitas loguear otra vez.

------------------------------------------------------------------------
PASO 1: VERIFICAR QUE EL TOKEN SIGUE VIVO
------------------------------------------------------------------------

Cualquier consulta de prueba:

  cd /root/solucionese\ richi
  python3 -c "
from tacto_client import TACTO
api = TACTO(token_file='tacto_token.json')
r = api.get_person('48213083')
print(r['person']['fullName'])
"

Si ves un nombre, todo bien. Si ves error 401, el token expiro
pero el cliente se reloguea solo (tiene las credenciales).

------------------------------------------------------------------------
PASO 2: LEVANTAR EL API SERVER (OPCIONAL)
------------------------------------------------------------------------

Esto corre un servidor HTTP en 127.0.0.1:9180 para que otros
servicios en el mismo servidor consulten sin importar Python.

  cd /root/solucionese\ richi
  python3 api_server.py &

Para mantenerlo corriendo aunque cierres la terminal:

  nohup python3 api_server.py > api_server.log 2>&1 &

Verificar que esta vivo:

  curl http://127.0.0.1:9180/persona/48213083

------------------------------------------------------------------------
PASO 3: CONSULTAS INDIVIDUALES (3 formas)
------------------------------------------------------------------------

FORMA A - Via el API server (cualquier lenguaje):

  curl http://127.0.0.1:9180/persona/48213083
  curl http://127.0.0.1:9180/sbs/48213083
  curl http://127.0.0.1:9180/placa/ABC123
  curl http://127.0.0.1:9180/ruc/20123456789
  curl http://127.0.0.1:9180/licencia/48213083
  curl http://127.0.0.1:9180/telefono/999888777
  curl http://127.0.0.1:9180/afp/48213083
  curl http://127.0.0.1:9180/rcc/48213083
  curl http://127.0.0.1:9180/soat/ABC123
  curl http://127.0.0.1:9180/nombre/firstName=JUAN

  Todos devuelven JSON plano (ya descifrado).

FORMA B - Directo en Python (script rapido):

  python3 -c "
from tacto_client import TACTO
import json
api = TACTO(token_file='tacto_token.json')
r = api.get_person('48213083')
print(json.dumps(r, indent=2, ensure_ascii=False))
  "

FORMA C - Carga masiva por CSV:

  python3 -c "
from tacto_client import TACTO
api = TACTO(token_file='tacto_token.json')
resp = api.massive_upload('/ruta/dnis.csv', 'personas')
with open('resultado.xlsx', 'wb') as f:
    f.write(resp.content)
print('Descargado resultado.xlsx')
  "

------------------------------------------------------------------------
PASO 4: CONSULTAR MULTIPLES DOCUMENTOS (sin pausas)
------------------------------------------------------------------------

No hay limite de 15 segundos via API directa. Puedes consultar
todos los que quieras en bucle:

  python3 -c "
from tacto_client import TACTO
api = TACTO(token_file='tacto_token.json')
for dni in ['48213083','40825702','45647771']:
    r = api.get_person(dni)
    print(r['person']['fullName'], '-', r['person'].get('address',''))
"

------------------------------------------------------------------------
PASO 5: GUARDAR TOKEN TRAS CADA SESION
------------------------------------------------------------------------

  api.save_token()   # Actualiza tacto_token.json

Esto se hace automaticamente en el API server si lo usas,
pero si importas el modulo manualmente, llamalo al final.

------------------------------------------------------------------------
DIAGRAMA DE ARQUITECTURA
------------------------------------------------------------------------

  tacto.ucvox.com  (API remota)
       ^
       | HTTPS (AES-256-GCM + JWT)
       |
  207.244.230.123  (servidor actual)
       |
       |--- tacto_client.py (libreria Python, maneja cifrado/auth)
       |
       |--- api_server.py  (bridge HTTP -> 127.0.0.1:9180)
       |       |
       |       |--- curl / PHP / Node / Go -> http://127.0.0.1:9180/persona/...
       |
       |--- scripts Python directos (import tacto_client)

Los otros servicios en el mismo servidor consultan via
http://127.0.0.1:9180/ y obtienen JSON ya descifrado.

------------------------------------------------------------------------
SI EL TOKEN EXPIRA
------------------------------------------------------------------------

No pasa nada. El cliente:
  1. Detecta 401
  2. Intenta refresh con refresh_token
  3. Si falla, hace login automatico con user/pass guardados
Todo automatico, sin intervencion.

------------------------------------------------------------------------
ARCHIVOS
------------------------------------------------------------------------

  /root/solucionese richi/
    tacto_client.py   - Libreria principal (no tocar)
    api_server.py     - Servidor HTTP bridge
    tacto_token.json  - Token activo
    endpoints.txt     - Referencia de endpoints
    README.md         - Documentacion completa
