from pathlib import Path
from flask import Flask
from database import init_db, seed_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "quickeats-development-secret-key"
    app.config["DATABASE"] = str(Path(app.instance_path) / "quickeats.db")

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_db(app.config["DATABASE"])

    from routes import register_routes
    register_routes(app)

    with app.app_context():
        seed_db(app.config["DATABASE"])

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
