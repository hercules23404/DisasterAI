# DisasterAI Project Structure

**Last Updated**: April 30, 2026  
**Status**: ✅ Clean & Organized

---

## Directory Structure

```
DisasterAI/
├── 📁 env/                          # Core simulation modules
│   ├── environment.py               # OpenAI Gym interface
│   ├── hazard_propagation.py       # D8 flood simulation
│   ├── dispatch_engine.py          # Hungarian algorithm
│   ├── pathfinding.py              # A* with flood-aware weights
│   ├── flood_predictor.py          # N-step lookahead
│   ├── risk_scorer.py              # Composite risk calculation
│   ├── reward_function.py          # MARL incentive structure
│   ├── pre_positioning.py          # MCLP optimization
│   ├── victims.py                  # Dynamic victim spawning
│   ├── baselines.py                # Baseline algorithms
│   ├── run_baselines.py            # Baseline experiments
│   └── ablation.py                 # Ablation studies
│
├── 📁 context/                      # Human-readable documentation
│   ├── README.md                    # Navigation guide
│   ├── PROJECT_OVERVIEW.md          # High-level introduction
│   ├── ARCHITECTURE.md              # System design
│   ├── MODULES.md                   # Module reference
│   ├── RESEARCH_FOUNDATION.md       # 40 papers mapped
│   ├── RESULTS_SUMMARY.md           # Experimental results
│   └── QUICK_REFERENCE.md           # Commands & troubleshooting
│
├── 📁 ai_context/                   # AI-optimized documentation
│   ├── README.md                    # Usage guide for AI tools
│   ├── project_metadata.json        # Project info & tech stack
│   ├── system_architecture.json     # Components & algorithms
│   ├── experimental_results.json    # Complete experimental data
│   └── research_papers.json         # Research foundation
│
├── 📁 papers/                       # Research papers
│   ├── PAPER_CATALOG.md             # 40-paper reference catalog
│   ├── DisasterAI_IEEE_Paper.pdf    # ⭐ THE ACTUAL PAPER
│   ├── DisasterAI_IEEE_Paper.tex    # LaTeX source
│   ├── ACM Paper 3356395.pdf        # Ref [36]
│   ├── arXiv 2409.02246.pdf         # Ref [5]
│   └── archive/                     # 25 legacy papers
│
├── 📁 results/                      # Experimental results
│   ├── baseline_comparison.csv      # 100 runs, 5 algorithms
│   ├── ablation_lookahead.csv       # 100 runs, N=1-7
│   ├── ieee_figures/                # 7 publication-ready plots
│   └── knowledge_tree/              # Knowledge tree visualization
│
├── 📁 scripts/                      # Utility scripts
│   ├── run_all_experiments.py       # Run all experiments
│   ├── generate_figures.py          # Generate IEEE figures
│   ├── build_knowledge_tree.py      # Build knowledge tree
│   ├── create_literature_table.py   # Create literature table
│   └── create_presentation.py       # Create presentation
│
├── 📁 docs/                         # Legacy detailed documentation
│
├── 📄 dashboard.py                  # ⭐ Main Streamlit dashboard
├── 📄 dashboard_utils.py            # Dashboard helper functions
├── 📄 README.md                     # Quick start guide
├── 📄 QUICK_START.md                # Step-by-step tutorial
├── 📄 CLEANUP_SUMMARY.md            # Cleanup documentation
├── 📄 Literature_Survey_Table.csv   # Literature survey
├── 📄 requirements.txt              # Python dependencies
└── 📄 .gitignore                    # Git ignore rules
```

---

## Key Entry Points

### Running the Dashboard
```bash
python3 -m streamlit run dashboard.py
```

### Running Experiments
```bash
# All experiments (baseline + ablation)
python3 scripts/run_all_experiments.py

# Baseline comparison only
python3 env/run_baselines.py

# Ablation study only
python3 env/ablation.py
```

### Generating Figures
```bash
python3 scripts/generate_figures.py
```

---

## Documentation Hierarchy

### For Humans
1. **Start here**: `README.md` - Quick start guide
2. **Tutorial**: `QUICK_START.md` - Step-by-step walkthrough
3. **Deep dive**: `context/` folder - Comprehensive documentation
   - Navigation: `context/README.md`
   - Overview: `context/PROJECT_OVERVIEW.md`
   - Architecture: `context/ARCHITECTURE.md`
   - Modules: `context/MODULES.md`
   - Research: `context/RESEARCH_FOUNDATION.md`
   - Results: `context/RESULTS_SUMMARY.md`
   - Reference: `context/QUICK_REFERENCE.md`

### For AI Tools
1. **Start here**: `ai_context/README.md` - AI usage guide
2. **Structured data**: `ai_context/*.json` - Machine-readable context
   - Project info: `project_metadata.json`
   - Architecture: `system_architecture.json`
   - Results: `experimental_results.json`
   - Papers: `research_papers.json`

### For Research
1. **The paper**: `papers/DisasterAI_IEEE_Paper.pdf`
2. **Paper catalog**: `papers/PAPER_CATALOG.md` (40 references)
3. **Research foundation**: `context/RESEARCH_FOUNDATION.md`

---

## What's NOT Here (Intentionally)

These folders/files are excluded via `.gitignore`:

- `__pycache__/` - Python bytecode cache
- `cache/` - API response caches
- `graphify-out/` - Graphify cache files
- `archive/` - Old/legacy files
- `project context/` - Replaced by `context/`
- `.DS_Store` - macOS metadata
- `.venv/`, `env/`, `venv/` - Virtual environments
- `.claude/` - Claude AI cache
- `*.code-workspace` - VS Code workspace files

---

## Folder Purposes

| Folder | Purpose | Target Audience |
|--------|---------|-----------------|
| `env/` | Core simulation code | Developers |
| `context/` | Human-readable docs | Researchers, developers |
| `ai_context/` | Machine-readable docs | AI tools, LLMs |
| `papers/` | Research papers | Researchers |
| `results/` | Experimental data | Researchers |
| `scripts/` | Utility scripts | Developers |
| `docs/` | Legacy documentation | Reference only |

---

## File Counts

- **Core modules**: 12 files in `env/`
- **Documentation**: 7 markdown files in `context/`
- **AI context**: 4 JSON files + 1 README in `ai_context/`
- **Research papers**: 2 available locally + 40 cataloged
- **Utility scripts**: 5 files in `scripts/`
- **Results**: 2 CSV files + 7 figures

---

## Size Summary

- **Total documentation**: ~3,250 lines (markdown) + ~25KB (JSON)
- **Core code**: ~5,000 lines (Python)
- **Results data**: ~200 rows (CSV) + 7 figures (PNG)
- **Research papers**: 2 PDFs available locally

---

## Maintenance

### Adding New Scripts
Place utility scripts in `scripts/` folder:
```bash
mv new_script.py scripts/
```

### Adding New Documentation
- Human-readable: Add to `context/` folder
- AI-optimized: Add to `ai_context/` folder

### Adding New Papers
1. Add PDF to `papers/` folder
2. Update `papers/PAPER_CATALOG.md`
3. Update `ai_context/research_papers.json`

---

## Clean Structure Benefits

✅ **Clear organization** - Everything has its place  
✅ **Easy navigation** - Logical folder structure  
✅ **No redundancy** - Single source of truth  
✅ **Well documented** - Multiple documentation formats  
✅ **Git-friendly** - Proper .gitignore rules  
✅ **AI-ready** - Structured data for AI tools  

---

**Last Cleanup**: April 30, 2026  
**Status**: Production-ready and well-organized
