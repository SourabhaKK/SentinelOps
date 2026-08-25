#!/usr/bin/env python3
"""
Drift Analysis Engine

Computes PSI, KS, and Chi-Square statistics for distribution drift detection.
Sandboxed skill for SentinelOps incident response agent.
"""

import json
import sys
import argparse
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Tuple


def psi_score(baseline: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    """
    Population Stability Index (PSI).

    PSI = sum((% in current - % in baseline) * ln(% current / % baseline))

    Interpretation:
    - PSI < 0.10: No significant population change
    - PSI 0.10-0.25: Small population change
    - PSI > 0.25: Significant population change
    """
    # Remove NaN and inf values
    baseline = baseline[np.isfinite(baseline)]
    current = current[np.isfinite(current)]

    if len(baseline) == 0 or len(current) == 0:
        return 0.0

    # Create bins based on baseline distribution
    breakpoints = np.percentile(baseline, np.linspace(0, 100, bins + 1))
    breakpoints[0] -= 1  # Ensure min value is included
    breakpoints[-1] += 1

    # Count values in each bin
    baseline_counts = np.histogram(baseline, bins=breakpoints)[0]
    current_counts = np.histogram(current, bins=breakpoints)[0]

    # Calculate proportions with smoothing to avoid log(0)
    baseline_prop = (baseline_counts + 1) / (baseline_counts.sum() + bins)
    current_prop = (current_counts + 1) / (current_counts.sum() + bins)

    # Compute PSI
    psi = np.sum((current_prop - baseline_prop) * np.log(current_prop / baseline_prop))
    return float(psi)


def ks_statistic(baseline: np.ndarray, current: np.ndarray) -> Tuple[float, float]:
    """
    Kolmogorov-Smirnov test.

    Tests if two samples come from the same distribution.
    Returns: (statistic, p_value)

    Interpretation:
    - KS stat > 0.3: Large difference between distributions
    - p-value < 0.05: Significant difference (reject null hypothesis)
    """
    baseline = baseline[np.isfinite(baseline)]
    current = current[np.isfinite(current)]

    if len(baseline) == 0 or len(current) == 0:
        return 0.0, 1.0

    statistic, pvalue = stats.ks_2samp(baseline, current)
    return float(statistic), float(pvalue)


def chi_square_test(baseline: np.ndarray, current: np.ndarray, bins: int = 10) -> Tuple[float, float]:
    """
    Chi-Square test for distribution difference.

    Tests if observed (current) frequencies differ significantly from expected (baseline).
    Returns: (chi_square_stat, p_value)
    """
    baseline = baseline[np.isfinite(baseline)]
    current = current[np.isfinite(current)]

    if len(baseline) == 0 or len(current) == 0:
        return 0.0, 1.0

    breakpoints = np.percentile(baseline, np.linspace(0, 100, bins + 1))
    breakpoints[0] -= 1
    breakpoints[-1] += 1

    expected = np.histogram(baseline, bins=breakpoints)[0]
    observed = np.histogram(current, bins=breakpoints)[0]

    # Chi-square test (add pseudocount to avoid division by zero)
    expected = expected + 1
    observed = observed + 1

    chi_stat = np.sum((observed - expected) ** 2 / expected)
    pvalue = 1 - stats.chi2.cdf(chi_stat, df=bins - 1)

    return float(chi_stat), float(pvalue)


def analyze_metric_drift(
    baseline_data: Dict[str, List[float]],
    current_data: Dict[str, List[float]],
    threshold_psi: float = 0.25,
    threshold_ks: float = 0.3,
) -> Dict[str, Any]:
    """
    Analyze drift in multiple metrics.

    Returns comprehensive drift analysis across all metrics.
    """
    results = {
        "drift_detected": False,
        "severity": "low",
        "metrics": {},
        "summary": {
            "psi_score": 0.0,
            "ks_statistic": 0.0,
            "chi_square": 0.0,
        },
        "thresholds_exceeded": [],
        "recommendations": [],
    }

    psi_scores = []
    ks_stats = []

    # Analyze each metric
    for metric_name in baseline_data.keys():
        if metric_name not in current_data:
            continue

        baseline = np.array(baseline_data[metric_name], dtype=float)
        current = np.array(current_data[metric_name], dtype=float)

        # Skip if insufficient data
        if len(baseline) < 5 or len(current) < 5:
            continue

        # Compute drift metrics
        psi = psi_score(baseline, current)
        ks_stat, ks_pval = ks_statistic(baseline, current)
        chi_sq, chi_pval = chi_square_test(baseline, current)

        psi_scores.append(psi)
        ks_stats.append(ks_stat)

        results["metrics"][metric_name] = {
            "psi": psi,
            "ks_statistic": ks_stat,
            "ks_pvalue": ks_pval,
            "chi_square": chi_sq,
            "chi_square_pvalue": chi_pval,
            "drift_detected": psi > threshold_psi or ks_stat > threshold_ks,
        }

        # Track which metrics exceeded thresholds
        if psi > threshold_psi:
            results["thresholds_exceeded"].append(f"PSI ({metric_name}): {psi:.3f}")
        if ks_stat > threshold_ks:
            results["thresholds_exceeded"].append(f"KS ({metric_name}): {ks_stat:.3f}")

    # Summary statistics
    if psi_scores:
        results["summary"]["psi_score"] = float(np.mean(psi_scores))
    if ks_stats:
        results["summary"]["ks_statistic"] = float(np.mean(ks_stats))

    # Determine overall drift and severity
    drift_count = sum(1 for m in results["metrics"].values() if m.get("drift_detected", False))
    total_metrics = len(results["metrics"])

    if drift_count > 0:
        results["drift_detected"] = True

        if drift_count == total_metrics:
            results["severity"] = "high"
        elif drift_count >= total_metrics * 0.5:
            results["severity"] = "medium"
        else:
            results["severity"] = "low"

    # Generate recommendations
    if results["drift_detected"]:
        if results["severity"] == "high":
            results["recommendations"].append(
                "CRITICAL: Severe drift detected in multiple metrics. Immediate investigation required."
            )
            results["recommendations"].append("Consider rollback to previous model version.")
            results["recommendations"].append("Review recent data pipeline changes.")
        elif results["severity"] == "medium":
            results["recommendations"].append(
                "Moderate drift detected. Monitor metrics closely and investigate root cause."
            )
            results["recommendations"].append("Check for data quality issues or input distribution changes.")
        else:
            results["recommendations"].append("Low-level drift detected. Continue monitoring.")

    if results["summary"]["psi_score"] > 0.4:
        results["recommendations"].append(
            f"PSI score {results['summary']['psi_score']:.2f} indicates significant population shift."
        )

    return results


def main():
    parser = argparse.ArgumentParser(description="Drift Analysis Engine")
    parser.add_argument(
        "--baseline", required=True, help="Baseline metrics JSON file"
    )
    parser.add_argument("--current", required=True, help="Current metrics JSON file")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    parser.add_argument("--threshold-psi", type=float, default=0.25, help="PSI threshold")
    parser.add_argument("--threshold-ks", type=float, default=0.3, help="KS threshold")

    args = parser.parse_args()

    try:
        # Load baseline data
        with open(args.baseline, "r") as f:
            baseline_data = json.load(f)
        if "metrics" in baseline_data:
            baseline_data = baseline_data["metrics"]

        # Load current data
        with open(args.current, "r") as f:
            current_data = json.load(f)
        if "metrics" in current_data:
            current_data = current_data["metrics"]

        # Analyze drift
        results = analyze_metric_drift(
            baseline_data,
            current_data,
            threshold_psi=args.threshold_psi,
            threshold_ks=args.threshold_ks,
        )

        # Output results
        output = json.dumps(results, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)

    except Exception as e:
        error_result = {
            "error": str(e),
            "drift_detected": False,
            "severity": "unknown",
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
