import datetime
import logging
from typing import Dict, Union

import requests
from pydantic import BaseModel, Field


class FormattedResponse(BaseModel):
    url: str = Field(..., description="url of the endpoint")
    status_code: int = Field(..., description="status_code")
    elapsed_time: datetime.timedelta = Field(
        ..., description="elapsed time to complete the request"
    )
    response_time: datetime.datetime = Field(
        ..., description="time when the response has been formatted"
    )
    content_as_json: Union[Dict, None] = Field(..., description="content_as_json")


class GenericApiClient:
    def __init__(
        self,
        api_server_url: str,
        api_server_type: str,
        user_agent: str = None,
        connect_timeout: float = 180,
        read_timeout: float = 20,
        max_retries: int = 5,
    ):

        """
        Examples :
        Based on https://swagger.io/docs/specification/api-host-and-base-path/,
        if we consider the following url :
        https://api.example.com/v1/users?role=admin&status=active

        api_server_url is "https://api.dummy.com/v1/"
        endpoint_path is "users"
        query_parameters are "?role=admin&status=active
        """

        if api_server_type not in (
            "local",
            "test_starlette",
        ):

            if not api_server_url.startswith("https"):
                raise ValueError(
                    "api_server_url does not start with https : " + str(api_server_url)
                )
            else:
                logging.debug(
                    "api_server_url does starts with https : " + str(api_server_url)
                )

        self.api_server_url: str = api_server_url
        self.user_agent: str = user_agent
        self.connect_timeout: float = connect_timeout
        self.read_timeout: float = read_timeout
        self.max_retries: int = max_retries
        self.api_server_type: str = api_server_type
        self.headers: str = None
        self.session = None

    @staticmethod
    def _format_response(response: requests.Response):

        try:
            content_as_json = response.json()
        except Exception as e:
            content_as_json = None
            logging.error(response)
            logging.error(e)
        return FormattedResponse(
            url=str(response.url),
            status_code=response.status_code,
            response_time=datetime.datetime.now(datetime.timezone.utc),
            elapsed_time=response.elapsed,
            content_as_json=content_as_json,
        )

    def form_url(self, endpoint_path: str, path_params: Union[dict, None] = None):
        url = self.api_server_url + "/"

        if path_params is None:
            url += endpoint_path
        else:

            endpoint_path_updated = endpoint_path

            for key, value in path_params.items():
                key_formatted = "{" + key + "}"
                if key_formatted in endpoint_path_updated:
                    endpoint_path_updated = endpoint_path_updated.replace(
                        key_formatted, value
                    )
                else:
                    raise ValueError(
                        f"path param : {key} not found "
                        f"in endpoint path {endpoint_path_updated}"
                    )

            url += endpoint_path_updated
        return url

    def set_headers(self):
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}
        self.headers = headers

    def init_session(self):
        if self.api_server_type != "test_starlette":
            session = requests.Session()
            self.set_headers()
            session.headers.update(self.headers)
            self.session = session

    def close_session(self):
        if self.api_server_type != "test_starlette":
            self.session.close()

    def get(
        self,
        endpoint_path: str,
        query_params: Union[dict, None] = None,
        path_params: Union[dict, None] = None,
    ) -> FormattedResponse:

        self.init_session()

        url = self.form_url(endpoint_path=endpoint_path, path_params=path_params)
        response = self.session.get(
            url,
            params=query_params,
            # verify=self.verify_ssl,
            timeout=(self.connect_timeout, self.read_timeout),
            allow_redirects=True,
        )
        response_formatted = self._format_response(response=response)
        self.close_session()
        return response_formatted

    def post(
        self,
        endpoint_path: str,
        data: Union[dict, None] = None,
        query_params: Union[dict, None] = None,
        path_params: Union[dict, None] = None,
    ) -> FormattedResponse:

        self.init_session()
        url = self.form_url(endpoint_path=endpoint_path, path_params=path_params)
        response = self.session.post(
            url,
            params=query_params,
            json=data,
            timeout=(self.connect_timeout, self.read_timeout),
            allow_redirects=True,
        )
        response_formatted = self._format_response(response=response)
        # self.close_session()
        return response_formatted
