import functools
from typing import List
from gym import spaces
from pettingzoo import ParallelEnv
from pettingzoo.utils import wrappers, parallel_to_aec
from pz_battlesnake.constants import DEFAULT_COLORS
from pz_battlesnake.spaces.move import Move
from pz_battlesnake.wrapper import env_done, env_render, env_reset, env_setup, env_step


def env(**kwargs):
    env = raw_env(**kwargs)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    env = wrappers.OrderEnforcingWrapper(env)
    return env


def raw_env(**kwargs):
    """
    To support the AEC API, the raw_env() function just uses the from_parallel
    function to convert from a ParallelEnv to an AEC env
    """
    env = parallel_env(**kwargs)
    env = parallel_to_aec(env)
    return env


class parallel_env(ParallelEnv):
    metadata = {
        "render_modes": ["human", "human_color"],
        "name": "battlesnake-standard_v0",
    }

    def __init__(
        self,
        width=11,
        height=11,
        num_agents=4,
        colors=DEFAULT_COLORS,
    ):
        self.possible_agents = ["agent_" + str(i) for i in range(num_agents)]
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )

        self.agent_selection = self.possible_agents[0]

        self.options = {
            "width": width,
            "height": height,
            "map": "standard",
            "game_type": "standard",
            "names": self.possible_agents,
            "colors": colors,
        }

    # this cache ensures that same space object is returned for the same agent
    # allows action space seeding to work as expected
    @functools.lru_cache(maxsize=0)
    def observation_space(self, agent=None):
        # Gym spaces are defined and documented here: https://gym.openai.com/docs/#spaces

        # Check if agent is provided
        assert agent, "Agent must be provided"

        # Check if agent is valid
        assert agent in self.possible_agents, "agent must be one of {}".format(
            self.possible_agents
        )

        # Not implemented yet
        # assert False, "observation_space() is not implemented yet"
        return spaces.Dict()

    @functools.lru_cache(maxsize=0)
    def action_space(self, agent=None):
        # Gym spaces are defined and documented here: https://gym.openai.com/docs/#spaces
        # Check if agent is provided
        assert agent, "Agent must be provided"

        # Check if agent is valid
        assert agent in self.possible_agents, "agent must be one of {}".format(
            self.possible_agents
        )

        # assert False, "observation_space() is not implemented yet"
        return Move()

    def render(self, mode="none"):
        """
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and understand.
        """
        if mode == "human":
            env_render(False)

        if mode == "human_color":
            env_render(True)

    def close(self):
        """
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        """
        pass

    def reset(self, seed=None):
        """
        Reset needs to initialize the `agents` attribute and must set up the
        environment so that render(), and step() can be called without issues.

        Returns the observations for each agent
        """
        self.agents = self.possible_agents[:]

        if seed:
            self.options["seed"] = seed

        return env_reset(self.options)

    def step(self, action):
        """
        step(action) takes in an action for each agent and should return the
            - observations
            - rewards
            - dones
            - infos
        dicts where each dict looks like {agent_0: item_1, agent_1: item_2}
        """
        if not action:
            self.agents = []
            return {}, {}, {}, {}

        agents = env_step(action)

        observations = {}
        rewards = {}
        dones = {}
        infos = {}

        for agent in agents:
            observations[agent] = agents[agent]["observation"]
            rewards[agent] = agents[agent]["reward"]
            dones[agent] = agents[agent]["done"]
            infos[agent] = agents[agent]["info"]

        if env_done():
            self.agents = []

        return observations, rewards, dones, infos
