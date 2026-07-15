# Intelligent CI/CD Pipeline with ML Failure Prediction

**MSc DevOps Research Project — Chinni Krishna Kothagorla, TU Dublin (Tallaght)**

A demonstration of predicting CI/CD pipeline failures **before execution** using
an interpretable machine-learning model, integrated as a gate in a real
GitHub Actions pipeline.

## Pipeline stages

```
PUSH ─► [0] PREDICT ─► [1] BUILD ─► [2] TEST ─► [3] DEPLOY
          (ML gate)      compile      pytest      (simulated)
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

## Run locally

```bash
pip install -r requirements.txt
pytest -v                      # run the tests
python predict_gate.py         # run the prediction gate on the latest commit
```

## How to use on GitHub

1. Create a new GitHub repository and push this folder to it.
2. GitHub Actions runs `.github/workflows/ci.yml` automatically on every push.
3. Open the **Actions** tab to watch Predict → Build → Test → Deploy run, and
   see the predicted failure risk in the **Predict** job log.

## Files

| Path | Purpose |
|------|---------|
| `app/calculator.py` | Tiny sample app (the pipeline is the point, not the app) |
| `tests/test_calculator.py` | Unit tests run in the Test stage |
| `predict_gate.py` | The pre-execution ML prediction gate |
| `data/ci_features_sample.csv` | Historical CI data the gate trains on |
| `.github/workflows/ci.yml` | The CI/CD pipeline definition |
