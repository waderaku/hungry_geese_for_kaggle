from typing import List, Tuple

import numpy as np
import tensorflow as tf
from geese.agent import Agent
from geese.constants import ACTIONLIST
from geese.structure import Observation
from geese.structure.parameter.agent_parameter import AgentParameter
from geese.util.converter import action2int, to_np_obs
from kaggle_environments.envs.hungry_geese.hungry_geese import Action
from kaggle_environments.envs.hungry_geese.hungry_geese import (
    Observation as KaggleObservation,
)

EPS = 1e-6


class PPOAgent(Agent):
    def __init__(self, parameter: AgentParameter):
        self._model = parameter.model
        # KaggleAgentとして利用するためのKaggle Observation
        self._last_obs = None

        self._last_action = None

    # return Tuple([4], [4], [4*4])
    def step(
        self,
        obs: List[Observation],
        masked_flg: bool = False,
        before_done_list: List[bool] = None,
    ) -> Tuple[List[Action], np.ndarray, np.ndarray]:
        prob_list, value_list = self._model(np.array(obs))
        prob_list = prob_list.numpy()
        value_list = value_list.numpy()
        if masked_flg and self._last_action is not None:
            mask_action_index = [
                self._mask_action(action2int(action)) for action in self._last_action
            ]
            mask_action_one_hot = np.identity(len(ACTIONLIST))[mask_action_index]
            # 前回の行動を0、それ以外を1にする
            mask_action_one_hot = (
                mask_action_one_hot.T * (1 - np.array(before_done_list))
            ).T * -1 + 1
            # masking
            masked_prob_list = (prob_list + EPS) * mask_action_one_hot
            sum_prob_list = np.sum(masked_prob_list, axis=1)
            next_action_list = [
                np.random.choice(ACTIONLIST, p=prob / sum_prob)
                for prob, sum_prob in zip(masked_prob_list, sum_prob_list)
            ]
        else:
            next_action_list = [
                np.random.choice(ACTIONLIST, p=prob) for prob in prob_list
            ]
        self._last_action = next_action_list
        return next_action_list, value_list, prob_list

    def _mask_action(self, action: int):
        if action == 0:
            return 1
        elif action == 1:
            return 0
        elif action == 2:
            return 3
        elif action == 3:
            return 2
        else:
            raise ValueError

    def get_action(self, obs: Observation) -> Action:
        next_action, _, _ = self.step([obs])
        return next_action[0]

    def save(self, path: str) -> None:
        if self._model.built:
            self._model.save(path)
        else:
            print("Model is not yet built. Skipping saving proceduce.")

    def load(self, path: str) -> None:
        self._model = tf.keras.models.load_model(path)

    @property
    def model(self) -> tf.keras.models.Model:
        return self._model

    def __call__(self, obs: KaggleObservation) -> str:
        np_obs = to_np_obs(obs, self._last_obs)
        action = self.get_action(np_obs)
        return action.name
