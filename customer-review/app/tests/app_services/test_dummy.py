# TODO maybe propose an alternative using tavern


from app.src.config import SETTINGS
from app.tests.helpers.api_services_checkers import (
    ApiSettings,
    check_api_service_for_one_file,
    set_api_client,
)

_DEFAULT_TEST_FILE_PATH = "app/tests/app_services/data/dummy/test_dummy_00.json"


def test_dummy():
    endpoint_path = "dummy"

    settings_api = ApiSettings(
        api_server_type=SETTINGS.test_api_server_type,
        api_server_url=SETTINGS.test_api_server_url,
    )

    api_client = set_api_client(settings_api=settings_api)
    check_api_service_for_one_file(
        api_client=api_client,
        endpoint_path=endpoint_path,
        file_path=_DEFAULT_TEST_FILE_PATH,
    )


def test_dummy_with_api_interactions_writer():
    endpoint_path = "dummy_with_api_interactions_writer"

    settings_api = ApiSettings(
        api_server_type=SETTINGS.test_api_server_type,
        api_server_url=SETTINGS.test_api_server_url,
    )

    api_client = set_api_client(settings_api=settings_api)
    check_api_service_for_one_file(
        api_client=api_client,
        endpoint_path=endpoint_path,
        file_path=_DEFAULT_TEST_FILE_PATH,
    )


if __name__ == "__main__":
    test_dummy()
