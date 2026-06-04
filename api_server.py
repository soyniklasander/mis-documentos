# Servidor HTTP local para que otros servicios del mismo servidor
# consulten TACTO sin importar el modulo Python directamente.
# Escucha en 127.0.0.1:9180, responde JSON plano (ya descifrado).
#
# Uso: python3 api_server.py &
# Consultar: curl http://127.0.0.1:9180/persona/48213083
#            curl http://127.0.0.1:9180/ruc/20123456789
#            curl http://127.0.0.1:9180/placa/ABC123

import http.server
import json
import os
import sys
from urllib.parse import urlparse

from tacto_client import TACTO

DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(DIR, 'tacto_token.json')
ENV_FILE = os.path.join(DIR, '.env')
PORT = 9180
HOST = '127.0.0.1'

# Cargar credenciales desde .env si existe
email = os.environ.get('TACTO_EMAIL')
password = os.environ.get('TACTO_PASSWORD')
if not email and os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        if '=' in line:
            k, v = line.strip().split('=', 1)
            if k == 'TACTO_EMAIL': email = v
            if k == 'TACTO_PASSWORD': password = v

api = TACTO(email, password, token_file=TOKEN_FILE)

ROUTES = {
    'persona':  lambda p: api.get_person(p),
    'sbs':      lambda p: api.get_sbs(p),
    'afp':      lambda p: api.get_afp(p),
    'rcc':      lambda p: api.get_rcc(p),
    'ruc':      lambda p: api.get_sunat(p),
    'placa':    lambda p: api.get_plate(p),
    'soat':     lambda p: api.get_soat(p),
    'licencia': lambda p: api.get_licence(p),
    'telefono': lambda p: api.get_phone(p),
    'nombre':   lambda p: api.search_name(dict(q.split('=') for q in p.split('&') if '=' in q)),
}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path.strip('/')
        parts = path.split('/', 1)
        key = parts[0]
        param = parts[1] if len(parts) > 1 else ''

        if key not in ROUTES:
            self._json({'error': 'endpoint no valido', 'rutas': list(ROUTES.keys())}, 404)
            return
        try:
            data = ROUTES[key](param)
            # Guardar token por si hubo refresh
            api.save_token(TOKEN_FILE)
            self._json(data)
        except Exception as e:
            self._json({'error': str(e)}, 500)

    def _json(self, obj, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False, default=str).encode())

    def log_message(self, fmt, *args):
        sys.stderr.write(f'[TACTO API] {args[0]} {args[1]} {args[2]}\n')


if __name__ == '__main__':
    server = http.server.HTTPServer((HOST, PORT), Handler)
    print(f'TACTO API server on http://{HOST}:{PORT}')
    print(f'Endpoints: {", ".join(ROUTES.keys())}')
    server.serve_forever()
