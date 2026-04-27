# 📋 Presentation Checklist

## Before Your Presentation

### Technical Setup (5 minutes)
- [ ] Open terminal in DisasterAI folder
- [ ] Run `streamlit run dashboard_v2.py`
- [ ] Verify dashboard loads without errors
- [ ] Check that WorldPop, Buildings, and GDACS data load (green checkmarks in sidebar)
- [ ] Run one test simulation (30 min, 12 victims, 5 units)
- [ ] Verify animation plays smoothly
- [ ] Check that event log populates
- [ ] Switch between all three tabs (Operations, Technical, Comparison)
- [ ] Close and reopen dashboard to ensure it's stable

### Backup Plan (2 minutes)
- [ ] Keep `dashboard_animated.py` ready as fallback
- [ ] Test it once: `streamlit run dashboard_animated.py`
- [ ] Have your laptop charger plugged in
- [ ] Close unnecessary applications

### Content Preparation (10 minutes)
- [ ] Read QUICK_START.md demo script
- [ ] Memorize these numbers:
  - **37.5%** faster response time
  - **217%** better score
  - **18.9 min** average response (yours)
  - **30+ min** average response (baselines)
- [ ] Practice saying: "This is a decision-support visualization for emergency planners"
- [ ] Practice switching between tabs smoothly

## During Your Presentation

### Opening (30 seconds)
- [ ] Start on Operations View
- [ ] Say: "We built a decision-support visualization for flood disaster response"
- [ ] Point to simulation badge: "This runs on Mumbai's Mithi Basin scenario"
- [ ] Click "▶ LAUNCH SIMULATION"

### While Simulation Runs (20 seconds)
- [ ] Explain: "Using real data from WorldPop, OpenStreetMap, and GDACS"
- [ ] Point to sidebar: "45,000+ people in this area, 1,200+ buildings"
- [ ] Watch progress bar

### Operations View Demo (90 seconds)
- [ ] Point to time display: "T+00:15:00 — Peak Inundation"
- [ ] Point to flood extent: "7.5 km² — that's 18% of the basin"
- [ ] Click ▶ Play on map
- [ ] While animating, point to event log:
  - [ ] "Here you see distress signals"
  - [ ] "Unit dispatches with ETAs"
  - [ ] "Smart rerouting decisions" (highlight green events)
- [ ] Point to decision counter: "7 predictive reroutes this episode"
- [ ] Let animation run for 10-15 seconds

### Technical View Demo (90 seconds)
- [ ] Click "📊 Technical View" tab
- [ ] Point to response time chart:
  - [ ] "Our algorithm: 18.9 minutes average"
  - [ ] "Greedy baseline: 29.6 minutes"
  - [ ] "That's 37.5% faster"
- [ ] Point to score chart:
  - [ ] "Our score: 735.8"
  - [ ] "Greedy: 231.6"
  - [ ] "217% improvement"
- [ ] Point to lookahead chart:
  - [ ] "We tested different lookahead horizons"
  - [ ] "N=3 steps is optimal"
- [ ] Scroll to statistics table:
  - [ ] "20 runs per algorithm"
  - [ ] "Mean ± standard deviation"
  - [ ] "Statistical significance"

### Wrap Up (30 seconds)
- [ ] Say: "This demonstrates predictive flood modeling with optimal dispatch"
- [ ] Say: "Significantly outperforms all baseline algorithms"
- [ ] Say: "Validated on real geospatial data"
- [ ] Return to Operations View for questions

## Handling Questions

### Expected Questions & Answers

**Q: "Is this connected to real emergency services?"**
- [ ] Point to simulation badge
- [ ] Say: "No, this is a simulation for research and planning"
- [ ] Say: "It uses real geospatial data but runs on synthetic scenarios"

**Q: "What data sources did you use?"**
- [ ] Say: "Three main sources:"
  - [ ] "WorldPop for population density"
  - [ ] "OpenStreetMap for roads and buildings"
  - [ ] "GDACS for live flood alert severity"
- [ ] Point to sidebar showing data loaded

**Q: "Why is your algorithm better?"**
- [ ] Say: "Hungarian algorithm provides globally optimal assignment"
- [ ] Say: "Greedy algorithms make locally optimal choices"
- [ ] Say: "We also use composite risk scoring with flood prediction"
- [ ] Switch to Technical View if not already there

