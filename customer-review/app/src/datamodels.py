from __future__ import annotations
from typing import List
from enum import Enum

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator


JOB_STATUS_00_TO_RUN = "to_run"
JOB_STATUS_01_LAUNCHED = "launched"
JOB_STATUS_10_COMPLETED = "completed"
JOB_STATUS_20_FAILED = "failed"

class DummyParameterEnum(str, Enum):
    value_00 = "value_00"
    value_01 = "value_01"
    
class JobStatusEnum(str, Enum):
    to_run = JOB_STATUS_00_TO_RUN
    launched = JOB_STATUS_01_LAUNCHED
    completed = JOB_STATUS_10_COMPLETED
    failed = JOB_STATUS_20_FAILED

class CustomerData(BaseModel):
    review: str = Field(default=None)
    sentiment: int = Field(description='sentiment of review', default=None)
    
    
class ReviewsTable(BaseModel):
    data: List[CustomerData]
    
    
class TrainingInput(BaseModel):
    reviews_table: ReviewsTable = Field(...)
    
    
    def to_frame(
        self,
    ) -> pd.DataFrame:
        # Create series
        df_reviews = pd.DataFrame(
            data=[[x.review, x.sentiment] for x in self.reviews_table.data],
            columns =['review', 'sentiment']
        )
        
        df_reviews = df_reviews.dropna(axis=1)
        
        return df_reviews

class TrainingOutput(BaseModel):
    accuracy_score: float = Field(description='Accuracy Score of the model')
    
class ModelPredictInput(BaseModel):
    review: str = Field(..., min_length=1, description='Review to make a prediction.')
    
    @validator('review')
    def check_review_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Review cannot be empty or whitespace.')
        return v
    
class ModelPredictOutput(BaseModel):
    sentiment: str = Field(..., description='sentiment of review')


class DummyInputs(BaseModel):
    id: str
    dummy_parameter: DummyParameterEnum = Field(
        ...,
        description="dummy_parameter to use to perform job",
    )


class DummyOutputs(DummyInputs):
    job_status: JobStatusEnum = Field(..., description="job_status")
