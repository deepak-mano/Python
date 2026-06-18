from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, request

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from address_validator import validate_canadian_address
else:
    from .address_validator import validate_canadian_address


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.post("/validate")
    def validate_address() -> tuple[dict[str, object], int]:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return {"error": "Request body must be valid JSON."}, 400

        required_fields = ["line1", "city", "province", "postal_code"]
        missing_fields = [field for field in required_fields if not str(payload.get(field, "")).strip()]
        if missing_fields:
            return {"error": "Missing required fields.", "missing_fields": missing_fields}, 400

        result = validate_canadian_address(
            line1=str(payload.get("line1", "")),
            line2=str(payload.get("line2", "")),
            city=str(payload.get("city", "")),
            province=str(payload.get("province", "")),
            postal_code=str(payload.get("postal_code", "")),
        )

        response = {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "normalized_address": result.normalized_address,
        }
        return response, 200 if result.is_valid else 400

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
