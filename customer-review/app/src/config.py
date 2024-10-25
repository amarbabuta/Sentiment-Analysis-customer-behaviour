import logging
import os
from pathlib import Path
from typing import Union

from pydantic import BaseSettings, root_validator, validator

_AUTHORIZED_VALUES = {"test_api_server_type": ["test_starlette", "local", "cloud_run"]}


class Settings(BaseSettings):
    environment_name: str
    log_level: Union[str, int]
    log_format: str
    test_api_server_type: str
    test_api_server_url: str = ""
    gcp_service_account_file: str = ""
    default_csv_separator: str = ","

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("test_api_server_type", allow_reuse=True)
    def test_api_server_type_must_be_in_authorized_values(cls, value):
        authorized_values = _AUTHORIZED_VALUES["test_api_server_type"]

        if value is None:
            raise ValueError("test_api_server_type cannot be None")

        elif value not in authorized_values:
            raise ValueError(
                "test_api_server_type not supported : "
                + value
                + " - authorized_values are : "
                + ",".join(authorized_values)
            )
        else:
            return value

    @root_validator
    def check_test_api_server_url(cls, values):
        server_type = values.get("test_api_server_type")
        api_url = values.get("test_api_server_url")
        if server_type in ["local", "cloud_run"] and api_url is None:
            raise ValueError(
                "test_api_server_url could not be None with server_type : "
                + server_type
            )

        return values


DEFAULT_ENV_FILE_PATH = "app/config/default.env"


def define_env_file_path_to_use(default_env_file_path: str = DEFAULT_ENV_FILE_PATH):
    if "ENVIRONMENT_NAME" not in os.environ:
        print(
            f"ENVIRONMENT_NAME not set in os.environ - "
            f"using default_env_file : {default_env_file_path}"
        )
        return default_env_file_path

    else:
        environment_name = os.environ["ENVIRONMENT_NAME"]
        env_file_path_as_string = f"app/config/{environment_name}.env"
        env_file_path = Path(env_file_path_as_string)
        if not env_file_path.is_file():
            print(
                f"env_file {env_file_path_as_string} "
                f"corresponding to ENVIRONMENT_NAME in os.environ not found"
                f"- using default_env_file : {default_env_file_path}"
            )
            return default_env_file_path
        else:
            print(
                f"ENVIRONMENT_NAME in os.environ set to"
                f" {os.environ['ENVIRONMENT_NAME']}"
                f" - using env_file : {env_file_path_as_string}"
            )
            return env_file_path_as_string


env_file_path_to_use = define_env_file_path_to_use()
SETTINGS = Settings(_env_file=env_file_path_to_use)
logging.basicConfig(level=SETTINGS.log_level, format=SETTINGS.log_format)
logging.info("environment settings : " + SETTINGS.json())
