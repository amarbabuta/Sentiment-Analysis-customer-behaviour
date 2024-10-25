import logging
import os

import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import google.oauth2.id_token

from app.src.utils.api_clients.generic_api_client import GenericApiClient


class GcpServicesClient(GenericApiClient):
    def __init__(
        self,
        api_server_url: str,
        api_server_type: str,
        user_agent: str = None,
        connect_timeout: float = 180,
        read_timeout: float = 20,
        max_retries: int = 5,
        use_google_application_default_credentials: bool = True,
    ):
        super().__init__(
            api_server_url=api_server_url,
            api_server_type=api_server_type,
            user_agent=user_agent,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            max_retries=max_retries,
        )
        self.use_google_application_default_credentials: bool = (
            use_google_application_default_credentials
        )

    def _get_id_token_from_application_default_credentials(self) -> str:
        logging.info("")
        credentials, project_id = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        id_token = credentials.id_token
        return id_token

    def _get_id_token_from_explicit_service_account_file(self) -> str:
        logging.info(
            f"_get_id_token_from_explicit_service_account_file for audience :"
            f" {self.api_server_url}"
        )
        request = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(request, self.api_server_url)
        return id_token

    def _get_id_token(self):
        """
        Notes :
            we use this twisted imbrication because the
            _get_id_token_from_application_default_credentials method does not work
            when GOOGLE_APPLICATION_CREDENTIALS is set in os.environ
        """
        if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
            try:
                logging.info(
                    "GOOGLE_APPLICATION_CREDENTIALS is set in os.environ "
                    "- let's try to fetch id_token with this "
                    "explicit_service_account_file"
                )
                id_token = self._get_id_token_from_explicit_service_account_file()
            except Exception as e:
                logging.info(
                    "_get_id_token_from_explicit_service_account_file has failed", e
                )
                logging.info("let's try to fetch application_default_credentials")
                # google_application_credentials_backup = os.environ[
                #     "GOOGLE_APPLICATION_CREDENTIALS"
                # ]
                # we delete temporarly "GOOGLE_APPLICATION_CREDENTIALS" beecause
                # del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
                id_token = self._get_id_token_from_application_default_credentials()
                # os.environ[
                #     "GOOGLE_APPLICATION_CREDENTIALS"
                # ] = google_application_credentials_backup

        else:
            id_token = self._get_id_token_from_application_default_credentials()

        return id_token

    def set_headers(self):
        """
        Note that this method overrides the one inherit from GenericApiClient
        """
        if self.use_google_application_default_credentials is True:

            headers = {
                "User-Agent": self.user_agent,
                "Accept": "application/json",
                "Authorization": f"Bearer {self._get_id_token()}",
            }
        else:
            raise ValueError(
                "use_google_application_default_credentials is False not supported"
            )

        self.headers = headers
