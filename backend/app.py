from flask import Flask
from flask_cors import CORS
from auth_routes import auth

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth, url_prefix='/api/auth')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
