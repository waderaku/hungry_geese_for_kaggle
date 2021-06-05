from geese.constants import NUM_GEESE, ACTIONLIST
from typing import Tuple
from geese.structure import Observation, Reward
from geese.structure.parameter.env_parameter import EnvParameter
from geese.env.env import Env
from kaggle_environments.envs.hungry_geese.hungry_geese import Action


class SoloEnv(Env):
    def __init__(self, parameter: EnvParameter):
        self._env = Env(parameter)

    def reset(self) -> Observation:
        return self._env.reset()[0]

    def step(self, action: Action) -> Tuple[Observation, Reward, bool]:
        other_actions = [
            ACTIONLIST[self._env.dena_env.rule_based_action(player)]
            for player in range(1, NUM_GEESE)
        ]
        actions = [action] + other_actions
        obs, reward, done = self._env.step(actions)
        return obs[0], reward[0], done[0]
