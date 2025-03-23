from app.utils.base_session import BaseSession
from config import Server

class User:
    def __init__(self, **kwargs):
        json_ = kwargs.pop("json", {})
        self._email = kwargs.pop("email", None)
        self._first_name = kwargs.pop("first_name", None)
        self._last_name = kwargs.pop("last_name", None)
        self._avatar = kwargs.pop("avatar", None)
        self._json = json_ if json_ else {
            "email": self._email,
            "first_name": self._first_name,
            "last_name": self._last_name,
            "avatar": self._avatar,
        }
    @property
    def email(self):
        return self._json["email"]
    @property
    def first_name(self):
        return self._json["first_name"]
    @property
    def last_name(self):
        return self._json["last_name"]
    @property
    def avatar(self):
        return self._json["avatar"]


class ResponseUser:
    def __init__(self, **kwargs):
        json_ = kwargs.pop("json", {})
        self._id = kwargs.pop("id", 2)
        self._email = kwargs.pop("email", "janet.weaver@reqres.in")
        self._first_name = kwargs.pop("first_name", "Janet")
        self._last_name = kwargs.pop("last_name", "Weaver")
        self._avatar = kwargs.pop("avatar", "https://reqres.in/img/faces/2-image.jpg")
        self._json = json_ if json_ else {
            "id": self._id,
            "email": self._email,
            "first_name": self._first_name,
            "last_name": self._last_name,
            "avatar": self._avatar,
        }

    @property
    def json(self):
        return self._json


class ResponseGetUser:
    def __init__(self, **kwargs):
        response = kwargs.pop("response", None)
        json_ = kwargs.pop("json", response.json() if response else None)
        self._data = kwargs.pop("data", ResponseUser()).json
        self._json = json_ if json_ else {
            "data": self._data,
            "support": {
                "url": "https://reqres.in/#support-heading",
                "text": "To keep ReqRes free, contributions towards server costs are appreciated!"
            }
        }

    @property
    def json(self):
        return self._json


class Reqres:
    def __init__(self, env):
        self.session = BaseSession(base_url=Server(env).reqres)

    def get_user(self, user_id: int):
        return self.session.get(f"/api/users/{user_id}")

    def get_user_for_test(self, user_id: int):
        return self.session.get(f"/api/users/{user_id}")

    def get_users(self, page=None, size=None):
        params = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        return self.session.get("/api/users", params=params)

    def get_users_for_pagination(self, data: dict):
        return self.session.get("/api/users/", params=data)

    def create_user(self, user: dict):
        return self.session.post("/api/users/", json=user)

    def update_user(self, user_id: int, data: dict = None):
        return self.session.patch(f"/api/users/{user_id}", json=data)

    def delete_user(self, user_id: int):
        return self.session.delete(f"/api/users/{user_id}")

    def create_user_wrong_method(self, user: dict):
        return self.session.patch("/api/users/", json=user)

    def get_status(self):
        return self.session.get("/status")

    def put(self, path):
        return self.session.put(path)
        
    def delete(self, path):
        return self.session.delete(path)
        
    def patch(self, path):
        return self.session.patch(path)