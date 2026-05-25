from torch import nn
from encoder import Encoder


class Policy(nn.Module):
    def __init__(self, num_features=7, num_frames=4, num_actions=10):
        super().__init__()
        
        self.net = nn.Sequential(
            Encoder(num_features, num_frames),

            nn.Linear(128, num_actions),
        )

    def forward(self, x):
        return self.net(x)
