import os
import urllib.request
import torch
import torch.nn as nn

MODEL_URL = ("https://github.com/christophschuhmann/improved-aesthetic-predictor/raw/main/sac+logos+ava1-l14-linearMSE"
             ".pth")
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "aesthetic_model.pth")


def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        print("Downloading aesthetic model...")
        urllib.request.urlretrieve(
            MODEL_URL,
            MODEL_PATH
        )
        print("Model downloaded:", MODEL_PATH)


def load_aesthetic_model():
    download_model()
    model = AestheticPredictor()
    model.load_state_dict(
        torch.load(MODEL_PATH,
                   map_location="cpu")
    )
    model.eval()
    return model


class AestheticPredictor(nn.Module):

    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(768, 1024),
            nn.Dropout(0.2),
            nn.Linear(1024, 128),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.Dropout(0.1),
            nn.Linear(64, 16),
            nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.layers(x)
