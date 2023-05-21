""" Register new environments
"""
from rlcard.envs.registration import register

register(
    env_id='zole',
    entry_point='envs.zole:ZoleEnv',
)