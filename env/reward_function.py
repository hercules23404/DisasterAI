# env/reward_function.py
"""
reward_function.py
──────────────────
Explicit reward signal for QMIX agents.
Every term is documented so the panel can audit it.

Reward formula — what QMIX is maximising:
    R = +rescue_base × (1 + composite_risk)    [per successful rescue]
      + preemptive_bonus × preemptive_arrivals
      − time_penalty × composite_risk           [per active victim per step]
      − flood_penalty × flooded_traversals
      − 2 × rescue_base × deaths
      − rescue_base × idle_penalty_factor × idle_agents_facing_high_risk

Rescuing a critical victim (composite_risk close to 1.0) yields up to
2× rescue_base reward. Preemptive arrivals — units that stage in a
predicted zone before a victim spawns — receive a bonus, incentivising
forward-looking behaviour.

The time penalty is risk-weighted so agents feel more urgency for
high-risk victims. Deaths carry double the rescue reward as a penalty
to make them categorically undesirable.

The idle penalty fires when an agent has no target AND at least one
active victim has composite_risk > 0.5, discouraging avoidance of
high-risk engagements.
"""


class RewardFunction:
    """
    Explicit reward signal for QMIX agents.
    Every term is documented so the panel can audit it.
    """

    def __init__(self, rescue_base=10.0, time_penalty=0.1,
                 flood_penalty=5.0, preemptive_bonus=3.0,
                 idle_penalty_factor=0.1):
        self.rescue_base        = rescue_base
        self.time_penalty       = time_penalty
        self.flood_penalty      = flood_penalty
        self.preemptive_bonus   = preemptive_bonus
        self.idle_penalty_factor = idle_penalty_factor

    def step_reward(self, events: dict) -> float:
        r = 0.0
        for rescue in events.get('rescues', []):
            r += self.rescue_base * (1.0 + rescue['composite_risk'])
        r += self.preemptive_bonus * events.get('preemptive_arrivals', 0)
        for victim in events.get('active_victims', []):
            r -= self.time_penalty * victim['composite_risk']
        r -= self.flood_penalty * events.get('flooded_traversals', 0)
        r -= self.rescue_base * 2.0 * events.get('deaths', 0)

        # Idle penalty: penalise each idle agent when high-risk victims exist
        idle_agents = events.get('idle_agents', 0)
        high_risk_exists = any(
            v['composite_risk'] > 0.5
            for v in events.get('active_victims', [])
        )
        if high_risk_exists and idle_agents > 0:
            r -= self.rescue_base * self.idle_penalty_factor * idle_agents

        return r

