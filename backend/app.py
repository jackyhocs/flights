import os
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

from skypath.data_loader import load_dataset
from skypath.graph import build_graph
from skypath.routes import bp

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_DATASET_PATH = Path(os.environ.get("FLIGHTS_DATASET_PATH", REPO_ROOT / "flights.json"))


def create_app(dataset_path=DEFAULT_DATASET_PATH):
    app = Flask(__name__)
    CORS(app)

    airports, flights = load_dataset(dataset_path)
    app.config["AIRPORTS"] = airports
    app.config["FLIGHT_GRAPH"] = build_graph(flights)

    app.register_blueprint(bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
