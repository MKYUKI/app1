from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import BertTokenizer, BertForSequenceClassification
import torch

app = FastAPI()

# Pydanticモデル
class PredictRequest(BaseModel):
    text: str
    phone: str

class PredictResponse(BaseModel):
    label: str
    score: float

# トークナイザーとモデルのロード
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

@app.post("/predict/", response_model=PredictResponse)
async def predict(request: PredictRequest):
    inputs = tokenizer(request.text, return_tensors="pt")
    outputs = model(**inputs)
    scores = torch.nn.functional.softmax(outputs.logits, dim=1)
    predicted_class = torch.argmax(scores, dim=1).item()
    label = "Positive" if predicted_class == 1 else "Negative"
    score = scores[0][predicted_class].item()
    return PredictResponse(label=label, score=score)

# チャットボットエンドポイント
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 簡単なチャットボットの実装例
    if "こんにちは" in request.message:
        reply = "こんにちは！ご用件をお聞かせください。"
    elif "AI" in request.message:
        reply = "AIについて詳しくお話しします。何を知りたいですか？"
    else:
        reply = "申し訳ありませんが、その質問には答えられません。"
    return ChatResponse(reply=reply)

# テキスト生成エンドポイント
class GenerateRequest(BaseModel):
    prompt: str
    max_length: int

class GenerateResponse(BaseModel):
    generated_text: str

@app.post("/generate/", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    from transformers import GPT2LMHeadModel, GPT2Tokenizer

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    inputs = tokenizer.encode(request.prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=request.max_length, num_return_sequences=1, no_repeat_ngram_size=2, early_stopping=True)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return GenerateResponse(generated_text=generated_text)

# お問い合わせエンドポイント
class ContactRequest(BaseModel):
    name: str
    email: str
    phone: str
    message: str

@app.post("/contact/")
async def contact(request: ContactRequest):
    # ここでメール送信やデータベース保存などの処理を行います
    # 例として、成功メッセージを返します
    return {"detail": "メッセージが正常に送信されました。"}
