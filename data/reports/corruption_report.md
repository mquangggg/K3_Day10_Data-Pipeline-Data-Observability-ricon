# Corruption & Recovery Impact Report

## 1. Metric Comparison Overview

| State | Retrieval Hit Rate | Mean Token F1 | Quality Passed | Freshness Status |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline** | 1.0000 | 0.0623 | True | Fresh |
| **Corrupted** | 0.8000 | 0.0554 | False | True |
| **Repaired** | 1.0000 | 0.0623 | True | True |

## 2. Impact Analysis
- **Impact of Corruption (Delta Hit Rate):** -0.2000
- **Recovery Effect (Delta Hit Rate Repaired vs Corrupted):** +0.2000

## 3. Conclusion
- Repairing clean dataset directly from reliable raw source restores data observability signals and evaluation metrics back to baseline level.
