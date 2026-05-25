import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from torch import nn


class Env(gym.Env):
    def __init__(self, width=20, height=15, num_features=7, num_frames=4,
                 num_actions=10):
        super().__init__()

        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(num_features * num_frames, height, width),
            dtype=np.float32,
        )

        self.action_space = spaces.Discrete(num_actions)

    def reset(self, seed=None, options=None):
        obs = self.get_obs()
        info = {}
        return obs, info

    def step(self, action):
        pass


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

            MarioResidualBlock(32),
            MarioResidualBlock(32),

            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),

            nn.Linear(32, features_dim),
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
        return self.policy_net(x), self.value_net(x)


class MarioPPOWrapper(ActorCriticPolicy):
    def __init__(self, observation_space, action_space, lr_schedule, *args,
                 **kwargs):
        kwargs['ortho_init'] = False
        super().__init__(observation_space, action_space, lr_schedule, *args,
                         **kwargs)
    
    def _build_mlp_extractor(self):
        self.mlp_extractor = MarioPPO(self.features_dim)


env = Env()


policy_kwargs = dict(
    features_extractor_class=MarioEncoder,
    features_extractor_kwargs=dict(features_dim=128),
)


model = PPO(
    policy=MarioPPOWrapper,
    env=env,
    policy_kwargs=policy_kwargs,
    learning_rate=0.0003,
    n_steps=2_048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    verbose=1,
)


model.learn(total_timesteps=1_000_000)
