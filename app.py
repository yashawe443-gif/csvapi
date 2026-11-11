
import os
import csv
import requests
from io import TextIOWrapper
from flask import Flask, request, jsonify

app = Flask(__name__)

# Google Drive public CSV file ID
DRIVE_FILE_ID = os.environ.get("DRIVE_FILE_ID", "")

# CSV ka first column number hai
NUMBER_COLUMN = os.environ.get("NUMBER_COLUMN", "number")

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "CSV Search API is running"
    })

@app.route("/api/search")
def search():
    number = request.args.get("number", "").strip()

    if not number:
        return jsonify({
            "status": "error",
            "message": "Number parameter required"
        }), 400

    if not DRIVE_FILE_ID:
        return jsonify({
            "status": "error",
            "message": "Drive file ID not configured"
        }), 500

    url = (
        "https://drive.google.com/uc"
        f"?export=download&id={DRIVE_FILE_ID}"
    )

    try:
        response = requests.get(
            url,
            stream=True,
            timeout=(20, 180)
        )
        response.raise_for_status()

        reader = csv.DictReader(
            TextIOWrapper(
                response.raw,
                encoding="utf-8-sig",
                newline=""
            )
        )

        # Only return non-personal synthetic test records.
        for row in reader:
            if row.get(NUMBER_COLUMN, "").strip() == number:
                return jsonify({
                    "status": "success",
                    "data": row
                })

        return jsonify({
            "status": "not_found",
            "message": "Record not found"
        }), 404

    except Exception:
        return jsonify({
            "status": "error",
            "message": "CSV could not be read"
        }), 502

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
