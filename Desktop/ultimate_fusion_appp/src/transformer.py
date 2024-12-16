import torch
import torch.nn as nn
import torch.nn.functional as F

class Transformer(nn.Module):
    def __init__(self, input_dim, model_dim, num_heads, num_layers, output_dim):
        super(Transformer, self).__init__()
        self.embedding = nn.Embedding(input_dim, model_dim)
        self.positional_encoding = nn.Parameter(torch.zeros(1, 100, model_dim))
        self.encoder_layer = nn.TransformerEncoderLayer(d_model=model_dim, nhead=num_heads)
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(model_dim, output_dim)

    def forward(self, src):
        src = self.embedding(src) + self.positional_encoding[:, :src.size(1), :]
        output = self.transformer_encoder(src)
        return self.fc(output.mean(dim=1))

# モデルの初期化
input_dim = 1000  # ボキャブラリーサイズ
model_dim = 128   # 隠れ層の次元
num_heads = 8     # マルチヘッド注意機構の数
num_layers = 4    # エンコーダ層の数
output_dim = 10   # 出力次元

model = Transformer(input_dim, model_dim, num_heads, num_layers, output_dim)
