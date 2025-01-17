# Sentiment Analysis for Customer Reviews

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1.0-red)

A powerful sentiment analysis tool for customer reviews, built with FastAPI and PyTorch.

## 🚀 Features

- 📊 Sentiment classification of customer reviews
- 🧠 BERT-based model for high accuracy
- 🔄 API for real-time sentiment prediction
- 📈 Model training and evaluation
- 🧪 Comprehensive testing suite

## 📁 Project Structure
```sh
SENTIMENT-ANALYSIS-CUSTOMER-BEHAVIOUR/
└── customer-review/
    └── app/
        ├── config/
        │   ├── default.env
        │   └── dev.env
        ├── data/
        │   ├── classification_report.csv
        │   ├── Restaurant_Reviews.tsv
        │   └── reviews_data.json
        ├── models/
        ├── openapi_specifications/
        │   ├── generate_openapi_specification.py
        │   └── Sentiment-Analysis_0.0.0_openapi.json
        ├── src/
        │   └── utils/
        │       ├── api_clients/
        │           ├── gcp_services_client.py
        │           └── generic_api_client.py
        │       ├── data_io_services/
        │           └── cloud_storage.py
        │       └── monitoring/
        │           └── api_interactions_writer.py
        │   ├── config.py
        │   ├── datamodels.py
        │   ├── model_predict.py
        │   ├── model_train.py
        │   └── training_local.py
        ├── tests/
        │   ├── app_services/
        │       ├── data/
        │           ├── dummy/
        │               └── test_dummy_00.json
        │           ├── predict/
        │               └── test_predict_00.json
        │           ├── root/
        │               └── test_root_00.json
        │           └── train/
        │               ├── predicted_value.json
        │               └── reviews_data.json
        │       ├── test_dummy.py
        │       ├── test_predict.py
        │       ├── test_root.py
        │       └── test_train.py
        │   └── helpers/
        │       ├── api_services_checkers.py
        │       ├── case_handlers.py
        │       └── test_case_handlers.py
        ├── main.py
        └── requirements.txt
    └── README.md
```


## 🛠️ Installation

1. Clone the repository:
```sh
git clone https://github.com/amarbabuta/Sentiment-Analysis-customer-behaviour.git
cd SENTIMENT-ANALYSIS-CUSTOMER-BEHAVIOUR/customer-review
```



2. Set up a virtual environment:
```sh
python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
```


3. Install dependencies:
```sh
pip install -r app/requirements.txt
```



## 🏃‍♂️ Running the Application

Start the API server:
```sh
uvicorn app.main:app --reload
```



The API will be available at `http://127.0.0.1:8000`.

## 🔍 API Endpoints
```sh
`GET /`: Welcome message
`POST /model_training`: Train the sentiment analysis model
`POST /model_predict`: Predict sentiment for a given text
`POST /dummy`: Test endpoint (returns input with a job status)
`POST /dummy_with_api_interactions_writer`: Test endpoint with API interaction logging
```


## 📊 Model Training and Prediction (Other way)

1. Train the model:
```sh
python -m app.tests.app_services.test_train
```

4. Make predictions:
```sh
python -m app.tests.app_services.test_predict
```


## 🧪 Testing

Run the test suite:
```sh
pytest app/tests
```


## 📚 Documentation

- Swagger UI: (http://127.0.0.1:8000/docs)
- ReDoc: (http://127.0.0.1:8000/redoc)



## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/amarbabuta/Sentiment-Analysis-customer-behaviour/issues).



## 📞 Contact
```sh
Your Name - (Amar Babuta) - amarbabuta0707@gmail.com
```
Project Link: (https://github.com/amarbabuta/Sentiment-Analysis-customer-behaviour)
