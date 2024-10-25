import json
import logging
from typing import Optional, Union

from pydantic import BaseModel, root_validator, validator
from starlette.testclient import TestClient

from app.main import app
from app.src.utils.api_clients.gcp_services_client import GcpServicesClient
from app.src.utils.api_clients.generic_api_client import GenericApiClient
from app.tests.helpers.case_handlers import compare_outputs_and_expected_outputs

_AUTHORIZED_VALUES = {"api_server_type": ["test_starlette", "local", "cloud_run"]}


class ApiSettings(BaseModel):
    api_server_type: str
    api_server_url: str
    gcp_service_account_file: Optional[str]

    @validator("api_server_type", allow_reuse=True)
    def api_server_type_must_be_in_authorized_values(cls, value):
        authorized_values = _AUTHORIZED_VALUES["api_server_type"]

        if value is None:
            raise ValueError("api_server_type cannot be None")

        elif value not in authorized_values:
            raise ValueError(
                "api_server_type not supported : "
                + value
                + " - authorized_values are : "
                + ",".join(authorized_values)
            )
        else:
            return value

    @root_validator
    def check_api_url(cls, values):
        api_server_type = values.get("api_server_type")
        api_server_url = values.get("api_server_url")
        if api_server_type in ["local", "cloud_run"] and api_server_url is None:
            raise ValueError(
                "api_server_url could not be None with server_type : " + api_server_type
            )

        return values


def set_api_client(
    settings_api: ApiSettings,
) -> GenericApiClient:
    if settings_api.api_server_type == "test_starlette":

        api_client = GenericApiClient(
            api_server_url=settings_api.api_server_url,
            api_server_type=settings_api.api_server_type,
        )
        api_client.session = TestClient(app)

    elif settings_api.api_server_type == "local":

        api_client = GenericApiClient(
            api_server_url=settings_api.api_server_url,
            api_server_type=settings_api.api_server_type,
            read_timeout=200,
        )

    elif settings_api.api_server_type == "cloud_run":

        if settings_api.api_server_url is None:
            raise ValueError(
                "api_url cannot be None with server_type="
                + settings_api.api_server_type
            )

        else:
            api_client = GcpServicesClient(
                api_server_url=settings_api.api_server_url,
                api_server_type=settings_api.api_server_type,
                connect_timeout=100,
                read_timeout=300,
            )

    else:
        raise ValueError("server_type not supported : " + settings_api.api_server_type)

    return api_client


def check_api_service(
    api_client: GenericApiClient,
    endpoint_path: str,
    method: str = "post",
    request_body: Union[dict, None] = None,
    expected_outputs: Union[dict, None] = None,
    compare_only_keys_in_expected_outputs: bool = False,
):
    # TODO handle other methods than post
    # TODO maybe check for status_code

    if method == "post":

        response = api_client.post(
            endpoint_path=endpoint_path,
            data=request_body,
        )

        if response.status_code == 200:
            outputs = response.content_as_json
            compare_outputs_and_expected_outputs(
                outputs=outputs,
                expected_outputs=expected_outputs,
                compare_only_keys_in_expected_outputs=compare_only_keys_in_expected_outputs,  # noqa
            )
        else:
            raise ValueError(
                f"response.status_code = {response.status_code}",
                response.content_as_json,
            )
    elif method == "get":
        response = api_client.get(
            endpoint_path=endpoint_path,
        )
        outputs = response.content_as_json

        if response.status_code == 200:
            compare_outputs_and_expected_outputs(
                outputs=outputs,
                expected_outputs=expected_outputs,
                compare_only_keys_in_expected_outputs=compare_only_keys_in_expected_outputs,  # noqa
            )

        else:
            raise ValueError(
                f"response.status_code = {response.status_code}",
                response.content_as_json,
            )

    else:
        raise ValueError("method not supported : " + method)


def check_api_service_for_one_file(
    api_client: GenericApiClient,
    endpoint_path: str,
    file_path: str,
    method: str = "post",
    compare_only_keys_in_expected_outputs: bool = False,
):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    if method == "post":
        request_body = data["inputs"]["request_body"]
    elif method == "get":
        request_body = None
    else:
        raise ValueError(f"method not supported : {method}")

    try:
        check_api_service(
            api_client=api_client,
            endpoint_path=endpoint_path,
            method=method,
            request_body=request_body,
            expected_outputs=data["expected_outputs"],
            compare_only_keys_in_expected_outputs=compare_only_keys_in_expected_outputs,
        )
    except AssertionError as error:
        logging.error("problem with : " + file_path + " - " + error.__str__())
