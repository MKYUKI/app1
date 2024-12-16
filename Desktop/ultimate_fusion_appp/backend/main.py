# backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, constr
from transformers import pipeline
import torch
import logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Ultimate Fusion AI API",
    description="API for Transformer-based AI functionalities",
    version="1.0.0"
)

# CORS設定
origins = [
    "http://localhost:3000",  # ローカル開発環境
    "https://your-domain.com",  # 本番ドメイン
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 許可するオリジン
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Transformerパイプラインの初期化
try:
    sentiment_analyzer = pipeline("sentiment-analysis")
except Exception as e:
    logger.error(f"Error loading sentiment model: {e}")
    raise e

try:
    chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")
except Exception as e:
    logger.error(f"Error loading chatbot model: {e}")
    raise e

try:
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
except Exception as e:
    logger.error(f"Error loading GPT-2 model: {e}")
    raise e

# データモデルの定義
class TextInput(BaseModel):
    text: constr(min_length=1)

class Prediction(BaseModel):
    label: str
    score: float

class ChatInput(BaseModel):
    message: constr(min_length=1)

class ChatResponse(BaseModel):
    reply: str

class ContactInput(BaseModel):
    name: constr(min_length=1, max_length=100)
    email: EmailStr
    message: constr(min_length=1, max_length=1000)

class ContactResponse(BaseModel):
    status: str
    detail: str

class GenerateInput(BaseModel):
    prompt: constr(min_length=1)
    max_length: int = 50

class GenerateResponse(BaseModel):
    generated_text: str

# エンドポイントの定義
@app.post("/predict/", response_model=Prediction, summary="Predict sentiment of input text")
def predict_sentiment(input: TextInput):
    try:
        result = sentiment_analyzer(input.text)[0]
        return Prediction(label=result['label'], score=result['score'])
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました。")

@app.post("/chat/", response_model=ChatResponse, summary="Chat with AI")
def chat_ai(input: ChatInput):
    try:
        conversation = chatbot(input.message)
        reply = conversation.generated_responses[-1]
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました。")

@app.post("/contact/", response_model=ContactResponse, summary="Handle contact form submissions")
def handle_contact(input: ContactInput):
    try:
        # ここでメール送信やデータベース保存のロジックを実装
        # 例としてログに記録
        logger.info(f"Contact Form Submission - Name: {input.name}, Email: {input.email}, Message: {input.message}")
        return ContactResponse(status="success", detail="メッセージが正常に送信されました。")
    except Exception as e:
        logger.error(f"Contact form processing error: {e}")
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました。")

@app.post("/generate/", response_model=GenerateResponse, summary="Generate text based on prompt")
def generate_text(input: GenerateInput):
    try:
        inputs = tokenizer.encode(input.prompt, return_tensors="pt")
        outputs = gpt2_model.generate(inputs, max_length=input.max_length, num_return_sequences=1, no_repeat_ngram_size=2, early_stopping=True)
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return GenerateResponse(generated_text=generated_text)
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        raise HTTPException(status_code=500, detail="内部サーバーエラーが発生しました。")
