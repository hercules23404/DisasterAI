# DisasterAI Context Documentation

**Last Updated:** April 29, 2026

This folder contains comprehensive, human-readable documentation for the DisasterAI project. These files are designed to provide complete context for understanding the system's design, implementation, and research foundation.

---

## Documentation Files

### 📋 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
**Start here!** High-level introduction to DisasterAI.

**Contents:**
- What is DisasterAI and why it exists
- Core mission and use cases
- System architecture overview (4 components)
- Technology stack
- Key experimental results
- Research foundation summary
- Quick start guide
- Project structure
- Current status and future work

**Best for:** First-time readers, stakeholders, project presentations

---

### 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md)
Deep dive into system design and component interactions.

**Contents:**
- Layered architecture diagram
- Data layer (terrain, population, buildings, APIs)
- Simulation engines (flood, dispatch, pathfinding)
- Orchestration layer (environment, state space, reward function)
- Presentation layer (dashboard, visualization)
- Data flow diagrams
- Performance characteristics
- Design decisions and rationale
- Extension points for customization
- Known limitations

**Best for:** Developers, system architects, technical reviewers

---

### 🔧 [MODULES.md](MODULES.md)
Detailed reference for all 12 core modules.

**Contents:**
- Module 1: Terrain and Data Loaders
- Module 2: Hazard Injection & Propagation
- Module 3: Flood Predictor
- Module 4: Risk Scorer
- Module 5: Dispatch Engine
- Module 6: Reward Function
- Module 7: Pre-Positioning Module
- Module 8: Pathfinding
- Module 9: Victim Spawn Model
- Module 10: Environment Orchestrator
- Module 11: MARL Engine & Baselines
- Module 12: Animated Dashboard

Each module includes:
- Purpose and algorithms
- Why these methods were chosen
- Implementation details
- Key functions and APIs
- Research foundation
- Performance benchmarks

**Best for:** Developers implementing features, code reviewers, researchers

---

### 📚 [RESEARCH_FOUNDATION.md](RESEARCH_FOUNDATION.md)
*(To be created)* Mapping of 29 research papers to project components.

**Contents:**
- Component 1: Flood Propagation Engine (12 papers)
- Component 2: Rescue Unit Dispatch (8 papers)
- Component 3: Dynamic Pathfinding (5 papers)
- Component 4: Multi-Agent Architecture (4 papers)
- Paper catalog with metadata
- Publication venue analysis
- Research coverage matrix

**Best for:** Academic reviewers, researchers, paper submissions

---

### 📊 [RESULTS_SUMMARY.md](RESULTS_SUMMARY.md)
Comprehensive experimental results and analysis.

**Contents:**
- Baseline comparison study (5 algorithms, 100 runs)
- Lookahead ablation study (5 values, 100 runs)
- Statistical significance analysis
- Performance metrics (response time, score, rescue rate)
- Computational performance benchmarks
- Flood propagation characteristics
- Key findings and conclusions
- Future experiments

**Best for:** Results analysis, paper writing, performance evaluation

---

### ⚡ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
Practical guide for common tasks and troubleshooting.

**Contents:**
- Installation and setup
- Running the simulation
- Configuration parameters
- Common tasks (run experiments, generate figures)
- Dashboard controls
- File structure
- Troubleshooting guide
- Performance optimization
- API reference
- Data sources
- Quick commands cheat sheet

**Best for:** Daily development, troubleshooting, quick lookups

---

## Reading Paths

### For New Team Members
1. Start with **PROJECT_OVERVIEW.md** (15 min read)
2. Skim **QUICK_REFERENCE.md** for practical commands (5 min)
3. Read **ARCHITECTURE.md** for system understanding (30 min)
4. Reference **MODULES.md** as needed when working on specific components

### For Code Review
1. **ARCHITECTURE.md** → Understand overall design
2. **MODULES.md** → Deep dive into specific module being reviewed
3. **QUICK_REFERENCE.md** → Test the changes locally

