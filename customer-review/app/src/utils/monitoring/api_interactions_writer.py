import datetime
import functools
import logging
from uuid import UUID

import pandas as pd
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, validator

from app.src.config import SETTINGS
from app.src.utils.data_io_services.cloud_storage import CloudStorageManager

logging.basicConfig(level=SETTINGS.log_level, format=SETTINGS.log_format)


class RunInfo(BaseModel):
    timestamp_start: datetime.datetime
    timestamp_end: datetime.datetime
    duration: datetime.timedelta = None
    duration_in_seconds: float = -1

    @validator("duration", always=True)
    def compute_duration(cls, v, values):
        duration = values["timestamp_end"] - values["timestamp_start"]
        if duration <= datetime.timedelta(seconds=0):
            raise ValueError("duration is negative or zero - please check ")
        else:
            return duration

    @validator("duration_in_seconds", always=True)
    def compute_duration_in_seconds(cls, v, values):
        if "duration" not in values:
            raise ValueError("duration attribute not available")
        else:
            return values["duration"].total_seconds()

    def to_isoformat(self) -> dict:
        return {
            "timestamp_start": self.timestamp_start.isoformat(),
            "timestamp_end": self.timestamp_end.isoformat(),
            "duration": pd.Timedelta(self.duration).isoformat(),
            "duration_in_seconds": self.duration_in_seconds,
        }


def generate_run_info(timestamp_start: datetime.datetime) -> RunInfo:
    # TODO maybe use a pydantic BaseModel or DataClass to specify return type
    # TODO maybe add duration as iso8601

    r = RunInfo(
        timestamp_start=timestamp_start,
        timestamp_end=datetime.datetime.now(tz=datetime.timezone.utc),
    )

    return r


class ApiInteractionsWriter(CloudStorageManager):
    def __init__(self, request: Request):
        self.request = request
        self.endpoint_path: str = ""
        self.set_endpoint_path()
        super().__init__()

    @staticmethod
    def get_endpoint_path(request: Request):
        return request.url.path

    def set_endpoint_path(self):
        self.endpoint_path = self.get_endpoint_path(request=self.request)

    def define_blob_name(
        self, application_id: str, job_id: UUID, job_has_failed: bool
    ) -> str:

        """

        Note :
            endpoint_path={endpoint_path}/date={date}
            /application_id={application_id}/{success_or_failure}
            /datetime={datetime}_job_id={job_id}.json
        """

        endpoint_path_formatted = self.endpoint_path[1:].replace(
            "/", "-"
        )  # notice the tricks to get rid of "/" in path
        now = datetime.datetime.now(datetime.timezone.utc)
        date_as_str = now.date().isoformat()
        datetime_as_str = now.isoformat(timespec="milliseconds")
        success_or_failure = "failures" if job_has_failed else "success"

        blob_name = (
            f"endpoint_path={endpoint_path_formatted}/"
            f"date={date_as_str}/"
            f"application_id={application_id}/"
            f"{success_or_failure}/"
            f"datetime={datetime_as_str}_job_id={job_id}.json"
        )

        return blob_name

    def write_interactions_in_cloud_storage(
        self,
        interactions: BaseModel,
        bucket_name: str,
        blob_name: str,
        timestamp_start: datetime.datetime,
        add_run_info=True,
        add_endpoint_path_info=True,
    ):

        if isinstance(interactions, BaseModel):
            interactions_as_datamodel = interactions
        else:
            raise ValueError("interactions must be an instance of pydantic.BaseModel")

        interactions_as_dict = jsonable_encoder(interactions_as_datamodel)
        dict_to_write = {"content": interactions_as_dict}

        if add_run_info is True:
            run_info = generate_run_info(timestamp_start=timestamp_start)
            dict_to_write["run_info"] = run_info.to_isoformat()

        if add_endpoint_path_info is True:
            dict_to_write["endpoint_path"] = self.endpoint_path

        self.write_dict_to_blob(
            dict_to_write=dict_to_write,
            bucket_name=bucket_name,
            blob_name=blob_name,
        )


def write_interactions_in_cloud_storage(
    request: Request,
    interactions: BaseModel or dict,
    bucket_name: str,
    timestamp_start: datetime.datetime,
    application_id: str = None,
    job_id: UUID = None,
    job_has_failed: bool = True,
    add_run_info=False,
    add_endpoint_path_info=False,
):
    try:
        writer = ApiInteractionsWriter(request=request)
        blob_name = writer.define_blob_name(
            application_id=application_id,
            job_id=job_id,
            job_has_failed=job_has_failed,
        )

        writer.write_interactions_in_cloud_storage(
            interactions=interactions,
            bucket_name=bucket_name,
            blob_name=blob_name,
            timestamp_start=timestamp_start,
            add_run_info=add_run_info,
            add_endpoint_path_info=add_endpoint_path_info,
        )

    except Exception as e:
        err_str = "problem writing api interactions in cloud storage"
        logging.error(err_str)
        logging.error(e, exc_info=True, stack_info=True)


def write_api_interactions_in_google_cloud_storage(
    bucket_name: str, add_run_info: bool = True
):
    def decorator_api_interactions_writer(func):
        @functools.wraps(func)
        def wrapper_api_interactions_writer(*args, **kwargs):
            timestamp_start = datetime.datetime.now(tz=datetime.timezone.utc)
            outputs = None
            interactions_to_write_in_cloud_storage = None
            job_has_failed = True
            try:
                outputs = func(*args, **kwargs)

            except Exception as e:
                logging.error(e, exc_info=True, stack_info=True)
                interactions_to_write_in_cloud_storage = kwargs["inputs"]
                job_has_failed = True

            else:
                interactions_to_write_in_cloud_storage = outputs
                job_has_failed = False
            finally:
                print(f"file will be written in {bucket_name}")

                job_id = None
                if hasattr(interactions_to_write_in_cloud_storage, "job_id"):
                    job_id = interactions_to_write_in_cloud_storage.job_id

                application_id = None
                if hasattr(interactions_to_write_in_cloud_storage, "application_id"):
                    application_id = (
                        interactions_to_write_in_cloud_storage.application_id
                    )

                write_interactions_in_cloud_storage(
                    request=kwargs["request"],
                    interactions=interactions_to_write_in_cloud_storage,
                    bucket_name=bucket_name,
                    timestamp_start=timestamp_start,
                    application_id=application_id,
                    job_id=job_id,
                    job_has_failed=job_has_failed,
                    add_run_info=add_run_info,
                    add_endpoint_path_info=True,
                )

            return outputs

        return wrapper_api_interactions_writer

    return decorator_api_interactions_writer
