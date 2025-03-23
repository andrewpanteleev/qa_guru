import os


class Server:
    def __init__(self, env):
        # Загружаем базовый URL для микросервиса из переменных окружения или используем значения по умолчанию
        self.reqres = {
            "dev": os.getenv("APP_URL", "http://localhost:8002"),
            "beta": os.getenv("BETA_URL", "http://beta-api.example.com"),
            "rc": os.getenv("RC_URL", "https://reqres.in"),
        }[env]
        self.ninjacats = {
            "dev": "",
            "beta": "",
            "rc": "https://ninjactas.com",
        }[env]