### For Research Paper Writing
1. **PROJECT_OVERVIEW.md** → Abstract and introduction
2. **RESEARCH_FOUNDATION.md** → Related work section
3. **ARCHITECTURE.md** → Methodology section
4. **RESULTS_SUMMARY.md** → Results and discussion
5. **MODULES.md** → Implementation details appendix

### For Presentations
1. **PROJECT_OVERVIEW.md** → Slide content
2. **RESULTS_SUMMARY.md** → Results slides
3. **ARCHITECTURE.md** → System diagram slides

### For Troubleshooting
1. **QUICK_REFERENCE.md** → Troubleshooting section
2. **MODULES.md** → Specific module debugging
3. **ARCHITECTURE.md** → Understanding component interactions

---

## Documentation Principles

### 1. Completeness
Every major design decision is documented with rationale. No "magic numbers" or unexplained choices.

### 2. Accessibility
Written for multiple audiences: developers, researchers, stakeholders. Technical depth increases progressively across files.

### 3. Maintainability
Each file has a "Last Updated" timestamp. Update documentation when code changes.

### 4. Traceability
Research papers are explicitly linked to implementation choices. Every algorithm has a citation.

### 5. Practicality
Includes runnable code examples, configuration values, and troubleshooting steps.

---

## Companion Folders

### `../ai_context/`
Machine-readable documentation optimized for AI tools (JSON/YAML format). Contains the same information as this folder but structured for programmatic access.

### `../docs/`
Legacy detailed documentation. Contains original module docs, dataset descriptions, and development logs. Kept for historical reference.

### `../papers/`
29 research papers (PDFs) that validate the project's design choices. See RESEARCH_FOUNDATION.md for paper-to-component mapping.

### `../results/`
Experimental data (CSV files) and publication-ready figures (PNG). See RESULTS_SUMMARY.md for analysis.

---

## Updating Documentation

### When to Update
- **Code changes:** Update MODULES.md and ARCHITECTURE.md
- **New experiments:** Update RESULTS_SUMMARY.md
- **Configuration changes:** Update QUICK_REFERENCE.md
- **New papers added:** Update RESEARCH_FOUNDATION.md
- **Major milestones:** Update PROJECT_OVERVIEW.md status section

### How to Update
1. Edit the relevant markdown file
2. Update the "Last Updated" timestamp at the top
3. If adding new sections, update this README.md
4. Commit with descriptive message: `docs: update MODULES.md with new pathfinding algorithm`

---

## Documentation Standards

### Markdown Formatting
- Use `#` for main title, `##` for sections, `###` for subsections
- Use **bold** for emphasis, `code` for technical terms
- Use tables for structured data
- Use code blocks with language tags: ` ```python `
- Use bullet points for lists, numbered lists for sequences

### Code Examples
- Include complete, runnable examples
- Add comments explaining non-obvious logic
- Show both simple and advanced usage

### Cross-References
- Link to other documentation files: `[ARCHITECTURE.md](ARCHITECTURE.md)`
- Link to code files: `` `env/environment.py` ``
- Link to research papers: See Paper #13 in RESEARCH_FOUNDATION.md

---

## Quick Navigation

| Need | File |
|------|------|
| Project introduction | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| System design | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Module details | [MODULES.md](MODULES.md) |
| Research papers | [RESEARCH_FOUNDATION.md](RESEARCH_FOUNDATION.md) |
| Experimental results | [RESULTS_SUMMARY.md](RESULTS_SUMMARY.md) |
| Practical guide | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |

---

## Contact

For questions about this documentation:
- Check the relevant file first
- Review `../docs/dev/` for development logs
- See `QUICK_REFERENCE.md` troubleshooting section

---

**Documentation Version:** 1.0  
**Project Version:** Production-Ready Research Prototype  
**Last Major Update:** April 29, 2026
