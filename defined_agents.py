import torch

from rlcard.agents.dmc_agent.model import DMCAgent
from rlcard.agents.random_agent import RandomAgent
from agents.zole_human_agent import HumanAgent


def get_dmc_agent(env, index=0, xpid='dmc') -> DMCAgent:
    checkpoint_states = torch.load('experiments/dmc_result/' + xpid + '/model.tar', map_location='cpu')

    state_dict = checkpoint_states['model_state_dict'][index]

    agent = DMCAgent(
        state_shape=env.state_shape[index],
        action_shape=[env.num_actions],
        device='cpu'
    )

    agent.load_state_dict(state_dict)
    
    return agent


def get_path_agent(path: str):
    return torch.load(path)


def get_random_agent(env) -> RandomAgent:
    return RandomAgent(num_actions=env.num_actions)


def get_human_agent(env) -> HumanAgent:
    return HumanAgent(num_actions=env.num_actions)
