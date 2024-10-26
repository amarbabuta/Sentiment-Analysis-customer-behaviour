from asyncio.subprocess import PIPE
from app.src.datamodels import ModelPredictInput, ModelPredictOutput
from fastapi import HTTPException
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd
import os
        
def model_predict(
    inputs: ModelPredictInput
):
    review = inputs.review
    if os.path.isdir('app/models/saved_model'):
        # Load the model and tokenizer
        model = BertForSequenceClassification.from_pretrained('app/models/saved_model')
        tokenizer = BertTokenizer.from_pretrained('app/models/saved_model')
        model.eval()
        try:    
            # Tokenize the input review
            inputs = tokenizer(review, return_tensors='pt', padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                logits = model(**inputs).logits
                prediction = torch.argmax(logits, dim=-1).item()
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")


        sentiment = 'positive' if prediction == 1 else 'negative'
            
            
        # Get the predictions
        outputs = ModelPredictOutput(sentiment=sentiment)
    
    else:
        # Get the predictions
        outputs = ModelPredictOutput(sentiment='First train the model')
    return outputs
    
