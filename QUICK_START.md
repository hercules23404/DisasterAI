# 🚀 Quick Start Guide — Dashboard v2

## Run the Dashboard (30 seconds)

```bash
cd DisasterAI
streamlit run dashboard_v2.py
```

That's it! The dashboard will open in your browser.

## First-Time Setup (If Needed)

If you get import errors:

```bash
pip install streamlit plotly pandas numpy scipy rasterio osmnx
```

## Your 5-Minute Demo Script

### 1. Launch (30 seconds)
- Click "▶ LAUNCH SIMULATION" in sidebar
- Use defaults: 30 minutes, 12 victims, 5 units
- Wait for simulation to complete (~20 seconds)

### 2. Operations View (90 seconds)
**Say:** "This is our decision-support visualization running on Mumbai's Mithi Basin."

**Point to:**
- Time display: "T+00:15:00 — Peak Inundation"
- Flood extent: "7.5 km² (18% of basin)"
- Event log: "Here you see smart rerouting decisions"
- Decision counter: "7 predictive reroutes"

**Click:** ▶ Play button on map to show animation

### 3. Technical View (90 seconds)
**Say:** "We compared against 4 baseline algorithms with 20 runs each."

**Point to:**
- Response time chart: "37.5% faster than greedy"
- Score chart: "217% better performance"
- Lookahead chart: "N=3 steps is optimal"

**Say:** "Statistical significance with mean ± standard deviation."

### 4. Wrap Up (30 seconds)
**Say:** "This demonstrates our predictive flood modeling and optimal dispatch algorithm on real geospatial data."

## Key Numbers to Remember

- **37.5%** faster response time
- **217%** better score vs Greedy
- **18.9 min** average response (vs 30+ for baselines)
- **735.8** average score (vs <232 for baselines)

## Troubleshooting

### Dashboard won't start?
```bash
# Try the original dashboard
streamlit run dashboard_animated.py
```

### Import errors?
```bash
# Install dependencies
pip install -r requirements.txt
```

### Simulation crashes?
- Reduce duration to 20 minutes
- Reduce victims to 8
- Reduce units to 3

## Backup Plan

If dashboard_v2.py has issues, use dashboard_animated.py:
- It works (you've used it before)
- Has most of the same features
- Just lacks time translation and event log

## Questions Reviewers Might Ask

**Q: "Is this real-time?"**
A: "No, it's a simulation for research. The badge says 'Simulation Mode'."

**Q: "What data sources?"**
A: "WorldPop for population, OpenStreetMap for roads and buildings, GDACS for flood alerts."

**Q: "Why Hungarian?"**
A: "Globally optimal assignment. Greedy algorithms are locally optimal but miss global efficiency."

**Q: "How did you validate?"**
A: "20 runs per algorithm, 5 baselines, statistical comparison with mean ± std."

## You're Ready! 🎉

Just run `streamlit run dashboard_v2.py` and follow the demo script above.

**Total demo time: 5 minutes**
**Preparation needed: 0 minutes** (it's all ready)

Good luck! 🚀
