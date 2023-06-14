import json
from urllib.request import urlopen
from flask import request
from functools import wraps
from jose import jwt


AUTH0_DOMAIN = ""
ALGORITHMS = []
API_AUDIENCE = ""


"""
AuthError Exception
"""


class AuthError(Exception):
    def __init__(self, error: dict, status_code: int):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    auth_header = request.headers['Authentication']

    if not auth_header:
        raise AuthError({
            "error": "Authentication Error",
            "description": "Missing authentication header."
        }, 401)

    header_parts = auth_header.split(" ")

    if len(header_parts) != 2:
        raise AuthError({
            "error": "Authentication Error",
            "description": "Malformed Authentication Header."
        }, 401)
    elif header_parts[0] != "bearer":
        raise AuthError({
            "error": "Authentication Error",
            "description": "Malformed Authentication Header."
        }, 401)

    return header_parts[1]


def check_permission(permission: str, payload: dict) -> bool:
    if "permissions" not in payload:
        raise AuthError({
            "error": "Authentication Error",
            "description": "Malformed Authentication Header."
        }, 401)

    if permission not in payload["permissions"]:
        raise AuthError({
            "error": "Authentication Error",
            "description": "Malformed Authentication Header."
        }, 401)

    return True


def verify_decode_jwt(token: str):
    json_url = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.load(json_url.read())
    jwt_header = jwt.get_unverified_header(token)

    if "kid" not in jwt_header:
        raise AuthError({
            "error": "Authorization Error",
            "description": "Malformed token."
        }, 401)

    rsa_key = {}

    for key in jwks:
        if key["kid"] == jwt_header["kid"]:
            rsa_key = {
                "kid": key["kid"],
                "kty": key["kty"],
                "n": key["n"],
                "e": key["e"]
            }

    if rsa_key:
        try:
            payload = jwt.decode(token,
                                 key=rsa_key,
                                 algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer=f"https://{AUTH0_DOMAIN}"
                                 )

            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                "code": "token_expired",
                "description": "Your authorization time has been reached, authorize again."
            }, 401)
        
        except jwt.JWTClaimsError:
            raise AuthError({
                "code": "invalid_claims",
                "description": "Invalid Claims."
            }, 401)
        except Exception:
            raise AuthError({
                "code": "invalid_header",
                "description": "Invalid Header."
            }, 401)

    raise AuthError({
        "code": "invalid_header",
        "description": "Invalid Header."
    }, 401)


def require_auth(permission=""):
    def require_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permission(permission, payload)

            return f(payload, *args, **kwargs)

        return wrapper

    return require_auth_decorator
