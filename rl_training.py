""" An example of training a reinforcement learning agent on the environments in RLCard
"""
from typing import Any

from envs.zole import ZoleEnv

import os
import argparse
import timeit
from time import sleep
from datetime import datetime

from rlcard.agents import NFSPAgent, DQNAgent
from rlcard.utils import (
    get_device,
    set_seed,
    reorganize,
)

import torch


def get_dqn_agents(env: ZoleEnv, device, log_dir) -> list[DQNAgent]:
    # TODO: load agents from path
    # if args.load_model_path != "":
    #     agent = torch.load(args.load_model_path)
    # else:

    agents = []
    for i in range(3):
        agents.append(
            DQNAgent(
                num_actions=env.num_actions,
                state_shape=env.state_shape[0],
                mlp_layers=[64, 64],
                device=device,
                save_path=log_dir,
                save_every=args.save_every
            )
        )

    return agents


def get_nfsp_agents(env: ZoleEnv, device, log_dir) -> list[NFSPAgent]:
    # TODO: load agents from path
    # if args.load_model_path != "":
    #     agent = torch.load(args.load_model_path)
    # else:

    agents = []
    for i in range(3):
        agents.append(
            NFSPAgent(
                num_actions=env.num_actions,
                state_shape=env.state_shape[0],
                hidden_layers_sizes=[64, 64],
                q_mlp_layers=[64, 64],
                device=device,
                save_path=log_dir,
                save_every=args.save_every
            )
        )

    return agents


def get_configured_environment(args, log_dir) -> tuple[ZoleEnv, list[Any]]:
    # Seed numpy, torch, random
    set_seed(args.seed)
    # Check whether gpu is available
    device = get_device()

    # Make the environment with seed
    env = ZoleEnv(config={
        'seed': args.seed,
        'large_win_incentive': args.large_win_incentive,
        'allow_step_back': False,
    })

    # Initialize the agent and use random agents as opponents
    if args.algorithm == 'dqn':
        agents = get_dqn_agents(env, device, log_dir)
    else:  # args.algorithm == 'nfsp'
        agents = get_nfsp_agents(env, device, log_dir)

    env.set_agents(agents)

    return env, agents


def train(args):
    log_dir = os.path.join(args.log_dir, args.algorithm + '_result', args.env)
    os.makedirs(log_dir, exist_ok=True)

    env, agents = get_configured_environment(args, log_dir)

    timer = timeit.default_timer
    last_checkpoint_time = timer() - args.save_interval * 60
    for episode in range(args.num_episodes):

        if args.algorithm == 'nfsp':
            agents[0].sample_episode_policy()
            agents[1].sample_episode_policy()
            agents[2].sample_episode_policy()

        # Generate data from the environment
        trajectories, payoffs = env.run(is_training=True)

        # Reorganaize the data to be state, action, reward, next_state, done
        trajectories = reorganize(trajectories, payoffs)

        for agent_id in range(3):
            for ts in trajectories[agent_id]:
                agents[agent_id].feed(ts)

        if timer() - last_checkpoint_time > args.save_interval * 60:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            for agent_id in range(3):
                save_path = os.path.join(log_dir, f'{agent_id}', f'model_{timestamp}.pth')
                torch.save(agents[agent_id], save_path)
            print('\nModels saved in', log_dir)
            last_checkpoint_time = timer()
            sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("DQN/NFSP example in RLCard")
    parser.add_argument(
        '--env',
        type=str,
        default='zole',
        choices=[
            'zole'
        ],
    )
    parser.add_argument(
        '--algorithm',
        type=str,
        default='dqn',
        choices=[
            'dqn',
            'nfsp',
        ],
    )
    parser.add_argument(
        '--cuda',
        type=str,
        default='',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
    )
    parser.add_argument(
        '--num_episodes',
        type=int,
        default=200000000,
    )
    parser.add_argument(
        '--log_dir',
        type=str,
        default='experiments',
    )
    parser.add_argument(
        "--load_model_path",
        type=str,
        default="",
    )
    parser.add_argument(
        "--save_every",
        type=int,
        default=100000
    )
    parser.add_argument(
        "--save_interval",
        type=int,
        default=15
    )
    parser.add_argument(
        '--large_win_incentive',
        type=int,
        default=0,
    )

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    train(args)
