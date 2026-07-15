"""
predict_gate.py
========================================================================
PRE-EXECUTION FAILURE PREDICTION GATE
  Research Project: "Enhancing CI/CD Pipelines with Machine Learning for
  Predicting Failures Before Execution" - Chinni Krishna Kothagorla, TU Dublin

This is the novel step of the pipeline. It runs BEFORE build/test/deploy.
When a developer pushes a commit, it:
  1. Computes pre-execution features of THAT commit straight from git
     (files changed, code churn, etc.) - nothing that needs the build to run.
  2. Trains an interpretable model (Random Forest) on historical CI data
     (bundled sample in data/ci_features_sample.csv).
  3. Predicts the probability that this commit's pipeline will FAIL.
  4. Prints a clear risk warning. By default it only WARNS (exit 0) so the
     pipeline continues - matching the "decision support, not a blocker"
     design. Use --block to fail the job when risk is high.

Run locally:
  python predict_gate.py
  python predict_gate.py --threshold 0.5 --block
"""

import argparse
import subprocess
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

TRAIN_CSV = "data/ci_features_sample.csv"


def git(args):
    """Run a git command, return stdout as text ('' on failure)."""
    try:
        return subprocess.check_output(["git"] + args, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def commit_features(feature_names, medians):
    """Build a one-row feature vector for the current commit from git.
    Anything we can't derive from git is filled with the training median."""
    feats = dict(medians)  # start from medians, then override what we know

    # diff of the latest commit vs its parent (numstat = added, deleted, path)
    numstat = git(["diff", "--numstat", "HEAD~1", "HEAD"])
    src_churn = test_churn = 0
    files = src_files = doc_files = 0
    if numstat:
        for line in numstat.splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            added, deleted, path = parts
            add = int(added) if added.isdigit() else 0
            dele = int(deleted) if deleted.isdigit() else 0
            churn = add + dele
            files += 1
            p = path.lower()
            if "test" in p:
                test_churn += churn
            else:
                src_churn += churn
            if p.endswith((".md", ".rst", ".txt")):
                doc_files += 1
            elif p.endswith((".py", ".js", ".java", ".go", ".rb", ".ts")):
                src_files += 1

    known = {
        "src_churn": src_churn, "test_churn": test_churn,
        "files_modified": files, "src_files": src_files, "doc_files": doc_files,
        "num_commits": 1,
    }
    for k, v in known.items():
        if k in feats:
            feats[k] = v
    return pd.DataFrame([[feats[c] for c in feature_names]], columns=feature_names)


def main():
    ap = argparse.ArgumentParser(description="Pre-execution CI failure prediction gate")
    ap.add_argument("--threshold", type=float, default=0.5,
                    help="risk above this is flagged as high")
    ap.add_argument("--block", action="store_true",
                    help="exit non-zero (fail the job) when risk is high")
    args = ap.parse_args()

    print("=" * 60)
    print(" PRE-EXECUTION FAILURE PREDICTION GATE")
    print("=" * 60)

    # 1. train on historical data
    df = pd.read_csv(TRAIN_CSV)
    feature_names = [c for c in df.columns if c != "target"]
    X = df[feature_names].fillna(df[feature_names].median())
    y = df["target"].astype(int)
    medians = X.median().to_dict()

    scaler = StandardScaler().fit(X)
    model = RandomForestClassifier(n_estimators=200, random_state=42,
                                   class_weight="balanced", n_jobs=-1)
    model.fit(scaler.transform(X), y)

    # 2. features of the current commit
    commit = git(["rev-parse", "--short", "HEAD"]) or "(unknown)"
    msg = git(["log", "-1", "--pretty=%s"]) or "(no message)"
    xrow = commit_features(feature_names, medians)

    # 3. predict failure probability
    prob = float(model.predict_proba(scaler.transform(xrow))[0, 1])

    print("Commit      : %s  \"%s\"" % (commit, msg))
    print("Files changed: %d | src churn: %d | test churn: %d"
          % (int(xrow["files_modified"][0]) if "files_modified" in xrow else 0,
             int(xrow["src_churn"][0]) if "src_churn" in xrow else 0,
             int(xrow["test_churn"][0]) if "test_churn" in xrow else 0))
    print("-" * 60)
    print(" PREDICTED FAILURE RISK: %.1f%%" % (prob * 100))

    if prob >= args.threshold:
        print(" STATUS: HIGH RISK  - review this commit before the pipeline runs.")
        if args.block:
            print(" (--block set: failing the gate)")
            sys.exit(1)
    else:
        print(" STATUS: LOW RISK   - safe to proceed to build/test/deploy.")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