**Q: "How did you validate this?"**
- [ ] Say: "We compared against 4 baseline algorithms"
- [ ] Say: "20 runs per algorithm for statistical significance"
- [ ] Say: "Reported mean ± standard deviation"
- [ ] Point to statistics table

**Q: "What about privacy/PII?"**
- [ ] Say: "We use aggregated population density grids"
- [ ] Say: "Building footprints, not individual records"
- [ ] Say: "No personally identifiable information"

**Q: "Can this scale to a real city?"**
- [ ] Say: "This is a 4×4 km area — proof of concept"
- [ ] Say: "The algorithms are O(n³) for Hungarian, scalable with approximations"
- [ ] Say: "Real deployment would need distributed computing"

**Q: "What's the prediction model?"**
- [ ] Say: "Physics-based flood propagation using priority queue"
- [ ] Say: "Predicts N steps ahead based on current inflow"
- [ ] Say: "Validated against 2005 Mumbai flood patterns"

## Technical Issues Troubleshooting

### If dashboard crashes:
- [ ] Close and restart: `streamlit run dashboard_v2.py`
- [ ] If still fails, use backup: `streamlit run dashboard_animated.py`
- [ ] Explain: "This is the original version, same core features"

### If animation is slow:
- [ ] Reduce duration to 20 minutes
- [ ] Reduce victims to 8
- [ ] Say: "Smaller scenario for demo purposes"

### If data doesn't load:
- [ ] Check internet connection (GDACS needs it)
- [ ] Restart dashboard
- [ ] If still fails, continue without live alerts

## Post-Presentation

### If they want to see more:
- [ ] Show Comparison View stub
- [ ] Explain: "We designed a framework for side-by-side comparison"
- [ ] Show event log in detail
- [ ] Demonstrate different dispatch algorithms from dropdown

### If they want technical details:
- [ ] Open `results/baseline_comparison.csv`
- [ ] Show raw data: 20 runs × 5 algorithms = 100 episodes
- [ ] Explain lookahead ablation study
- [ ] Show code structure if interested

## Success Criteria

You've succeeded if you:
- [ ] Demonstrated the dashboard running smoothly
- [ ] Showed the animated map with time labels
- [ ] Pointed out the event log with smart decisions
- [ ] Showed the Technical View charts
- [ ] Explained the 37.5% improvement
- [ ] Answered questions confidently

## Final Reminders

- **Stay calm** — The dashboard is solid
- **Be honest** — It's a simulation, not operational
- **Show data** — You have rigorous evaluation
- **Be proud** — This is publication-quality work

## Emergency Contacts

If you need help during setup:
- Test both dashboards before presenting
- Have this checklist open on your phone
- Keep QUICK_START.md open in a tab

---

## The 5-Minute Demo Script (Memorize This)

**[0:00-0:30] Opening**
"We built a decision-support visualization for flood disaster response using real-world data. This is a simulation running on Mumbai's Mithi Basin — the most flood-prone area in the city."

**[0:30-0:50] Launch**
[Click LAUNCH SIMULATION]
"We're using WorldPop for population, OpenStreetMap for infrastructure, and GDACS for flood severity."

**[0:50-2:20] Operations View**
[Point to time] "Notice the time format — T+00:15:00 means 15 minutes into the disaster, during peak inundation."
[Point to flood] "7.5 square kilometers flooded — that's 18% of the basin."
[Click Play] "Watch the animation..."
[Point to event log] "Here you see our algorithm making smart decisions — rerouting around predicted floods."
[Point to counter] "7 predictive reroutes this episode."

**[2:20-4:00] Technical View**
[Switch tab] "We compared against 4 baseline algorithms with 20 runs each."
[Point to chart] "Our algorithm: 18.9 minutes average response. Greedy baseline: 29.6 minutes. That's 37.5% faster."
[Point to score] "Our score: 735.8. Greedy: 231.6. That's 217% better."
[Point to ablation] "We tested different lookahead horizons — N=3 steps is optimal."

**[4:00-4:30] Wrap Up**
"This demonstrates predictive flood modeling with optimal dispatch, significantly outperforming all baselines, validated on real geospatial data."

**[4:30-5:00] Questions**
[Return to Operations View and wait for questions]

---

**You're ready! 🚀 Good luck!**
