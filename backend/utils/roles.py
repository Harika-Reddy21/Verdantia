from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
def roles_required(*roles):
    def dec(fn):
        @wraps(fn)
        @jwt_required()
        def wrap(*a, **k):
            if get_jwt().get("role") not in roles: return jsonify(error="forbidden"),403
            return fn(*a, **k)
        return wrap
    return dec