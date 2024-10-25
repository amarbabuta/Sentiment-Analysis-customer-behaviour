import datetime
import time
import json
import sys
import logging
from app.src.config import SETTINGS

from app.tests.helpers.api_services_checkers import ApiSettings, set_api_client

now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
DATA_FOLDER_PATH = "app/tests/app_services/data/train/reviews_data.json"

def _define_time_to_wait_before_checking_if_job_is_completed(
    test_api_server_type: str,
) -> datetime.timedelta:
    training_job_duration = datetime.timedelta(seconds=2)
    if test_api_server_type in ["test_starlette", "local"]:
        time_to_wait = training_job_duration
    elif test_api_server_type == "cloud_run":
        # since the default min_instances for cloud run is zero,
        # we need to wait for the cloud_run to start and to run the job
        cloud_run_warm_up_duration = datetime.timedelta(seconds=60)
        time_to_wait = cloud_run_warm_up_duration + training_job_duration
    else:
        raise ValueError(f"test_api_server_type not supported : {test_api_server_type}")
    return time_to_wait


def test_train():
    f = open(DATA_FOLDER_PATH)
    data = json.load(f)


    # launch training_job
    endpoint_path = "model_training"
    
    logging.info(f"check endpoint {endpoint_path} - start") 
    logging.info("form_data_to_post_for_training_from_json")

    settings_api = ApiSettings(
        api_server_type=SETTINGS.test_api_server_type,
        api_server_url=SETTINGS.test_api_server_url,
    )

    api_client = set_api_client(settings_api=settings_api)

    response = api_client.post(
        endpoint_path=endpoint_path,
        data=data,
        query_params={"test_mode": True},
    )

    assert (
    response.status_code == 200
    ), f"check failed  : response.status_code == {response.status_code}"

    # wait for the training to finish
    time_to_wait = _define_time_to_wait_before_checking_if_job_is_completed(
        test_api_server_type=SETTINGS.test_api_server_type
    )
    
    time.sleep(time_to_wait.total_seconds())

    logging.info("response received")
    logging.info(f"Accuracy Score : {response.content_as_json['accuracy_score']}")
    logging.info(f"check endpoint {endpoint_path} - end")
    
    with open('app/tests/app_services/data/train/predicted_value.json', 'w') as outfile:
        json.dump({'Accuracy Score': response.content_as_json['accuracy_score']}, outfile)
    
if __name__ == "__main__":
    test_train()