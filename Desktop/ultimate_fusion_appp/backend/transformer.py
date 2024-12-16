from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch

app = FastAPI()

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    label: str
    score: float

# 事前学習済みモデルとトークナイザーの読み込み
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)  # num_labelsを指定

# pipelineを使用して推論を簡略化
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

@app.post("/predict/", response_model=PredictResponse)
async def predict(request: PredictRequest):
    result = classifier(request.text)[0]
    label = result['label']
    score = result['score']
    return PredictResponse(label=label, score=score)

@app.get("/")
async def root():
    return {"message": "Welcome to the Transformer API!"}