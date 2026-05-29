from stable_baselines3.common.distributions import Categorical
from stable_baselines3.common.policies import ActorCriticPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import torch
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
            # Use stride=2 to halve the image size
            nn.Conv2d(in_features, 32, kernel_size=8, stride=4),
            nn.ReLU(),

            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),

            MarioResidualBlock(64),
            MarioResidualBlock(64),

            # Optional: Add a MaxPool here if you want to shrink it further
            nn.MaxPool2d(2),

            nn.Flatten(),
        )

        # Compute shape dynamically by passing in a dummy tensor
        with torch.no_grad():
            dummy_input = torch.zeros(1, *observation_space.shape)
            n_flatten = self.net(dummy_input).shape[1]

        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU()
        )

    def forward(self, x):
        return self.linear(self.net(x))


class MarioPPO(nn.Module):
    def __init__(self, features_dim=128, num_actions=9):
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

    def _get_action_from_latent(self, latent_pi, deterministic=False):
        dir_logits, jump_logits, action_logits = self.mlp_extractor.forward_actor(latent_pi)
        if deterministic:
            dir = torch.argmax(dir_logits, dim=1)
            jump = torch.argmax(jump_logits, dim=1)
            action = torch.argmax(action_logits, dim=1)
        else:
            dir = Categorical(logits=dir_logits).sample()
            jump = Categorical(logits=jump_logits).sample()
            action = Categorical(logits=action_logits).sample()
        return torch.stack([dir, jump, action], dim=1)

    def _get_action_log_prob(self, actions, latent_pi):
        dir_logits, jump_logits, action_logits = self.mlp_extractor.forward_actor(latent_pi)
        dir = actions[:, 0]
        jump = actions[:, 1]
        action = actions[:, 2]
        dir_prob = Categorical(logits=dir_logits).log_prob(dir)
        jump_prob = Categorical(logits=jump_logits).log_prob(jump)
        action_prob = Categorical(logits=action_logits).log_prob(action)
        return dir_prob + jump_prob + action_prob
