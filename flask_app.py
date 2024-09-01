from flask import Flask

host = '0.0.0.0'
port = 5000
name = "TuneTransfer"


class FlaskApp:
    def __init__(self):
        self.flask_app = Flask(name)
        self.create_flask_app_routes()

    def create_flask_app_routes(self):
        @self.flask_app.route("/")
        def hello():
            ...

        return self.flask_app.run(host=host, port=port)