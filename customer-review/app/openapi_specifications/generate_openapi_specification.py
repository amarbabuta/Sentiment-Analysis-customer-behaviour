import json
from typing import Any, Dict

from fastapi import FastAPI

from app.main import app

_OPENAPI_SPECIFICATIONS_FOLDER_PATH = "app/openapi_specifications/"


def get_openapi_specification(app: FastAPI) -> Dict[str, Any]:
    return app.openapi()


def update_openapi_json(app: FastAPI):
    file_path = (
        _OPENAPI_SPECIFICATIONS_FOLDER_PATH
        + app.title
        + "_"
        + app.version
        + "_openapi.json"
    )

    with open(file_path, "w") as file:
        json.dump(get_openapi_specification(app=app), file, indent=2)


if __name__ == "__main__":
    update_openapi_json(app=app)
