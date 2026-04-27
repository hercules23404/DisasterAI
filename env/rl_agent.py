"""
rl_agent.py
───────────
QMIX Multi-Agent Reinforcement Learning (MARL) implementation for EPyMARL/PyMARL2.

Features:
- Replaces SB3 DQN with a PyMARL-compatible MultiAgentEnv wrapper.
- Implements Centralized Training with Decentralized Execution (CTDE).
- Heterogeneous cooperative agents (Ambulances & Firefighters).
- Partial observability: Each agent gets a local cropped observation.
- Global state provided for the centralized QMIX mixing network.
- Extended 6-channel state: [Current Flood Depth, Predicted Flood Depth,
  Composite Risk Grid, Victim Positions, Unit Positions, Population Vulnerability]

Usage:
    This file defines `DisasterPyMARLEnv`, which inherits from `MultiAgentEnv`.
    To train with EPyMARL, register this environment in EPyMARL's env registry.
"""

import numpy as np

try:
    # EPyMARL / PyMARL base class
    from envs.multiagentenv import MultiAgentEnv
except ImportError:
    raise ImportError("EPyMARL is not installed or not in the Python path. Please clone the EPyMARL repository and run this module from within its structure, or add it to your PYTHONPATH.")

# ── Observation / state constants ─────────────────────────────────────
OBS_RADIUS = 5        # radius (in grid cells) for agent partial observation crop
N_CHANNELS = 6        # state tensor channels: current depth, predicted depth,
                      # composite risk, victim positions, unit positions, pop vulnerability

class DisasterPyMARLEnv(MultiAgentEnv):
    def __init__(self, env_factory, obs_radius=OBS_RADIUS, max_victims=20):
        """
        Parameters
        ----------
        env_factory : callable
            A function that returns a fresh DisasterEnvironment instance.
        obs_radius : int
            The radius (in pixels) for the agent's partial observation crop.
        max_victims : int
            The maximum number of concurrent victims (defines action space size).
        """
        self.env_factory = env_factory
        self.obs_radius = obs_radius
        self.max_victims = max_victims
        self.env = self.env_factory()
        
        # Dynamic agent count based on active rescue units
        self.n_agents = len(self.env.units)
        self.episode_limit = 200
        self.steps = 0
        
        # Action space: 0 is NO-OP. 1..N is "assign to active victim i-1"
        self.n_actions = self.max_victims + 1 
        
        # Global state size: H × W × N_CHANNELS
        self.state_channels = N_CHANNELS
        H, W = self.env.rem.shape
        self.state_size = int(H * W * self.state_channels)
        
        # Local observation size: (2r+1)² × N_CHANNELS + agent_type_dim
        self.obs_dim = (2 * self.obs_radius + 1)
        self.obs_size = int(self.obs_dim * self.obs_dim * self.state_channels)
        
        # Identify heterogeneous agent types (Ambulance vs Firefighter)
        self.agent_type_dim = 2 # 0: Ambulance, 1: Firefighter
        self.obs_size += self.agent_type_dim

    def step(self, actions):
        """
        Takes a step in the environment.
        actions: list of integers (one per agent). 
        """
        active_incs = self.env.incident_manager.get_active_incidents()
        env_actions = []
        
        for i, action in enumerate(actions):
            if action > 0 and (action - 1) < len(active_incs):
                unit = self.env.units[i]
                if unit.status == "idle" and not unit.returning:
                    victim = active_incs[action - 1]
                    env_actions.append((unit.id, victim.id))
                    
        state, reward, done, info = self.env.step(env_actions)
        self.steps += 1
        
        if self.steps >= self.episode_limit:
            done = True
            
        # Joint reward is shared among all cooperative agents
        return float(reward), done, info

    def get_obs(self):
        """Returns all agent observations in a list."""
        return [self.get_obs_agent(i) for i in range(self.n_agents)]

    def get_obs_agent(self, agent_id):
        """
        Returns the partial observation for a single agent.
        Includes local flood state, nearby victims, and nearby units.
        """
        unit = self.env.units[agent_id]
        state = self.env.get_state()
        
        # Pad state to handle edges
        r = self.obs_radius
        # state is (H, W, Channels)
        padded_state = np.pad(state, ((r, r), (r, r), (0, 0)), mode='constant', constant_values=0)
        
        ur, uc = int(unit.r), int(unit.c)
        # Crop around unit's position
        local_crop = padded_state[ur:ur + 2*r + 1, uc:uc + 2*r + 1, :]
        obs_flat = local_crop.flatten().astype(np.float32)
        
        # Append heterogeneous type one-hot encoding
        type_encoding = np.zeros(self.agent_type_dim, dtype=np.float32)
        if unit.type == "Ambulance":
            type_encoding[0] = 1.0
        else:
            type_encoding[1] = 1.0
            
        return np.concatenate([obs_flat, type_encoding])

    def get_obs_size(self):
        """Returns the shape of the observation."""
        return self.obs_size

    def get_state(self):
        """
        Returns the global state for Centralized Training with Decentralized Execution (CTDE).
        This is consumed by the QMIX mixing network.
        """
        return self.env.get_state().flatten().astype(np.float32)

    def get_state_size(self):
        """Returns the shape of the global state."""
        return self.state_size

    def get_avail_actions(self):
        """Returns the available actions for all agents."""
        return [self.get_avail_agent_actions(i) for i in range(self.n_agents)]

    def get_avail_agent_actions(self, agent_id):
        """
        Returns a list of length n_actions with 1s and 0s indicating available actions.
        """
        avail = np.zeros(self.n_actions, dtype=int)
        avail[0] = 1 # NO-OP always available
        
        unit = self.env.units[agent_id]
        
        # If the unit is busy transporting or returning to depot, it cannot take new assignments
        if unit.status != "idle" or unit.returning:
            return avail.tolist()
            
        active_incs = self.env.incident_manager.get_active_incidents()
        for i in range(len(active_incs)):
            if i + 1 < self.n_actions:
                avail[i + 1] = 1
                
        return avail.tolist()

    def get_total_actions(self):
        """Returns the total number of actions an agent could ever take."""
        return self.n_actions

    def reset(self):
        """Resets the environment for a new episode."""
        self.env.reset()
        self.steps = 0
        return self.get_obs(), self.get_state()

    def get_reward(self):
        """Returns the current accumulated reward."""
        return getattr(self.env, 'total_reward', 0.0)

    def render(self):
        pass

    def close(self):
        pass

    def seed(self, seed=None):
        if seed is not None:
            np.random.seed(seed)

    def get_env_info(self):
        """Provides environment specifications to the EPyMARL framework."""
        env_info = {
            "state_shape": self.get_state_size(),
            "obs_shape": self.get_obs_size(),
            "n_actions": self.get_total_actions(),
            "n_agents": self.n_agents,
            "episode_limit": self.episode_limit
        }
        return env_info


def rl_dispatch(env, agent=None):
    """
    Fallback dispatch integration for the Streamlit dashboard.
    Because PyMARL models run via PyTorch runners, to integrate 
    a trained QMIX model here requires loading the MAC (Multi-Agent Controller).
    If no trained model is passed, we fallback to the Hungarian baseline.
    """
    if agent is None:
        from env.baselines import hungarian_dispatch
        return hungarian_dispatch(env)
        
    # Example logic if PyMARL MAC (Multi-Agent Controller) is passed:
    # obs = [get_obs_agent(i) for i in range(env.n_agents)]
    # actions = agent.select_actions(obs, avail_actions)
    # return decode_actions(actions)
    pass
