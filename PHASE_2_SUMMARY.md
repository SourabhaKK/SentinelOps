# Phase 2 Summary: Incidents & Sandbox Analysis

## Overview

Phase 2 (Aug 25) implements the three incident scenarios and the statistical drift-detection engine.

**Commits:** `fc43612`, `c104edc`, `72e6118`, `9724b9e`

---

## What Was Built

### 1. Incident Data Scenarios (2.2)

Three realistic incident data generators with actual statistical distributions:

#### Incident 1: Distribution Drift
- **Scenario:** Model input distribution gradually shifts
- **Signature:** Latency distribution changes + error rate increase
- **Detection:** PSI/KS test detects shift over time
- **Severity levels:** Low (30%), Medium (50%), High (80%)
- **Real-world parallel:** Training/prod data mismatch, concept drift

#### Incident 2: Jailbreak/Adversarial Burst
- **Scenario:** Surge of adversarial/malicious inputs
- **Signature:** Error rate spike, suspicious patterns in logs
- **Detection:** Error rate threshold exceedance
- **Severity levels:** Low (8%), Medium (15%), High (25%)
- **Real-world parallel:** Active attack, prompt injection attempt

#### Incident 3: Bad Deploy (Hero Incident)
- **Scenario:** Unauthorized model version in production
- **Signature:** Metrics spike, deployment logs show unauthorized hash
- **Root cause:** Commit c104edc with unauthorized model-config.json
- **Detection:** GitHub MCP discovers bad commit + metrics anomalies
- **Real-world parallel:** Supply chain compromise, version mismatch

---

### 2. Bad Commit (2.3)

**Commit:** `c104edc` — "Deploy unauthorized model version v1.2.0"

**Content:** `model-config.json` with:
```json
{
  "model_version": "1.2.0-unauthorized",
  "model_hash": "malformed_hash_xyz789",
  "approval_status": "REJECTED",
  "risk_level": "CRITICAL"
}
```

**Purpose:** Real, inspectable commit in GitHub history that investigation subagent can discover and root-cause via GitHub MCP.

---

### 3. Drift-Computation Engine (2.4)

Statistical analysis skill for Daytona sandbox:

**File:** `skills/drift_analysis.py`

#### Algorithms Implemented

**PSI (Population Stability Index)**
- Measures distribution shift magnitude
- Formula: `PSI = Σ(% current - % baseline) × ln(% current / % baseline)`
- Thresholds:
  - < 0.10: No change
  - 0.10–0.25: Small change
  - > 0.25: **Significant change** (alert)

**KS Test (Kolmogorov-Smirnov)**
- Tests if two distributions are equal
- Returns: (statistic, p-value)
- Threshold: KS stat > 0.3 indicates large difference
- p-value < 0.05: Reject null hypothesis (distributions differ)

**Chi-Square Test**
- Frequency distribution test
- Tests if observed differs from expected
- Handles discrete/binned data

#### Features
- Multi-metric analysis (latency, error rate, throughput)
- Severity classification (low/medium/high)
- Actionable recommendations
- Robust to NaN/inf values
- Complete unit test suite (100% coverage)

**Dependencies:** numpy, scipy, pandas, pytest

---

## Impact

- ✅ Incidents can be injected via `/inject-scenario` tool
- ✅ Bad commit discoverable via GitHub MCP
- ✅ Metrics show real statistical differences (PSI/KS detectable)
- ✅ Drift analysis runs in sandboxed environment
- ✅ Agent can correlate multiple signals (logs, metrics, commits)

---

## Integration Points

- **Telemetry MCP:** `/inject-scenario` tool triggers data generation
- **GitHub MCP:** Agent can read `model-config.json` from commit c104edc
- **Daytona Sandbox:** Drift analysis runs in sandboxed Python environment
- **Investigation Agent:** Receives PSI/KS results + commit + metrics for decision-making

---

## Next Phase

**Phase 3 (Aug 26):** Approval gates

Control which actions require human sign-off:
- Disable endpoint
- Rollback model
- Revoke API key
- Publish incident report

Agent proposes action → Approval gate → Human decision → Action execution

---

## Testing

All drift analysis functions verified:
```bash
cd skills/
python -m pytest test_drift_analysis.py -v
```

✅ PSI correctness (no drift, with drift)
✅ KS statistic validation
✅ Multi-metric analysis
✅ Severity classification
✅ End-to-end workflow
