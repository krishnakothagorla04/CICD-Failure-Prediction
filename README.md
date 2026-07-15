# Intelligent CI/CD Pipeline with ML Failure Prediction

**MSc DevOps Research Project — Chinni Krishna Kothagorla, TU Dublin (Tallaght)**

A demonstration of predicting CI/CD pipeline failures **before execution** using
an interpretable machine-learning model, integrated as a gate in a real
GitHub Actions pipeline.

## Pipeline stages

```
PUSH ─► [0] PREDICT ─► [1] BUILD ─► [2] TEST ─► [3] DEPLOY
          (ML gate)    
```

* **Predict** — `predict_gate.py` computes pre-execution features of the pushed
  commit (files changed, code churn, etc.) directly from git, trains a Random
  Forest on historical CI data (`data/ci_features_sample.csv`), and prints the
  predicted **failure risk** before anything is built. This is the project's
  contribution.
* **Build / Test / Deploy** — a standard three-stage pipeline. Deploy is
  simulated (an echo step) so no external accounts are needed.

By default the gate only **warns** (the pipeline continues), matching the
"decision support, not a hard blocker" design. Pass `--block` to fail the job
on high risk.
