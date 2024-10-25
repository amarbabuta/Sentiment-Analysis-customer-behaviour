import logging

from fastapi import FastAPI, Request

from app.src.config import SETTINGS
from app.src.datamodels import (
    DummyInputs,
    DummyOutputs,
    JobStatusEnum,
)
import app.src.datamodels as datamodels
from app.src.model_train import model_train
from app.src.model_predict import model_predict
from app.src.utils.monitoring.api_interactions_writer import (
    write_api_interactions_in_google_cloud_storage,
)

logging.basicConfig(level=SETTINGS.log_level, format=SETTINGS.log_format)

app = FastAPI(
    title="Sentiment-Analysis",
    version="0.0.0",
)



@app.get(
    "/",
    summary="root",
    deprecated=False,
)
def root() -> dict:
    return {"message": "Welcome to the Sentiment-Analysis"}


@app.post(
    "/model_training",
    summary="launch_training_service",
    response_description="this service basically returns the sentiment analysis model training and evaluation.",
    response_model=datamodels.TrainingOutput,
    deprecated=False,
)

def launch_training(inputs: datamodels.TrainingInput):
    
    outputs = model_train(inputs=inputs)
    return outputs

@app.post(
    "/model_predict",
    summary="predict the sentiment",
    response_description="this service predicts thesentiment of text whether positive/negative",
    response_model=datamodels.ModelPredictOutput,
    deprecated=False,
)
def predict(inputs: datamodels.ModelPredictInput):
    outputs = model_predict(inputs=inputs)
    return outputs


@app.post(
    "/dummy",
    summary="launch_dummy_service",
    response_description="this dummy service basically returns "
    "the inputs posted and a job status",
    response_model=DummyOutputs,
    deprecated=False,
)
def launch_dummy_service(dummy_inputs: DummyInputs):
    dummy_outputs = DummyOutputs(
        **dummy_inputs.dict(), job_status=JobStatusEnum.completed
    )
    return dummy_outputs


@app.post(
    "/dummy_with_api_interactions_writer",
    summary="launch_dummy_service_with_api_interactions_writer",
    response_description="this dummy service basically returns"
    " the inputs posted and a job status",
    response_model=DummyOutputs,
    deprecated=False,
)
@write_api_interactions_in_google_cloud_storage(
    bucket_name="dummy-bucket-where-to-write-api-interactions",
    add_run_info=True,
)
def launch_dummy_service_with_api_interactions_writer(
    inputs: DummyInputs, request: Request
):
    # following logging instruction is there
    # in order to prevent warning unused variable warning because request is needed
    # by the decorator @write_api_interactions_in_google_cloud_storage
    logging.debug(request)
    outputs = DummyOutputs(**inputs.dict(), job_status=JobStatusEnum.completed)
    return outputs
