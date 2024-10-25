import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer
from transformers import BertForSequenceClassification, AdamW
from sklearn.metrics import accuracy_score, classification_report

from asyncio.subprocess import PIPE
from app.src.datamodels import TrainingOutput, TrainingInput
# from app.src.artifacts_management import ArtifactsManager

import torch
from torch.utils.data import Dataset, DataLoader
import pytz
import numpy as np
import math
from sklearn import preprocessing, cluster



class ReviewDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)
    

def model_train(
    inputs: TrainingInput
):
    # Initialise the parameters
    df_reviews = inputs.to_frame()
    
    # Split the dataset into training and validation sets
    train_df, val_df = train_test_split(df_reviews, test_size=0.2, random_state=101, stratify=df_reviews['sentiment'])

    # Initialize the tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    
    # Tokenize the training and validation reviews
    train_encodings = tokenizer(train_df['review'].tolist(), padding=True, truncation=True, return_tensors='pt', max_length=512)
    val_encodings = tokenizer(val_df['review'].tolist(), padding=True, truncation=True, return_tensors='pt', max_length=512)
    
    train_labels = train_df['sentiment'].values
    val_labels = val_df['sentiment'].values
    
    
    # Create datasets
    train_dataset = ReviewDataset(train_encodings, train_labels)
    val_dataset = ReviewDataset(val_encodings, val_labels)


    # Create DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    # Load the BERT model for sequence classification
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
    optimizer = AdamW(model.parameters(), lr=5e-5)
    
    # Train the model
    model.train()
    for epoch in range(3):  # Adjust epochs as necessary
        for batch in train_loader:
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            
    # Validate the model
    model.eval()
    predictions, true_labels = [], []
    for batch in val_loader:
        with torch.no_grad():
            outputs = model(**batch)
            logits = outputs.logits
            predictions.extend(torch.argmax(logits, dim=-1).tolist())
            true_labels.extend(batch['labels'].tolist())
    
    
    output = TrainingOutput(accuracy_score=accuracy_score(true_labels, predictions))
    
    
    clsf_report = pd.DataFrame(classification_report(y_true = true_labels, y_pred = predictions, output_dict=True)).transpose()
    clsf_report.to_csv('app/data/classification_report.csv', index= True)
    
    # Combine the training and validation sets
    full_df = pd.concat([train_df, val_df])

    # Tokenize the full dataset
    full_encodings = tokenizer(full_df['review'].tolist(), padding=True, truncation=True, return_tensors='pt', max_length=512)
    full_labels = full_df['sentiment'].values

    # Create a new dataset for the full data
    full_dataset = ReviewDataset(full_encodings, full_labels)
    full_loader = DataLoader(full_dataset, batch_size=16, shuffle=True)

    # Retrain the model on the full dataset
    model.train()
    for epoch in range(3):  # Choose the number of epochs based on your needs
        for batch in full_loader:
            optimizer.zero_grad()
            outputs = model(**batch)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
    
    # Save the model
    model.save_pretrained('app/models/saved_model')
    tokenizer.save_pretrained('app/models/saved_model')

    return output
