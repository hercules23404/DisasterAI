# Module 5: Dispatch Engine

## Overview
Located in `dispatch_engine.py`, this module matches available rescue resources to victims requiring assistance.

## Methodologies
- **Hungarian Algorithm (Kuhn-Munkres)**: Solves the linear assignment problem for bipartite matching in $O(n^3)$ time.
- **Composite Cost Matrix**: Edges in the bipartite graph are weighted by: `travel_time × (2.0 − composite_risk)`.

## Why We Use Them
Greedy dispatch (nearest-unit) causes localized pile-ups and often ignores distant but high-risk victims, resulting in catastrophic loss of life. The Hungarian algorithm guarantees global mathematical optimality for assignment. By modifying the cost matrix to include risk, it intrinsically balances the tradeoff between saving time and saving the most endangered individuals.

## How We Use Them
When victims are spawned, the engine compiles a cost matrix between all idle units and active victims. It solves for the optimal assignment that minimizes the overall risk-weighted travel time. It also features preemptive staging, directing surplus units toward high-confidence predicted victim zones before the victims even formally trigger a rescue request.
