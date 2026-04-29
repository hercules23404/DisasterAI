# AI Context Documentation

**Purpose**: Machine-readable structured data optimized for AI tools, LLMs, and automated analysis.

**Format**: JSON with consistent schemas, explicit relationships, and complete metadata.

**Last Updated**: 2026-04-29

---

## Overview

This folder contains the complete DisasterAI project context in structured JSON format, designed specifically for consumption by AI assistants, code analysis tools, and automated documentation systems. Unlike the human-readable `context/` folder, these files prioritize:

- **Structured data** over narrative prose
- **Explicit relationships** between components
- **Complete metadata** with units, timestamps, and provenance
- **Machine-parseable formats** (JSON) over markdown
- **Hierarchical organization** for efficient querying

---

## File Structure

```
ai_context/
├── README.md                      # This file
├── project_metadata.json          # Project info, authors, tech stack, entry points
├── system_architecture.json       # Components, algorithms, data flow, performance
├── experimental_results.json      # Complete experimental data with statistics
└── research_papers.json           # 40 papers categorized with component mapping
```

---

## File Descriptions

### 1. `project_metadata.json`

**Purpose**: High-level project information and quick reference data.

**Contents**:
- Project name, version, status, last updated date
- Authors with affiliations and contact information
- Study area coordinates and grid specifications
- Technology stack (Python libraries, frameworks, data sources)
- Key results summary (baseline comparison, optimal parameters)
- Documentation folder structure
- Entry point commands for running experiments

**Use Cases**:
- Quick project overview for AI assistants
- Generating project summaries
- Identifying correct commands to run
- Understanding tech stack dependencies

**Schema**:
```json
{
  "project": { "name", "full_name", "version", "status", "last_updated", "authors", "location" },
  "technology_stack": { "language", "core_libraries", "visualization", "ml_frameworks", "data_sources" },
  "key_results": { "baseline_comparison", "optimal_lookahead" },
  "documentation": { "human_readable", "ai_optimized", "legacy", "research_papers" },
  "entry_points": { "dashboard", "baseline_experiments", "ablation_study", "all_experiments" }
}
```

---

### 2. `system_architecture.json`

**Purpose**: Complete technical architecture with algorithms, complexity, and performance.

**Contents**:
- 4-layer architecture (Presentation, Orchestration, Simulation, Data)
- 11 core components with detailed specifications:
  - Algorithm names and complexity (Big-O notation)
  - File paths and key functions
  - Performance metrics (ms per step)
  - Purpose and interfaces
- Complete data flow (initialization + simulation loop)
- Performance benchmarks and scalability tests

**Use Cases**:
- Understanding system design and component interactions
- Identifying bottlenecks and optimization opportunities
- Generating architecture diagrams
- Code navigation and refactoring
- Performance analysis

**Schema**:
```json
{
  "architecture": {
    "layers": [ { "name", "components", "purpose", "technologies" } ],
    "components": [ {
      "id", "name", "file", "algorithm", "complexity", "purpose",
      "key_functions", "performance"
    } ]
  },
  "data_flow": { "initialization", "simulation_loop" },
  "performance": { "per_step_timing", "scalability" }
}
```

**Key Components**:
1. Flood Propagation Engine (D8 Min-Heap, O(n log n))
2. Rescue Unit Dispatch Engine (Hungarian, O(n³))
3. Dynamic Pathfinding System (A*, O(E log V))
4. Flood Predictor (N-step forward simulation)
5. Composite Risk Scorer (4-component weighted formula)
6. Reward Function (MARL incentive structure)
7. Pre-Positioning Module (MCLP)
8. Victim Spawn Model (Population-weighted)
9. Environment Orchestrator (OpenAI Gym interface)
10. MARL Engine & Baselines (QMIX + 5 baselines)
11. Animated Dashboard (Streamlit + Plotly)

---

### 3. `experimental_results.json`

**Purpose**: Complete experimental data with statistical analysis.

**Contents**:
- Experiment metadata (dates, hardware, total runs)
- **Baseline Comparison** (100 runs, 5 algorithms):
  - Hungarian + Predictive (N=2): 735.8 ± 312.5 score, 19.3 min response time
  - Greedy Myopic: 232.0 ± 246.1 score, 30.9 min response time
  - Nearest Unit: 193.8 ± 289.4 score, 30.1 min response time
  - Priority Queue: 23.9 ± 267.3 score, 31.5 min response time
  - Random: 8.5 ± 297.8 score, 30.5 min response time
  - Statistical significance: p < 0.001, Cohen's d = 1.85 (large effect)
- **Ablation Study** (100 runs, 5 lookahead values):
  - N=1: 719.4 ± 348.2 score
  - N=2: 835.8 ± 386.7 score (optimal, +16.2% vs N=1)
  - N=3: 789.9 ± 459.3 score (+9.8% vs N=1)
  - N=5: 740.3 ± 363.8 score (+2.9% vs N=1)
  - N=7: 800.8 ± 398.5 score (+11.3% vs N=1)
