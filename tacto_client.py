import hashlib
import base64
import json
import os
import time
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class TACTO:
    KEY_STRING = "T@ct0_Px2026!#Zx$"
    AUTH_BASE = "https://tacto.ucvox.com/auth/auth"
    API_BASE = "https://tacto.ucvox.com/api"
    FILES_BASE = "https://tacto.ucvox.com/files"

    def __init__(self, email=None, password=None, token_file=None):
        self.s = requests.Session()
        self._derive_key()
        self.token = None
        self.refresh_token = None
        self.user = None
        self._login_time = None
        self._email = email
        self._password = password
        if token_file and os.path.exists(token_file):
            self._load_token(token_file)
        if email and password and not self.token:
            self.login(email, password)

    def _derive_key(self):
        self._key = hashlib.sha256(self.KEY_STRING.encode()).digest()

    def _encrypt(self, data):
        if isinstance(data, (dict, list)):
            data = json.dumps(data, separators=(',', ':')).encode()
        elif isinstance(data, str):
            data = data.encode()
        iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(self._key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ct = encryptor.update(data) + encryptor.finalize()
        raw = iv + ct + encryptor.tag
        return base64.b64encode(raw).decode()

    def _decrypt(self, data_b64):
        raw = base64.b64decode(data_b64)
        iv = raw[:12]
        tag = raw[-16:]
        ct = raw[12:-16]
        cipher = Cipher(algorithms.AES(self._key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        return json.loads(decryptor.update(ct) + decryptor.finalize())

    def _auth_headers(self):
        h = {}
        if self.token:
            h['Authorization'] = f'Bearer {self.token}'
        if self.user:
            uid = self.user.get('_id') or self.user.get('id', '')
            cid = self.user.get('companyId', '')
            if uid:
                h['id'] = uid
            if cid:
                h['cid'] = cid
        return h

    def _ensure_auth(self):
        if self.token:
            return True
        if self._email and self._password:
            self.login(self._email, self._password)
            return True
        return False

    def _request_raw(self, method, url, **kwargs):
        self._ensure_auth()
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_headers())
        resp = self.s.request(method, url, headers=headers, **kwargs)
        if resp.status_code == 401:
            if not self._refresh():
                if self._email and self._password:
                    self.login(self._email, self._password)
                else:
                    raise Exception("Session expired and no credentials for re-login")
            headers.update(self._auth_headers())
            resp = self.s.request(method, url, headers=headers, **kwargs)
        return resp

    def _request_encrypted(self, method, url, data=None, **kwargs):
        self._ensure_auth()
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_headers())
        if data is not None:
            payload = {'data': self._encrypt(data)}
        else:
            payload = None
        resp = self.s.request(method, url, headers=headers, json=payload, **kwargs)
        if resp.status_code == 401:
            if not self._refresh():
                if self._email and self._password:
                    self.login(self._email, self._password)
                else:
                    raise Exception("Session expired and no credentials for re-login")
            headers.update(self._auth_headers())
            payload = {'data': self._encrypt(data)} if data is not None else None
            resp = self.s.request(method, url, headers=headers, json=payload, **kwargs)
        j = resp.json()
        if isinstance(j.get('data'), str):
            return self._decrypt(j['data'])
        return j

    def login(self, email, password):
        payload = {'email': email, 'passwordPlain': password}
        data = {'data': self._encrypt(payload)}
        resp = self.s.post(f'{self.AUTH_BASE}/login', json=data)
        j = resp.json()
        result = self._decrypt(j['data'])
        self.token = result['token']
        self.refresh_token = result.get('refresh_token')
        self.user = result['user']
        self._login_time = time.time()
        if result.get('changePassword'):
            raise Exception("changePassword required")
        return result

    def _refresh(self):
        if not self.refresh_token:
            return False
        try:
            payload = {'refresh_token': self.refresh_token}
            data = {'data': self._encrypt(payload)}
            resp = self.s.post(f'{self.AUTH_BASE}/refreshToken', json=data)
            if resp.status_code != 200:
                return False
            j = resp.json()
            result = self._decrypt(j['data'])
            self.token = result['token']
            self.refresh_token = result.get('refresh_token')
            self._login_time = time.time()
            return True
        except Exception:
            return False

    def save_token(self, path='tacto_token.json'):
        with open(path, 'w') as f:
            json.dump({
                'token': self.token,
                'refresh_token': self.refresh_token,
                'user': self.user,
                'login_time': self._login_time,
            }, f)

    def _load_token(self, path):
        with open(path) as f:
            d = json.load(f)
        self.token = d.get('token')
        self.refresh_token = d.get('refresh_token')
        self.user = d.get('user')
        self._login_time = d.get('login_time')

    def _request_decrypt(self, method, url, **kwargs):
        self._ensure_auth()
        headers = kwargs.pop('headers', {})
        headers.update(self._auth_headers())
        resp = self.s.request(method, url, headers=headers, **kwargs)
        if resp.status_code == 401:
            if not self._refresh():
                if self._email and self._password:
                    self.login(self._email, self._password)
                else:
                    raise Exception("Session expired and no credentials for re-login")
            headers.update(self._auth_headers())
            resp = self.s.request(method, url, headers=headers, **kwargs)
        j = resp.json()
        if isinstance(j.get('data'), str):
            return self._decrypt(j['data'])
        return j

    def get_person(self, doc):
        return self._request_decrypt('GET', f'{self.API_BASE}/query/getPerson/{doc}')

    def get_sbs(self, doc):
        return self._request_decrypt('GET', f'{self.API_BASE}/query/getSbs/{doc}/0')

    def get_afp(self, doc):
        return self._request_decrypt('GET', f'{self.API_BASE}/query/getAfp/{doc}')

    def get_phone(self, phone):
        return self._request_decrypt('GET', f'{self.API_BASE}/query/getByPhone/{phone}')

    def get_plate(self, plate):
        return self._request_decrypt('GET', f'{self.API_BASE}/other/getSunarpPlate/{plate}')

    def get_licence(self, licence):
        return self._request_decrypt('GET', f'{self.API_BASE}/other/getLicence/{licence}')

    def get_soat(self, plate):
        return self._request_decrypt('GET', f'{self.API_BASE}/other/getSoatPlate/{plate}')

    def get_sunat(self, ruc):
        return self._request_decrypt('GET', f'{self.API_BASE}/company/getSunat/{ruc}')

    def get_rcc(self, doc):
        return self._request_decrypt('GET', f'{self.API_BASE}/rcc/getRccData/{doc}')

    def search_name(self, params):
        headers = self._auth_headers()
        resp = self.s.get(f'{self.FILES_BASE}/people/getAll', headers=headers, params=params)
        j = resp.json()
        if isinstance(j.get('data'), str):
            return self._decrypt(j['data'])
        return j

    # === Massive file upload ===
    def massive_upload(self, file_path, query_type='personas'):
        endpoints = {
            'personas': '/Masive/upload',
            'telefonos': '/Masive/uploadPhones',
            'ruc': '/Masive/uploadCompany',
        }
        if query_type not in endpoints:
            raise ValueError(f"Invalid query_type. Options: {list(endpoints.keys())}")
        url = f'{self.FILES_BASE}{endpoints[query_type]}'
        headers = self._auth_headers()
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            resp = self.s.post(url, headers=headers, files=files)
        return resp


if __name__ == '__main__':
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ")
    pwd = sys.argv[2] if len(sys.argv) > 2 else input("Password: ")
    api = TACTO(email, pwd)
    print("Login OK.")
    api.save_token()
    print("Token saved to tacto_token.json")
    doc = sys.argv[3] if len(sys.argv) > 3 else input("DNI to query: ")
    if doc:
        r = api.get_person(doc)
        print(json.dumps(r, indent=2, ensure_ascii=False))
