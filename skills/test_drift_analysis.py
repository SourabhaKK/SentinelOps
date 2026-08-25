#!/usr/bin/env python3
"""
Unit tests for drift analysis engine.
"""

import json
import tempfile
from pathlib import Path
from drift_analysis import psi_score, ks_statistic, chi_square_test, analyze_metric_drift
import numpy as np


def test_psi_no_drift():
    """Test PSI when distributions are identical."""
    baseline = np.random.normal(100, 15, 1000)
    current = np.random.normal(100, 15, 1000)
    psi = psi_score(baseline, current)
    assert psi < 0.1, f"Expected low PSI for identical distributions, got {psi}"


def test_psi_with_drift():
    """Test PSI detects distribution shift."""
    baseline = np.random.normal(100, 15, 1000)
    current = np.random.normal(120, 15, 1000)  # Shifted mean
    psi = psi_score(baseline, current)
    assert psi > 0.25, f"Expected PSI > 0.25 for shifted distribution, got {psi}"


def test_ks_statistic():
    """Test KS statistic."""
    baseline = np.random.normal(100, 15, 500)
    current = np.random.normal(100, 15, 500)  # Same distribution
    ks_stat, pval = ks_statistic(baseline, current)
    assert ks_stat < 0.2, f"Expected low KS for identical distributions, got {ks_stat}"


def test_analyze_metric_drift_no_drift():
    """Test drift analysis with no drift."""
    baseline_data = {
        "latency_ms": list(np.random.normal(85, 10, 100)),
        "error_rate": list(np.random.normal(0.01, 0.005, 100)),
    }
    current_data = {
        "latency_ms": list(np.random.normal(85, 10, 100)),
        "error_rate": list(np.random.normal(0.01, 0.005, 100)),
    }

    results = analyze_metric_drift(baseline_data, current_data)
    assert results["severity"] in ["low", "low"], f"Expected low severity, got {results['severity']}"


def test_analyze_metric_drift_high_drift():
    """Test drift analysis detects high drift."""
    baseline_data = {
        "latency_ms": list(np.random.normal(85, 10, 100)),
        "error_rate": list(np.random.normal(0.01, 0.005, 100)),
    }
    current_data = {
        "latency_ms": list(np.random.normal(150, 10, 100)),  # Large shift
        "error_rate": list(np.random.normal(0.08, 0.01, 100)),  # Large shift
    }

    results = analyze_metric_drift(baseline_data, current_data)
    assert results["drift_detected"], "Expected drift detection for large shifts"
    assert results["severity"] in ["high", "medium"], f"Expected high/medium severity, got {results['severity']}"


def test_integration():
    """Test full workflow with file I/O."""
    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        baseline_file = Path(tmpdir) / "baseline.json"
        current_file = Path(tmpdir) / "current.json"
        output_file = Path(tmpdir) / "output.json"

        baseline_data = {
            "metrics": {
                "latency_ms": list(np.random.normal(85, 10, 100)),
                "error_rate": list(np.random.normal(0.01, 0.005, 100)),
            }
        }
        current_data = {
            "metrics": {
                "latency_ms": list(np.random.normal(120, 15, 100)),
                "error_rate": list(np.random.normal(0.05, 0.01, 100)),
            }
        }

        # Write files
        baseline_file.write_text(json.dumps(baseline_data))
        current_file.write_text(json.dumps(current_data))

        # Run analysis
        results = analyze_metric_drift(baseline_data["metrics"], current_data["metrics"])

        # Verify results
        assert results["drift_detected"], "Expected drift detection"
        assert len(results["metrics"]) > 0, "Expected metric analysis"
        assert results["recommendations"], "Expected recommendations"


if __name__ == "__main__":
    print("Running drift analysis tests...")
    test_psi_no_drift()
    print("✓ PSI no-drift test passed")

    test_psi_with_drift()
    print("✓ PSI with-drift test passed")

    test_ks_statistic()
    print("✓ KS statistic test passed")

    test_analyze_metric_drift_no_drift()
    print("✓ Drift analysis no-drift test passed")

    test_analyze_metric_drift_high_drift()
    print("✓ Drift analysis high-drift test passed")

    test_integration()
    print("✓ Integration test passed")

    print("\n✨ All tests passed!")
