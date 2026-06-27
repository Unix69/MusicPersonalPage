from datetime import datetime
from flask import ( 
    Request, jsonify, make_response, request, Response    
)


# --- Cookies ---
class Cookie:
    def __init__(self, name, value, essential=True):
        self.name = name
        self.value = value
        self.essential = essential
        self.timestamp = datetime.utcnow().isoformat()

    def serialize(self):
        return {
            "name": self.name,
            "value": self.value,
            "essential": self.essential,
            "timestamp": self.timestamp
        }


class CookieSupporter:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.register_routes(app)

    def save(self, response: Response, cookie: Cookie):
        if not response:
            response = make_response()
        response.set_cookie(cookie.name, cookie.value, max_age=60 * 60 * 24 * 365)
        print("response")
        print(str(response))
        return response
    
    def delete(self, response: Response, cookie_name: str):
        if not response:
            self.response = make_response()
        # scaduto
        response.set_cookie(cookie_name, "", expires=0)
        print("response")
        print(str(response))

        return response

    def verify(self, cookie_name):
        return request.cookies.get(cookie_name)
    
    def compute_cookie_value(self, request: Request):
        ip = request.remote_addr
        port = request.environ.get("REMOTE_PORT")
        return f"{ip}:{port}:{datetime.utcnow().isoformat()}"

    def set_essentials_cookies(self, response: Response, request: Request):
        ip = request.remote_addr
        port = request.environ.get("REMOTE_PORT")
        value = f"{ip}:{port}:{datetime.utcnow().isoformat()}"
        cookie = Cookie("essential_cookie", value, essential=True)
        return self.save(response=response, cookie=cookie)

    def set_not_essentials_cookies(self, response: Response, request: Request):
        ip = request.remote_addr
        port = request.environ.get("REMOTE_PORT")
        value = f"{ip}:{port}:{datetime.utcnow().isoformat()}"
        cookie = Cookie("not_essential_cookie", value, essential=False)
        return self.save(response=response, cookie=cookie)
    
    def unset_essentials_cookies(self, response: Response):
        return self.delete(response=response, cookie_name="essential_cookie")

    def unset_not_essentials_cookies(self, response: Response):
        return self.delete(response=response, cookie_name="not_essential_cookie")
    
    def get_essential(self):
        return request.cookies.get("essential_cookie")

    def get_not_essential(self):
        return request.cookies.get("not_essential_cookie")

    def register_routes(self, app):
        @app.route("/set_cookie", methods=["POST"])
        def set_cookie():
            print("Ciaoooo")
            data = request.json
            essential = data.get("essential", False)
            not_essential = data.get("not_essential", False)

            response=make_response(jsonify({"status": "ok"}))

            # Se accetta gli essential
            if essential:
                self.set_essentials_cookies(response, request)
            else:
                self.unset_essentials_cookies(response)

            # Se accetta i non essential
            if not_essential:
                self.set_not_essentials_cookies(response, request)
            else:
                self.unset_not_essentials_cookies(response)

            return response

