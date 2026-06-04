# TACTO API Client

Cliente Python para automatizar consultas en TACTO (uCVox) sin intervencion manual del navegador.
Disenado para correr desde servidores con IP autorizada y servir a otros servicios internos.

## Requisitos

- Python 3.8+
- `pip install requests cryptography`

## Arquitectura

TACTO implementa tres capas de seguridad:

- **Cifrado AES-256-GCM** con clave derivada de SHA-256 de la semilla `T@ct0_Px2026!#Zx$`
- **Token JWT** via `Authorization: Bearer <token>` en cada request
- **Refresh token** para renovacion automatica sin re-login

Los endpoints reales de la API NO son los que aparecen en las rutas del frontend.
Las rutas reales se descubrieron analizando los chunks de JS del frontend:

| Categoria | Base URL | Cliente |
|-----------|----------|---------|
| Personas | `/api/query/` | Encriptado (respuesta) |
| Otros (placas, SOAT, licencias) | `/api/other/` | Encriptado (respuesta) |
| Empresas/RUC | `/api/company/` | Encriptado (respuesta) |
| RCC | `/api/rcc/` | Encriptado (respuesta) |
| Archivos | `/files/` | Encriptado (respuesta) |
| Auth | `/auth/auth/` | Encriptado (request y response) |

## Uso rapido

### Login y consulta individual

```bash
python3 tacto_client.py usuario@correo.com "MiPassword" 12345678
```

### Reutilizar token sin loguear cada vez

```python
from tacto_client import TACTO
import json

api = TACTO(token_file='tacto_token.json')

# Consultar persona por DNI
r = api.get_person('48213083')
print(json.dumps(r, indent=2, ensure_ascii=False))

# Guardar token actualizado (refresh automatico)
api.save_token()
```

### Login explicito (primera vez o token expirado)

```python
api = TACTO('usuario@correo.com', 'MiPassword')
api.save_token('tacto_token.json')
```

## Metodos disponibles

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| `get_person(doc)` | `GET /api/query/getPerson/{doc}` | Datos de persona por DNI/CE/Pasaporte |
| `get_sbs(doc)` | `GET /api/query/getSbs/{doc}/0` | Historial SBS (crediticio) |
| `get_afp(doc)` | `GET /api/query/getAfp/{doc}` | Datos AFP |
| `get_rcc(doc)` | `GET /api/rcc/getRccData/{doc}` | Reporte RCC |
| `get_sunat(ruc)` | `GET /api/company/getSunat/{ruc}` | Datos SUNAT por RUC |
| `get_plate(placa)` | `GET /api/other/getSunarpPlate/{placa}` | Datos vehiculares por placa |
| `get_soat(placa)` | `GET /api/other/getSoatPlate/{placa}` | Consulta SOAT |
| `get_licence(licencia)` | `GET /api/other/getLicence/{licencia}` | Licencia de conducir |
| `get_phone(telefono)` | `GET /api/query/getByPhone/{telefono}` | Busqueda por numero telefonico |
| `search_name(params)` | `GET /files/people/getAll` | Busqueda por nombre (query params) |
| `massive_upload(file, tipo)` | `POST /files/Masive/upload*` | Carga masiva por archivo CSV |
| `save_token(path)` | - | Persiste el token a disco |

### Carga masiva

```python
api = TACTO(token_file='tacto_token.json')

# Tipos: 'personas', 'telefonos', 'ruc'
resp = api.massive_upload('documentos.csv', 'personas')
with open('resultado.xlsx', 'wb') as f:
    f.write(resp.content)
```

El CSV debe tener una columna con los identificadores (DNI 8 digitos, RUC 11 digitos, telefonos 9-12 digitos).

## Manejo automatico de sesion

El flujo de autenticacion es completamente automatico:

1. Al crear la instancia, carga el token guardado o hace login
2. Cada request incluye `Authorization: Bearer <token>`, `id` y `cid`
3. Si el servidor responde 401, intenta refresh con `refresh_token`
4. Si el refresh falla, hace login automatico con las credenciales guardadas
5. Si no hay credenciales, lanza excepcion

No requiere intervencion manual nunca.

## Notas

- El cifrado AES-GCM usa un IV aleatorio de 12 bytes en cada request (autenticacion y confidencialidad)
- El token se almacena en texto plano en `tacto_token.json`. Proteger este archivo.
- Las respuestas de la API vienen cifradas con AES-GCM. El cliente las descifra automaticamente.
- Los requests GET no se cifran (solo los POST/PUT llevan body cifrado)
- La IP del servidor debe estar en la lista blanca del usuario (`allowedIp` en el perfil)
- No hay restriccion de 15 segundos entre consultas via API directa (ese limite solo aplica en la interfaz web)
