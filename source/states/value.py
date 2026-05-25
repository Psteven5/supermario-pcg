from torch import nn
from encoder import Encoder


class Value(nn.Module):
    def __init__(self, num_features=7, num_frames=4):
        super().__init__()
        
        self.net = nn.Sequential(
            Encoder(num_features, num_frames),

            nn.Linear(128, 1),
        )

    def forward(self, x):
        return self.net(x)