- Flood characteristics (peak extent, progression pattern)
- Computational performance breakdown (per-step timing)
- Scalability tests (144×144 to 256×256 grids)
- Data file paths and schemas

**Use Cases**:
- Generating result tables and figures
- Statistical analysis and hypothesis testing
- Performance benchmarking
- Comparing algorithm variants
- Validating research claims

**Schema**:
```json
{
  "experiments": {
    "date", "total_runs", "hardware",
    "baseline_comparison": { "runs_per_algorithm", "simulation_params", "results", "statistical_significance" },
    "ablation_study": { "parameter", "values_tested", "results", "key_finding" },
    "flood_characteristics": { "peak_flood_extent", "flood_progression", "victim_spawn_pattern" },
    "computational_performance": { "per_step_breakdown_ms", "scalability_tests", "bottleneck" }
  },
  "data_files": { "baseline_comparison", "ablation_lookahead", "figures" }
}
```

---

### 4. `research_papers.json`

**Purpose**: Complete research foundation with paper-to-component mapping.

**Contents**:
- 40 papers from IEEE Transactions paper (2026)
- Local coverage: 2/40 papers available (5%)
- Papers categorized by domain:
  - Flood Propagation (12 papers)
  - Dispatch Optimization (8 papers)
  - Pathfinding (5 papers)
  - MARL Framework (10 papers)
  - Pre-Positioning (3 papers)
  - Reward Shaping (3 papers)
  - Risk Scoring (5 papers)
  - Domain Context (2 papers)
- 6 core papers identified (highest impact)
- Component-to-paper mapping (which papers support which algorithms)
- Key insights with supporting papers

**Use Cases**:
- Understanding research foundation
- Identifying missing papers to acquire
- Generating literature review sections
- Validating algorithm choices
- Finding related work

**Schema**:
```json
{
  "research_foundation": {
    "total_papers", "source", "local_coverage", "categories", "top_venues",
    "core_papers": [ { "ref", "title", "venue", "importance", "local_file" } ],
    "component_mapping": {
      "component_name": { "core_algorithm", "key_papers", "comparison_papers" }
    }
  },
  "key_insights": {
    "insight_name": { "finding", "supporting_papers" }
  }
}
```

**Core Papers** (highest priority):
- [3] MARL with Hierarchical Coordination (ICML 2024) - **MISSING**
- [14] Shortest Path Planning and Dynamic Rescue Forces (Nature 2025) - **MISSING**
- [16] Online Algorithms for Ambulance Routing (OR Spectrum 2024) - **MISSING**
- [38] Fair Prioritization of Casualties (BMC 2021) - **MISSING**
- [5] Introduction to CTDE in Cooperative MARL (arXiv 2024) - **AVAILABLE**
- [36] Anytime and Efficient Multi-Agent Coordination (Springer 2021) - **AVAILABLE**

---

## Usage Examples

### Example 1: Generate Project Summary

```python
import json

with open('ai_context/project_metadata.json') as f:
    meta = json.load(f)

print(f"Project: {meta['project']['full_name']}")
print(f"Authors: {', '.join([a['name'] for a in meta['project']['authors']])}")
print(f"Key Result: {meta['key_results']['baseline_comparison']['improvement_vs_greedy']['score']} improvement")
```

### Example 2: Analyze Component Performance

```python
import json

with open('ai_context/system_architecture.json') as f:
    arch = json.load(f)

for component in arch['architecture']['components']:
    print(f"{component['name']}: {component['algorithm']} - {component['performance']}")
```

### Example 3: Extract Experimental Results

```python
import json

with open('ai_context/experimental_results.json') as f:
    results = json.load(f)

baseline = results['experiments']['baseline_comparison']['results']
for algo, data in baseline.items():
    print(f"{algo}: {data['mean_score']:.1f} ± {data['std_score']:.1f}")
```

### Example 4: Find Papers for Component

```python
import json

with open('ai_context/research_papers.json') as f:
    papers = json.load(f)

component = 'dispatch_optimization'
mapping = papers['research_foundation']['component_mapping'][component]
print(f"Core Algorithm: {mapping['core_algorithm']}")
print(f"Key Papers: {mapping['key_papers']}")
```

---

## Comparison with Human-Readable Context

| Aspect | `ai_context/` (This Folder) | `context/` (Human-Readable) |
|--------|----------------------------|----------------------------|
| **Format** | JSON (structured) | Markdown (narrative) |
| **Target Audience** | AI tools, LLMs, parsers | Human developers, researchers |
| **Organization** | Hierarchical, queryable | Linear, sequential |
| **Metadata** | Explicit (units, timestamps) | Implicit (embedded in prose) |
| **Relationships** | Explicit (IDs, references) | Implicit (described in text) |
| **Use Case** | Automated analysis, code generation | Understanding, learning, documentation |
| **Completeness** | All data with provenance | Curated highlights with context |

