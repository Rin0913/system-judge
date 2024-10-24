from functools import wraps
from flask import Flask, request, jsonify, abort, g, current_app

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authorization_header = request.headers.get("Authorization")
        if authorization_header:
            token = authorization_header.replace('Bearer ', '', 1)
            g.user = current_app.auth_service.authenticate_token(token)
        return f(*args, **kwargs)
    return decorated_function

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            abort(401)
        token = authorization_header.replace('Bearer ', '', 1)
        user = current_app.auth_service.authenticate_token(token)
        if user is None:
            abort(401)
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (not hasattr(g, 'user')) or  g.user is None:
            abort(401)
        if 'role' not in g.user or g.user['role'] != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def require_development_environment(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.runtime_environment == "Development":
            return f(*args, **kwargs)
        abort(404)
    return decorated_function
