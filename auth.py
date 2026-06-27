
from functools import wraps
from flask import Response, request


class AdminAuthenticator:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def check_auth(self, username, password):
        return username == self.username and password == self.password

    def authenticate(self):
        return Response(
            'Access denied', 401,
            {'WWW-Authenticate': 'Basic realm="Permission Deined"'}
        )

    def requires_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not self.check_auth(auth.username, auth.password):
                return self.authenticate()
            return f(*args, **kwargs)
        return decorated
