# Drift Computation Skill

Sandboxed statistical analysis for ML model distribution drift detection.

Computes PSI (Population Stability Index), KS (Kolmogorov-Smirnov), and Chi-Square statistics to detect data distribution changes.

## Language

Python 3.9+

## Dependencies

```
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
```

## Execution

```bash
python drift_analysis.py --baseline <baseline_file> --current <current_file> --output <output_file>
```

## Input Format

JSON files with metric arrays:

```json
{
  "metrics": {
    "latency_ms": [85.2, 92.1, 88.5, ...],
    "error_rate": [0.008, 0.009, 0.007, ...],
    "throughput": [850, 920, 880, ...]
  }
}
```

## Output Format

```json
{
  "drift_detected": true,
  "severity": "high",
  "psi_score": 0.45,
  "ks_statistic": 0.38,
  "chi_square": 125.6,
  "metrics_analyzed": ["latency_ms", "error_rate", "throughput"],
  "threshold_exceeded": ["psi", "ks"],
  "recommendations": [
    "High PSI detected in latency distribution",
    "KS test significant at p<0.05",
    "Consider rollback or investigation"
  ]
}
```

## Thresholds

- **PSI > 0.25**: Moderate drift detected
- **PSI > 0.4**: Severe drift
- **KS statistic > 0.3**: Significant distribution change
- **Chi-Square p-value < 0.05**: Reject null hypothesis (distribution changed)
