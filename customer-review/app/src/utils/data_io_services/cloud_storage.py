import datetime
import json
import logging
from io import BytesIO, StringIO
from typing import Dict, List, Union
from typing.io import IO

import google
import pandas as pd
from google.cloud import storage
from google.cloud.storage import Blob

from app.src.config import SETTINGS

logging.basicConfig(level=SETTINGS.log_level, format=SETTINGS.log_format)

_DEFAULT_BUCKET_LOCATION = "australia-southeast1"
_DEFAULT_ENCODING = "utf-8"
_MAX_BUCKET_NAME_LENGTH = 63


# TODO add associated tests
class CloudStorageManager:
    def __init__(self):
        self.client = storage.Client()

    def create_bucket(self, bucket_name: str, location: str = _DEFAULT_BUCKET_LOCATION):
        bucket = storage.bucket.Bucket(client=self.client, name=bucket_name)
        new_bucket = self.client.create_bucket(bucket, location=location)
        logging.info("bucket created : " + new_bucket.name)

    def list_buckets(self):
        buckets = self.client.list_buckets()
        return buckets

    def check_if_bucket_exists(self, bucket_name: str) -> bool:
        buckets_names = [x.name for x in self.list_buckets()]
        r = bucket_name in buckets_names
        return r

    def delete_all_blobs_in_bucket(self, bucket_name: str) -> None:
        blobs = self.client.list_blobs(bucket_name)
        for blob in blobs:
            blob.delete()

    def delete_bucket(
        self, bucket_name: str, delete_all_blobs_before: bool = False
    ) -> None:
        if not self.check_if_bucket_exists(bucket_name=bucket_name):
            logging.warning(
                f"impossible to delete bucket {bucket_name} since it does not exist"
            )

        else:
            if delete_all_blobs_before is True:
                self.delete_all_blobs_in_bucket(bucket_name=bucket_name)

            bucket = self.client.get_bucket(bucket_name)
            logging.info(f"deleting bucket {bucket_name} - start")
            bucket.delete()
            logging.info(f"deleting bucket {bucket_name} - end")

    def list_blob_names_in_bucket(self, bucket_name: str) -> List[str]:
        blobs = self.client.list_blobs(bucket_name)
        return [blob.name for blob in blobs]

    def instantiate_blob(
        self,
        bucket_name: str,
        blob_name: str,
    ) -> Blob:
        bucket = self.client.get_bucket(bucket_name)
        return bucket.blob(blob_name)

    def check_if_blob_exists(self, bucket_name: str, blob_name: str):
        blob = self.instantiate_blob(bucket_name=bucket_name, blob_name=blob_name)
        return blob.exists()

    def write_string_to_blob(
        self, string_to_write: str, bucket_name: str, blob_name: str
    ) -> None:
        if self.check_if_bucket_exists(bucket_name=bucket_name) is False:
            self.create_bucket(bucket_name=bucket_name)

        blob = self.instantiate_blob(bucket_name=bucket_name, blob_name=blob_name)
        blob.upload_from_string(string_to_write)
        logging.info(f"string written into blob : gs://{bucket_name}/{blob_name}")

    def write_dict_to_blob(
        self, dict_to_write: Dict, bucket_name: str, blob_name: str
    ) -> None:
        string_to_write = json.dumps(dict_to_write)
        self.write_string_to_blob(
            string_to_write=string_to_write,
            bucket_name=bucket_name,
            blob_name=blob_name,
        )

    def write_file_to_blob(
        self, source_file_path: str, bucket_name: str, blob_name: str
    ) -> None:
        if self.check_if_bucket_exists(bucket_name=bucket_name) is False:
            self.create_bucket(bucket_name=bucket_name)

        blob = self.instantiate_blob(bucket_name=bucket_name, blob_name=blob_name)
        blob.upload_from_filename(filename=source_file_path)
        logging.info(f"blob written in following  location : {bucket_name}/{blob_name}")

    def write_file_object_to_blob(
        self,
        source_file_object: Union[IO, StringIO, BytesIO],
        bucket_name: str,
        blob_name: str,
    ):
        if self.check_if_bucket_exists(bucket_name=bucket_name) is False:
            self.create_bucket(bucket_name=bucket_name)
        blob = self.instantiate_blob(bucket_name=bucket_name, blob_name=blob_name)
        blob.upload_from_file(file_obj=source_file_object)
        logging.info(f"blob written in following  location : {bucket_name}/{blob_name}")

    def download_blob_as_bytes(self, bucket_name: str, blob_name: str) -> bytes:
        blob = self.instantiate_blob(bucket_name=bucket_name, blob_name=blob_name)
        r = blob.download_as_bytes(client=self.client)
        return r

    def download_blob_as_pandas_dataframe(self, bucket_name, blob_name) -> pd.DataFrame:
        blob_as_bytes = self.download_blob_as_bytes(
            bucket_name=bucket_name, blob_name=blob_name
        )
        blob_as_string = str(blob_as_bytes, _DEFAULT_ENCODING)
        data = StringIO(blob_as_string)
        return pd.read_csv(data)

    def download_blob_as_dict(self, bucket_name, blob_name) -> dict:
        blob_as_bytes = self.download_blob_as_bytes(
            bucket_name=bucket_name, blob_name=blob_name
        )
        a = blob_as_bytes.decode(encoding=_DEFAULT_ENCODING)
        r = json.loads(a)
        return r

    def download_blob_to_file(
        self, bucket_name: str, blob_name: str, destination_file_path: str
    ) -> None:
        blob = self.instantiate_blob(bucket_name=bucket_name, blob_name=blob_name)
        blob.download_to_filename(filename=destination_file_path)

    def delete_blob(self, bucket_name: str, blob_name: str) -> None:
        blob = self.instantiate_blob(bucket_name=bucket_name, blob_name=blob_name)
        blob.delete()
        logging.info("blob deleted : " + blob_name + "\nin bucket : " + bucket_name)

    def copy_blob(
        self,
        source_bucket_name: str,
        source_blob_name: str,
        destination_bucket_name: str,
        destination_blob_name: str,
    ):
        source_bucket = self.client.get_bucket(source_bucket_name)
        source_blob = source_bucket.blob(source_blob_name)

        if self.check_if_bucket_exists(bucket_name=destination_bucket_name) is False:
            self.create_bucket(bucket_name=destination_bucket_name)

        destination_bucket = self.client.get_bucket(destination_bucket_name)

        destination_blob = source_bucket.copy_blob(
            source_blob, destination_bucket, destination_blob_name
        )

        logging.info(
            "Blob {} in bucket {} copied to blob {} in bucket {}.".format(
                source_blob.name,
                source_bucket.name,
                destination_blob.name,
                destination_bucket.name,
            )
        )

    def move_blob(
        self,
        source_bucket_name,
        source_blob_name,
        destination_bucket_name,
        destination_blob_name,
    ):
        self.copy_blob(
            source_bucket_name=source_bucket_name,
            source_blob_name=source_blob_name,
            destination_bucket_name=destination_bucket_name,
            destination_blob_name=destination_blob_name,
        )

        self.delete_blob(bucket_name=source_bucket_name, blob_name=source_blob_name)


_DEFAULT_TIMESPEC_FOR_BUCKET_NAME = "seconds"


def _get_now_formatted_for_bucket_name(
    timespec: str = _DEFAULT_TIMESPEC_FOR_BUCKET_NAME,
) -> str:
    return (
        datetime.datetime.now()
        .isoformat(sep="-", timespec=timespec)
        .replace(":", "")
        .replace("T", "")
    )


def define_bucket_name_with_default_gcp_project_name(
    bucket_name_generic: str,
    add_creation_timestamp: bool,
):
    _, _default_gcp_project_name = google.auth.default()

    bucket_name = f"{_default_gcp_project_name}-{bucket_name_generic}"

    if add_creation_timestamp is True:
        now_formatted_for_bucket_name = _get_now_formatted_for_bucket_name(
            timespec=_DEFAULT_TIMESPEC_FOR_BUCKET_NAME
        )
        bucket_name = bucket_name + "-" + now_formatted_for_bucket_name

    return bucket_name[-_MAX_BUCKET_NAME_LENGTH:]