**When to Use Which**:
- **Use `ai_context/`** when:
  - Providing context to AI assistants (Claude, GPT, etc.)
  - Building automated tools or scripts
  - Generating documentation programmatically
  - Performing data analysis or visualization
  - Need precise, structured data

- **Use `context/`** when:
  - Onboarding new team members
  - Writing research papers or reports
  - Understanding system design and rationale
  - Learning how components work together
  - Need narrative explanations and examples

---

## Maintenance Guidelines

### When to Update These Files

1. **`project_metadata.json`**:
   - Version changes
   - New authors or affiliations
   - Technology stack updates
   - New entry points or commands

2. **`system_architecture.json`**:
   - New components added
   - Algorithm changes
   - Performance improvements
   - Architecture refactoring

3. **`experimental_results.json`**:
   - New experiments run
   - Different hardware tested
   - New baseline algorithms added
   - Ablation studies on different parameters

4. **`research_papers.json`**:
   - New papers acquired locally
   - New papers published and referenced
   - Component-to-paper mappings updated
   - New insights discovered

### Validation Checklist

Before committing changes to these files:
- [ ] JSON syntax is valid (use `python -m json.tool <file>`)
- [ ] All referenced files exist (check paths in `data_files`)
- [ ] Units are specified for all numeric values
- [ ] Timestamps are in ISO 8601 format (YYYY-MM-DD)
- [ ] Cross-references are consistent (e.g., paper refs match across files)
- [ ] Schema structure matches examples in this README

---

## Integration with Other Documentation

### Documentation Hierarchy

```
DisasterAI/
├── README.md                          # Quick start, installation, basic usage
├── QUICK_START.md                     # Step-by-step tutorial
├── context/                           # Human-readable documentation (7 files)
│   ├── README.md                      # Navigation guide
│   ├── PROJECT_OVERVIEW.md            # High-level introduction
│   ├── ARCHITECTURE.md                # System design narrative
│   ├── MODULES.md                     # Detailed module reference
│   ├── RESEARCH_FOUNDATION.md         # Papers and citations
│   ├── RESULTS_SUMMARY.md             # Experimental results explained
│   └── QUICK_REFERENCE.md             # Commands and troubleshooting
├── ai_context/                        # Machine-readable documentation (5 files)
│   ├── README.md                      # This file
│   ├── project_metadata.json          # Project info and tech stack
│   ├── system_architecture.json       # Components and algorithms
│   ├── experimental_results.json      # Complete experimental data
│   └── research_papers.json           # Research foundation
├── papers/                            # Research papers (PDF)
│   ├── PAPER_CATALOG.md               # 40-paper catalog with metadata
│   ├── DisasterAI_IEEE_Paper.pdf      # THE ACTUAL PAPER
│   └── ...                            # 2 available papers
└── docs/                              # Legacy documentation (archived)
```

### Cross-References

- **IEEE Paper** → `papers/DisasterAI_IEEE_Paper.pdf` (authoritative source)
- **Paper Catalog** → `papers/PAPER_CATALOG.md` (40 references mapped)
- **Human Context** → `context/` (narrative explanations)
- **AI Context** → `ai_context/` (structured data, this folder)
- **Results Data** → `results/baseline_comparison.csv`, `results/ablation_lookahead.csv`
- **Figures** → `results/ieee_figures/` (7 publication-ready plots)

---

## AI Assistant Usage Tips

### For Claude, GPT, and Other LLMs

**Best Practices**:
1. **Start with `project_metadata.json`** for quick overview
2. **Use `system_architecture.json`** for understanding code structure
3. **Reference `experimental_results.json`** for validating claims
4. **Check `research_papers.json`** for research foundation

**Example Prompts**:
- "Based on `ai_context/system_architecture.json`, explain how the dispatch engine works"
- "Using `ai_context/experimental_results.json`, compare Hungarian vs Greedy algorithms"
- "From `ai_context/research_papers.json`, which papers support the flood propagation algorithm?"
- "Generate a performance report using data from `ai_context/`"

**Context Window Optimization**:
- These JSON files are designed to be compact and information-dense
- Total size: ~25KB (vs ~150KB for markdown context)
- Can be loaded entirely into most LLM context windows
- Use selective loading for specific queries (e.g., only load `experimental_results.json` for result analysis)

---

## Future Enhancements

Potential additions to this folder:

1. **`configuration.json`**: All config parameters with defaults and ranges
2. **`api_reference.json`**: Function signatures, parameters, return types
3. **`dependencies.json`**: Complete dependency graph with versions
4. **`test_coverage.json`**: Test suite metadata and coverage metrics
5. **`changelog.json`**: Structured version history with semantic versioning

---

## Contact

For questions about this documentation structure:
- **Viraj Champanera**: vc3288@srmist.edu.in
- **Abhinav Tripathi**: at6467@srmist.edu.in
- **Dr. R Mohandas**: mohandar1@srmist.edu.in

---

**Last Updated**: 2026-04-29  
**Version**: 1.0.0  
**Status**: Production-Ready
