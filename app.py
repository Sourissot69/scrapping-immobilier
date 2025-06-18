from flask import Flask, request, jsonify
from scraper_leboncoin_visible import main as run_scraper   # adapte si ton entry-point diffère

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok")

@app.route("/scrape", methods=["POST"])
def scrape():
    params = request.get_json(force=True)  # { "ville": "Marseille", ... }
    try:
        run_scraper(**params)              # lance le scraper avec les mêmes options que CLI
        return jsonify(status="done"), 202
    except Exception as e:
        return jsonify(error=str(e)), 400
