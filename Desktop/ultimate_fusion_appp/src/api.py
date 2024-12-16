from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformer import model

app = FastAPI()

class InputData(BaseModel):
    input_text: str

@app.post("/predict/")
def predict(data: InputData):
    input_ids = torch.tensor([[ord(c) % 1000 for c in data.input_text]])
    with torch.no_grad():
        output = model(input_ids)
        prediction = torch.argmax(output, dim=1).item()
    return {"input": data.input_text, "prediction": prediction}
