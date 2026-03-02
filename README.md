# EUCLID — Linear Viscoelasticity 2D

**Automated identification of linear viscoelastic Prony series parameters from full-field displacement measurements.**

This repository implements the EUCLID (Efficient Unsupervised Constitutive Law Identification and Discovery) framework applied to 2D linear viscoelasticity. Given displacement field data (from FEM simulation or DIC experiments), the pipeline identifies the Prony series parameters (G_i, K_i, τ_i) that characterize the material's time-dependent response.

---

## Repository Structure

```
EUCLID_Lin_viscoelasticity_2D/
│
├── Forward_solver/              # FEM forward problem: generate synthetic displacement data
│   ├── core/                    # FEM modules (material, mesh, assembly, solver, time integration)
│   ├── configs/                 # Geometry configurations for complex specimens
│   ├── run_simulation.py        # MAIN SCRIPT: run a forward FEM simulation
│   └── run_verification.py      # Verification against known solutions
│
├── inverse_problem/             # Inverse problem: identify Prony parameters
│   ├── core/                    # Inverse modules (data, geometry, history, assembly, solver,
│   │                            #   clustering, visualization, boundary conditions)
│   ├── preprocessing/           # Preprocessing for real DIC data
│   │   ├── unified_preprocessor.py   # Convert DIC output to FEM-compatible format
│   │   └── dic_data_analysis.py      # DIC data quality analysis
│   ├── Postprocessing/          # Output directory (results + figures written here)
│   ├── Real_data/               # Place raw DIC experiment data here
│   ├── run_experiment.py        # MAIN SCRIPT: run the inverse identification
│   ├── inverse_problem.py       # Core orchestrator class
│   ├── plot_relaxation_curves.py  # Plot G(t), K(t) vs ground truth
│   ├── plot_prony_comparison.py   # Bar chart: identified vs ground truth Prony terms
│   └── read_results_npz.py        # Utility to inspect saved results
│
├── standard_FE_dataset/         # Centralized data store (input to inverse solver)
│   ├── 800/                     # Synthetic: rectangular specimen, coarse mesh (5×13 nodes)
│   └── 900/                     # Real: PA6 specimen, preprocessed from DIC
│
├── requirements.txt
└── README.md
```

---

## Installation

**Python 3.8+ required**

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
cd Forward_solver
python -c "from core.material import ViscoelasticMaterial; print('Forward solver ready')"

cd ../inverse_problem
python -c "from inverse_problem import InverseProblem; print('Inverse solver ready')"
```

---

## Workflow 1: Synthetic Data (Forward → Inverse)

### Step 1: Generate Synthetic Data

```bash
cd Forward_solver
python run_simulation.py
```

Edit `run_simulation.py` to configure the experiment:

```python
experiment_id = 800      # Output folder name in standard_FE_dataset/
nx = 5                   # Mesh nodes in X direction
ny = 13                  # Mesh nodes in Y direction
n_timesteps = 600        # Number of time steps
dt = 0.5                 # Time step size [s]
load = 50.0              # Applied load [N/mm]
```

**Output:** `standard_FE_dataset/800/` containing:
- `U.csv` — displacement field [2*nNodes × nTime]
- `F.csv` — boundary forces [4 × nTime]
- `coord.csv` — node coordinates
- `conne.txt` — element connectivity
- `time.csv` — time vector
- `ground_truth_material.txt` — true Prony parameters (for validation)

### Step 2: Run Inverse Identification

```bash
cd inverse_problem
python run_experiment.py
```

Edit `run_experiment.py` to configure:

```python
EXPERIMENT_NUMBER = 800   # Reads from standard_FE_dataset/800/
N_MAXWELL_SHEAR = 150     # Number of shear Prony terms (nG)
N_MAXWELL_BULK = 150      # Number of bulk Prony terms (nK)
TAU_MIN = 1.0             # Min relaxation time [s]
TAU_MAX = 600.0           # Max relaxation time [s]
LAMBDA_INTERIOR = 0.0     # Interior equation weight (0=off for synthetic data)
LAMBDA_BOUNDARY = 1.0     # Boundary equation weight
APPLY_CLUSTERING = True   # Merge similar relaxation times
```

**Output:** `inverse_problem/Postprocessing/final_outputs/800_.../`
- `results.npz` — identified parameters
- `figures/` — 9 diagnostic plots

### Step 3: Plot Results

```bash
cd inverse_problem
python plot_relaxation_curves.py   # G(t), K(t) comparison
python plot_prony_comparison.py    # Bar chart vs ground truth
```

---

## Workflow 2: Real DIC Data (Preprocess → Inverse)

### Step 1: Preprocess DIC Data

Place raw DIC CSV files in `inverse_problem/Real_data/experiments/`.

```bash
cd inverse_problem/preprocessing
python unified_preprocessor.py
```

This converts DIC output to FEM-compatible format and writes to `standard_FE_dataset/900/`.

### Step 2: Run Inverse Identification

```bash
cd inverse_problem
python run_experiment.py
```

Set in `run_experiment.py`:

```python
EXPERIMENT_NUMBER = 900
LAMBDA_INTERIOR = 1.0    # Use interior equations for real data
LAMBDA_BOUNDARY = 1.0
```

---

## Scientific Background

### Prony Series Model

Linear viscoelastic materials are characterized by time-dependent relaxation moduli:

```
G(t) = G_inf + sum_i G_i * exp(-t / tau_i)    [Shear]
K(t) = K_inf + sum_i K_i * exp(-t / tau_i)    [Bulk]
```

Where:
- `G(t)`, `K(t)`: Relaxation moduli [MPa]
- `G_inf`, `K_inf`: Equilibrium (long-time) moduli [MPa]
- `G_i`, `K_i`: Prony coefficients [MPa]
- `tau_i`: Relaxation times [s]

### Inverse Problem Formulation

Given full-field displacement measurements `u(x,t)`, identify `{G_i, K_i, tau_i}` by solving:

```
Minimize  ||A * p - R||^2
Subject to  p >= 0

