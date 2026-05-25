from torch import nn


class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()

        self.net = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
        )

        self.relu = nn.ReLU()
    
    def forward(self, x):
        return self.relu(self.net(x) + x)
    

class Encoder(nn.Module):
    def __init__(self, num_features=7, num_frames=4):
        super().__init__()
        
        self.net = nn.Sequential(
            nn.Conv2d(num_features * num_frames, 32, kernel_size=3, padding=1),
            nn.ReLU(),

            ResidualBlock(64),
            ResidualBlock(64),

            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )

    def forward(self, x):
        return self.net(x)
