from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from torch import nn


class MarioResidualBlock(nn.Module):
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


class MarioEncoder(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim=128):
        super().__init__(observation_space, features_dim)

        in_features = observation_space.shape[0]
        
        self.net = nn.Sequential(
            nn.Conv2d(in_features, 32, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),

            MarioResidualBlock(64),
            MarioResidualBlock(64),

            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),

            nn.Linear(64, features_dim),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.net(x)


class MarioPPO(nn.Module):
    def __init__(self, features_dim=128, num_actions=10):
        super().__init__()

        self.latent_dim_pi = features_dim
        self.latent_dim_vf = features_dim

        self.policy_net = nn.Sequential(
            nn.Linear(features_dim, self.latent_dim_pi),
            nn.ReLU(),
        )

        self.value_net = nn.Sequential(
            nn.Linear(features_dim, self.latent_dim_vf),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.forward_actor(x), self.forward_critic(x)

    def forward_actor(self, x):
        return self.policy_net(x)
    
    def forward_critic(self, x):
        return self.value_net(x)


class MarioPPOWrapper(ActorCriticPolicy):
    def __init__(self, observation_space, action_space, lr_schedule, *args,
                 **kwargs):
        kwargs['ortho_init'] = False
        super().__init__(observation_space, action_space, lr_schedule, *args,
                         **kwargs)
    
    def _build_mlp_extractor(self):
        self.mlp_extractor = MarioPPO(self.features_dim)