Where:
  p = [G_1, ..., G_nG, K_1, ..., K_nK]   (Prony amplitudes)
  A = system matrix (assembled from history variables beta_i)
  R = displacement residuals
```

**Solution method:** Non-Negative Least Squares (NNLS) with logarithmically spaced relaxation times, followed by clustering to identify dominant Prony terms.

### Ground Truth Material (MAT3.5 — used in synthetic experiments)

```
G_prony = [200, 500, 1000] MPa,   tau_G = [5.3, 50.1, 400.2] s,   G_inf = 1500 MPa
K_prony = [500, 700,  567] MPa,   tau_K = [5.3, 50.1, 400.2] s,   K_inf = 2000 MPa
```

---

## Dataset Description

| Exp | Type | Geometry | Mesh | Purpose |
|-----|------|----------|------|---------|
| 800 | Synthetic | Rectangle 20×60 mm | 5×13 nodes (structured) | Baseline — coarse mesh |
| 900 | Real (DIC) | Rectangle ~20×60 mm | DIC-mapped nodes | PA6 polymer validation |

---

## Key Parameters Reference

### Forward Solver (`run_simulation.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `experiment_id` | 800 | Output folder ID |
| `width` / `height` | 20 / 60 mm | Domain dimensions |
| `nx` / `ny` | 5 / 13 | Structured mesh density |
| `dt` | 0.5 s | Time step |
| `n_timesteps` | 600 | Total time steps |
| `load` | 50 N/mm | Applied distributed load |

### Inverse Problem (`run_experiment.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EXPERIMENT_NUMBER` | 800 | Dataset to read |
| `N_MAXWELL_SHEAR/BULK` | 150 | Number of Prony terms |
| `TAU_MIN` / `TAU_MAX` | 1 / 600 s | Relaxation time range |
| `LAMBDA_INTERIOR` | 0.0 | Interior equation weight |
| `LAMBDA_BOUNDARY` | 1.0 | Boundary equation weight |
| `APPLY_CLUSTERING` | True | Merge similar tau values |
| `CLUSTERING_RANGE` | 0.3 | Merging threshold (30%) |

**Recommended settings:**
- Synthetic data: `LAMBDA_INTERIOR=0.0, LAMBDA_BOUNDARY=1.0`
- Real DIC data: `LAMBDA_INTERIOR=1.0, LAMBDA_BOUNDARY=1.0`

---

## Output Files

### `results.npz` — identified parameters

```python
import numpy as np
data = np.load('results.npz', allow_pickle=True)

# All Prony terms (including zeros)
G_params = data['G_params']      # [nG] shear amplitudes [MPa]
tau_G    = data['tau_G']         # [nG] relaxation times [s]

# Dominant terms after clustering
G_nonzero     = data['G_nonzero']
tau_G_nonzero = data['tau_G_nonzero']

# Equilibrium moduli
G_inf = data['G_inf']
K_inf = data['K_inf']
```

### Diagnostic Plots (9 figures in `figures/`)

1. Input displacement and force data
2. Mesh quality (node distribution, connectivity)
3. History variable (beta) snapshots
4. Displacement residuals
5. Force residuals
6. All 150 identified Prony parameters
7. Clustering before/after comparison
8. Relaxation curves G(t), K(t)
9. Prony spectrum bar chart

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'core'`**
Run scripts from their own directory:
```bash
cd Forward_solver    # then run forward scripts
cd inverse_problem   # then run inverse scripts
```

**`FileNotFoundError: standard_FE_dataset/800`**
Generate data first with `Forward_solver/run_simulation.py`.

**Too few Prony terms after clustering**
Reduce `CLUSTERING_RANGE` from 0.3 to 0.2, or increase `N_MAXWELL_SHEAR` to 200.

**Large displacement residuals (>10%)**
Try switching `BOUNDARY_CONDITION = 'BottomForceBC'`, or expand `TAU_MAX` to 1000.

---

## Citation

If you use this code in your research, please cite:

```bibtex
@software{euclid_lin_viscoelasticity_2d,
  title  = {EUCLID -- Linear Viscoelasticity 2D},
  author = {Undamatla, Kali Satya Sri Charan},
  year   = {2025},
  note   = {Prony series identification from full-field displacement data using NNLS optimization}
}
```

---

**Python 3.8+ | numpy | scipy | matplotlib | scikit-learn | pygmsh | gmsh**
