# Realized-force safety-envelope reproduction

Minimal numerical companion to **Realized-Force Safety Envelopes and Information-Age Admissibility for Heavy-Truck Platoons**, by Jianbo Feng, Zepeng Gao, Bingying Guo, Yanxue Wang and Zhenkun Guo.

This package regenerates the main numerical Figures 2-5, Table I, the heterogeneous force-interface comparison, the supplementary design-contract sensitivity figure/table, and the 20,000-case directional inequality check. It runs independently of the manuscript directory. Figure 1 is an illustrative diagram; the historical bridge/contact/network studies are outside this minimal analytical package.

## Run

Use **Python 3.12**, create and activate a virtual environment, then run:

```sh
python -m pip install -r requirements.txt
python -m pytest -q
python reproduce.py
```

For Windows, `python -m venv .venv` followed by `.venv\Scripts\Activate.ps1` activates the environment in PowerShell. On Linux/macOS, use `python3.12 -m venv .venv` and `source .venv/bin/activate`. No TeX installation, GPU, simulator or network connection is needed after the dependencies are installed. The complete generation run typically takes minutes; elapsed time depends on the machine.

The command creates output directories automatically, runs the five generation scripts sequentially, and validates generated data against the reference tables and output manifest. The 21 focused analytical tests retain admission boundaries, signed force projection, both braking-comparison branches, actuator margins, information intersection and continuation hypotheses.

## Output map

| Paper object | Generated files |
|---|---|
| Figure 2: displacement comparators | `figures_v5/fig2_comparison.pdf`, `results_processed_v5/comparator_curve.csv` |
| Figure 3: age admission maps | `figures_v5/fig3_v5.pdf`, `results_processed_v5/fig3_v5.csv` (3,780 rows) |
| Figure 4: emergency headway maps | `figures_v5/fig4_v5.pdf`, `results_processed_v5/fig4_v5.csv` (42,723 rows) |
| Figure 5: bounded-sensing comparison | `figures_v5/fig5_sensing.pdf`, `results_processed_v5/analytical_sensing.csv` (402 rows) |
| Main Table I and interface comparison | `tables_v5/selected_analytical_results.csv`, `tables_v5/interface_comparison.csv`, `tables_v5/table_age.tex` |
| Supplementary sensitivity | `certificate_sensitivity_v5.csv` (128 rows), `certificate_sensitivity_v5.pdf`, `tables_v5/sensitivity.tex` |
| Directional inequality check | `results_raw/force_sector_verification.csv` (20,000 rows), `results_processed_v5/analytical_summary.json` |
| Generated manuscript values | `sections/results_values.tex`, `audit/tex_value_provenance.json` |
| Reproduction checks | `audit/reproduction_verification.json` |

The checked headline results are: at 15 m/s and 110 m nominal separation, admission of the imposed 1 s age cap on level road, 0.410 s on a 3% descent, and fresh-information rejection on a 6% descent; at the heterogeneous 18 m/s reference, minimum certified emergency headways of 5.868 s, 7.577 s and 11.994 s for ideal specific force, the realized-force bound and ideal common force, respectively. These are emergency certificate requirements.

## Scientific assumptions and reproducibility

The two `src/` modules retain the manuscript's numerical equations without modification. The exact radial sector applies to the stated tire map; the directional braking bound is sufficient. Physical-domain validity, continuation and stop-hold are explicit hypotheses. Synthetic finite payload families and contract ranges are design conditions. The package supplies analytical calculations and implementation checks, not a validated closed-loop controller, empirical collision probability or string-stability result.

The physical demand cap is 8.5 times mass. The two actuator margins remain separate. Baseline jerk is 40 m/s^3, maximum lag 0.8 s, road-kinematic residual 0.15 m/s^2, demand-sector radius 0.9, age cap 1 s and nominal gap 110 m. Scenario grids and the two sensitivity references are defined explicitly in the generation scripts, rather than in an unused configuration file. Every physical sensitivity change recomputes peak closure. The deterministic force-check seed is 2026092701; randomized test seeds remain in their test source.

`reference/` contains the 27 selected cases, three interface results, all 128 sensitivity cases and manifest row counts/hashes for the larger datasets. Verification uses a relative tolerance of 1e-12 and an absolute tolerance of 1e-9 for numerical table cells; blank/rejection/NaN statuses are checked explicitly. Normalized CSV fingerprints are also reported, with line-ending differences removed. Floating-point/PDF metadata differences across platforms need not produce identical binary figures.

Version `v1.0.0` records the first public reproduction package. Cite the pinned tag when reproducing the associated manuscript revision. The repository contains numerical code and small reference tables; manuscript PDFs, author correspondence, proposal documents, prior version archives and local audit histories are not part of the release.
