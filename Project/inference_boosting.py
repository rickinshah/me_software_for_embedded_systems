"""
inference_boosting.py
=====================
Standalone inference script for the three saved boosting models.

Usage:
  python inference_boosting.py                        # 10 random samples (different every run)
  python inference_boosting.py --n 25                 # 25 random samples
  python inference_boosting.py --seed 7               # pin seed for reproducibility
  python inference_boosting.py --model xgb            # only XGBoost
  python inference_boosting.py --model lgb --n 20     # LightGBM, 20 samples
  python inference_boosting.py --csv my_cars.csv      # predict from a custom CSV

Note: The seed used is always printed — pass it as --seed <N> to reproduce
      the exact same sample in a later run.

Requirements:
  • used_cars.csv must be in the current directory (for random sampling)
  • Run  `python save_boosting_models.py`  first to generate ./models/

Price class bins (same as training):
  Budget    :  < $15,000
  Mid-range :  $15,000 – $30,000
  Premium   :  $30,000 – $55,000
  Luxury    :  > $55,000
"""

import argparse
import os
import sys
import time

import joblib
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
MODEL_DIR = "models"
DATA_FILE = "used_cars.csv"

# ── Feature lists (must match training exactly) ────────────────────────────────
NUMERIC_FEATURES = [
    "mileage_num", "horsepower", "displacement", "car_age", "model_year",
    "has_accident", "clean_title_flag", "is_automatic",
    "num_cylinders", "has_turbo", "is_electric", "hp_per_liter",
    "trans_speeds",
]
CATEGORICAL_FEATURES = ["brand", "model", "fuel_type"]
ALL_FEATURES          = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# ── Price bin boundaries (must match training) ─────────────────────────────────
PRICE_BINS   = [0, 15_000, 30_000, 55_000, float("inf")]
PRICE_LABELS = ["Budget", "Mid-range", "Premium", "Luxury"]

PRICE_RANGES = {
    "Budget":    "< $15,000",
    "Mid-range": "$15,000 – $30,000",
    "Premium":   "$30,000 – $55,000",
    "Luxury":    "> $55,000",
}


def price_to_class(price: float) -> str:
    """Map a numeric price to its class label using the training bins."""
    for i, upper in enumerate(PRICE_BINS[1:]):
        if price < upper:
            return PRICE_LABELS[i]
    return PRICE_LABELS[-1]


# ──────────────────────────────────────────────────────────────────────────────
# Full preprocessing — mirrors save_boosting_models.py exactly
# ──────────────────────────────────────────────────────────────────────────────
def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies all feature-engineering steps to the raw used_cars.csv DataFrame.
    Returns a DataFrame that contains ALL_FEATURES + 'actual_price' + 'actual_class'.
    """
    d = df.copy()

    # ── Price ─────────────────────────────────────────────────────────────────
    d["actual_price"] = (
        d["price"]
        .str.replace(r"[$,]", "", regex=True)
        .astype(float)
    )

    # ── Mileage ───────────────────────────────────────────────────────────────
    d["mileage_num"] = (
        d["milage"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+)")[0]
        .astype(float)
    )

    # ── Engine features ───────────────────────────────────────────────────────
    d["horsepower"]   = d["engine"].str.extract(r"(\d+\.?\d*)HP")[0].astype(float)
    d["displacement"] = d["engine"].str.extract(r"(\d+\.?\d*)L")[0].astype(float)
    d["num_cylinders"] = d["engine"].str.extract(r"(\d+)\s*Cylinder")[0].astype(float)
    d["has_turbo"]    = d["engine"].str.contains("Turbo|Turbocharged", case=False, na=False).astype(int)
    d["is_electric"]  = d["engine"].str.contains("Electric", case=False, na=False).astype(int)
    d["hp_per_liter"] = d["horsepower"] / d["displacement"].replace(0, float("nan"))

    # ── Car age ───────────────────────────────────────────────────────────────
    d["car_age"] = 2025 - d["model_year"]

    # ── Accident / title ─────────────────────────────────────────────────────
    d["has_accident"]     = d["accident"].str.contains("accident", case=False, na=False).astype(int)
    d["clean_title_flag"] = (d["clean_title"] == "Yes").astype(int)

    # ── Transmission ─────────────────────────────────────────────────────────
    d["is_automatic"] = (
        d["transmission"].str.contains("A/T|Automatic|CVT|DCT", case=False, na=False).astype(int)
    )
    d["trans_speeds"] = d["transmission"].str.extract(r"(\d+)-Speed")[0].astype(float)

    # ── Actual class ──────────────────────────────────────────────────────────
    d["actual_class"] = d["actual_price"].apply(price_to_class)

    return d


def load_random_samples(n: int, seed: int | None) -> pd.DataFrame:
    """
    Loads used_cars.csv, preprocesses it, drops rows with missing price or
    target features, then returns n stratified-random rows — one per class
    where possible, otherwise fully random.

    If seed is None a random seed is drawn from OS entropy; the seed
    actually used is always printed so the run can be reproduced.
    """
    if not os.path.exists(DATA_FILE):
        sys.exit(
            f"\n❌  Dataset not found: {DATA_FILE}\n"
            "    Make sure used_cars.csv is in the current directory.\n"
        )

    # Resolve seed: None → fresh OS-entropy seed
    if seed is None:
        seed = int.from_bytes(os.urandom(4), "big")
    print(f"\n📂  Loading dataset from {DATA_FILE} …")
    print(f"    Random seed       : {seed}  (re-run with --seed {seed} to reproduce)")
    raw = pd.read_csv(DATA_FILE)
    print(f"    Total rows in CSV : {len(raw):,}")

    data = preprocess_dataset(raw)

    # Drop rows missing price or key model features
    required = ALL_FEATURES + ["actual_price", "actual_class"]
    data = data.dropna(subset=["actual_price"] + ["mileage_num", "horsepower"])
    data = data[data["actual_price"] > 0]

    print(f"    Usable rows       : {len(data):,}")
    print(f"    Class distribution:\n{data['actual_class'].value_counts().to_string()}")

    # Stratified sample: try to take ≥1 from each class, fill rest randomly
    rng     = np.random.default_rng(seed)
    classes = PRICE_LABELS

    per_class = max(1, n // len(classes))
    sampled_idx = []

    for cls in classes:
        cls_idx = data[data["actual_class"] == cls].index.tolist()
        k = min(per_class, len(cls_idx))
        sampled_idx.extend(rng.choice(cls_idx, size=k, replace=False).tolist())

    # Fill remaining quota randomly from the rest of the dataset
    remaining_needed = n - len(sampled_idx)
    if remaining_needed > 0:
        leftover = data.index.difference(sampled_idx).tolist()
        extra = rng.choice(
            leftover, size=min(remaining_needed, len(leftover)), replace=False
        )
        sampled_idx.extend(extra.tolist())

    sample = data.loc[sampled_idx].reset_index(drop=True)
    print(f"\n🎲  Randomly sampled {len(sample)} rows.")
    return sample


# ──────────────────────────────────────────────────────────────────────────────
# Feature engineering for custom CSV (no price column)
# ──────────────────────────────────────────────────────────────────────────────
def engineer_features(raw: pd.DataFrame) -> pd.DataFrame:
    """Convert a raw-column DataFrame to the engineered feature DataFrame."""
    if set(ALL_FEATURES).issubset(raw.columns):
        return raw[ALL_FEATURES].copy()

    d = raw.copy()

    if "mileage_num" not in d.columns:
        d["mileage_num"] = (
            d["milage"].astype(str)
            .str.replace(",", "", regex=False)
            .str.extract(r"(\d+)")[0].astype(float)
        )
    if "horsepower" not in d.columns:
        d["horsepower"] = d["engine"].str.extract(r"(\d+\.?\d*)HP")[0].astype(float)
    if "displacement" not in d.columns:
        d["displacement"] = d["engine"].str.extract(r"(\d+\.?\d*)L")[0].astype(float)
    if "num_cylinders" not in d.columns:
        d["num_cylinders"] = d["engine"].str.extract(r"(\d+)\s*Cylinder")[0].astype(float)
    if "has_turbo" not in d.columns:
        d["has_turbo"] = d["engine"].str.contains("Turbo|Turbocharged", case=False, na=False).astype(int)
    if "is_electric" not in d.columns:
        d["is_electric"] = d["engine"].str.contains("Electric", case=False, na=False).astype(int)
    if "hp_per_liter" not in d.columns:
        d["hp_per_liter"] = d["horsepower"] / d["displacement"].replace(0, float("nan"))
    if "car_age" not in d.columns:
        d["car_age"] = 2025 - d["model_year"].astype(int)
    if "has_accident" not in d.columns:
        d["has_accident"] = d["accident"].str.contains("accident", case=False, na=False).astype(int)
    if "clean_title_flag" not in d.columns:
        d["clean_title_flag"] = (d["clean_title"] == "Yes").astype(int)
    if "is_automatic" not in d.columns:
        d["is_automatic"] = (
            d["transmission"].str.contains("A/T|Automatic|CVT|DCT", case=False, na=False).astype(int)
        )
    if "trans_speeds" not in d.columns:
        d["trans_speeds"] = d["transmission"].str.extract(r"(\d+)-Speed")[0].astype(float)

    return d[ALL_FEATURES].copy()


# ──────────────────────────────────────────────────────────────────────────────
# Load saved model artefacts
# ──────────────────────────────────────────────────────────────────────────────
def load_models(model_choice: str):
    def _load(name):
        path = os.path.join(MODEL_DIR, name)
        if not os.path.exists(path):
            sys.exit(
                f"\n❌  Model file not found: {path}\n"
                "    Please run  `python save_boosting_models.py`  first.\n"
            )
        return joblib.load(path)

    le          = _load("label_encoder.joblib")
    class_names = _load("class_names.joblib")

    pipelines = {}
    if model_choice in ("xgb", "all"):
        pipelines["XGBoost"]          = (_load("xgb_pipeline.joblib"), True)
    if model_choice in ("lgb", "all"):
        pipelines["LightGBM"]         = (_load("lgb_pipeline.joblib"), True)
    if model_choice in ("gb", "all"):
        pipelines["GradientBoosting"] = (_load("gb_pipeline.joblib"),  False)

    return pipelines, le, class_names


# ──────────────────────────────────────────────────────────────────────────────
# Run predictions
# ──────────────────────────────────────────────────────────────────────────────
def predict(X: pd.DataFrame, pipelines, le, class_names):
    """
    Returns (results_df, infer_times) where infer_times is a dict
    mapping model_name -> seconds taken for predict_proba + predict.
    """
    results     = []
    infer_times = {}

    for model_name, (pipeline, use_encoded) in pipelines.items():
        t0    = time.perf_counter()
        proba = pipeline.predict_proba(X)
        if use_encoded:
            str_preds = le.inverse_transform(pipeline.predict(X))
        else:
            str_preds = pipeline.predict(X)
        infer_times[model_name] = time.perf_counter() - t0

        for i, (pred, prob_row) in enumerate(zip(str_preds, proba)):
            prob_dict = {f"P({c})": f"{p:.1%}" for c, p in zip(class_names, prob_row)}
            results.append({
                "sample"     : i + 1,
                "model"      : model_name,
                "prediction" : pred,
                "confidence" : f"{prob_row.max() * 100:.1f}%",
                **prob_dict,
            })

    return pd.DataFrame(results), infer_times


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def fmt_price(p: float) -> str:
    return f"${p:,.0f}"

def fmt_correct(pred: str, actual: str) -> str:
    return "Yes" if pred == actual else "No"


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Inference with saved boosting models on used-car price classification."
    )
    parser.add_argument(
        "--model", choices=["xgb", "lgb", "gb", "all"], default="all",
        help="Which model(s) to run  (default: all)."
    )
    parser.add_argument(
        "--n", type=int, default=10,
        help="Number of random samples to draw from used_cars.csv  (default: 10)."
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Pin the random seed for reproducibility. Omit for a different sample every run."
    )
    parser.add_argument(
        "--csv", default=None,
        help=(
            "Path to a custom CSV (same schema as used_cars.csv). "
            "Add an 'actual_price' column to get accuracy reporting. "
            "If omitted, random samples are drawn from used_cars.csv."
        ),
    )
    args = parser.parse_args()

    # ── Load models ──────────────────────────────────────────────────────────
    print(f"\n📦  Loading model(s): {args.model} …")
    pipelines, le, class_names = load_models(args.model)
    print(f"    Classes : {class_names}")

    # ── Prepare input data ───────────────────────────────────────────────────
    has_actuals = False

    if args.csv:
        if not os.path.exists(args.csv):
            sys.exit(f"❌  CSV not found: {args.csv}")
        raw = pd.read_csv(args.csv)
        print(f"\n📄  Loaded {len(raw)} row(s) from {args.csv}")
        if "actual_price" in raw.columns:
            raw["actual_class"] = raw["actual_price"].apply(price_to_class)
            has_actuals = True
        X = engineer_features(raw)
    else:
        # ── Random samples from used_cars.csv ─────────────────────────────
        sample_df = load_random_samples(n=args.n, seed=args.seed)
        X         = sample_df[ALL_FEATURES].copy()
        raw       = sample_df          # carries actual_price + actual_class
        has_actuals = True

    # ── Run inference ────────────────────────────────────────────────────────
    print("\n⚙️   Running inference …\n")
    results, infer_times = predict(X, pipelines, le, class_names)

    # Readable car label
    if "brand" in raw.columns and "model" in raw.columns:
        car_labels = (raw["brand"] + " " + raw["model"].str[:26]).tolist()
    else:
        car_labels = [f"Car {i + 1}" for i in range(len(raw))]

    results.insert(1, "car", results["sample"].apply(lambda s: car_labels[s - 1]))

    # Attach actuals
    if has_actuals:
        actual_prices  = raw["actual_price"].tolist()
        actual_classes = raw["actual_class"].tolist()
        results["actual_price"] = results["sample"].apply(lambda s: fmt_price(actual_prices[s - 1]))
        results["actual_class"] = results["sample"].apply(lambda s: actual_classes[s - 1])
        results["correct?"]     = results.apply(
            lambda r: fmt_correct(r["prediction"], r["actual_class"]), axis=1
        )

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 30)

    model_names = results["model"].unique()

    # ── Per-model table ──────────────────────────────────────────────────────
    for mname in model_names:
        sub = results[results["model"] == mname].copy()
        print("=" * 100)
        print(f"  MODEL : {mname}")
        print("=" * 100)

        display_cols = ["sample", "car"]
        if has_actuals:
            display_cols += ["actual_price", "actual_class"]
        display_cols += ["prediction", "confidence"]
        if has_actuals:
            display_cols += ["correct?"]
        display_cols += [c for c in sub.columns if c.startswith("P(")]

        print(sub[display_cols].to_string(index=False))

        if has_actuals:
            n_correct = (sub["correct?"] == "Yes").sum()
            n_total   = len(sub)
            print(f"\n  Sample accuracy : {n_correct}/{n_total}  ({n_correct / n_total * 100:.0f}%)")
        print()

    # ── Side-by-side summary ─────────────────────────────────────────────────
    if len(model_names) > 1:
        print("=" * 100)
        print("  SIDE-BY-SIDE SUMMARY")
        print("=" * 100)

        idx_cols = ["sample", "car"]
        if has_actuals:
            idx_cols += ["actual_price", "actual_class"]

        pivot = (
            results
            .pivot_table(index=idx_cols, columns="model",
                         values="prediction", aggfunc="first")
            .reset_index()
        )
        pivot.columns.name = None

        if has_actuals:
            for mname in model_names:
                pivot[f"{mname} ✓?"] = pivot.apply(
                    lambda r, m=mname: fmt_correct(r[m], r["actual_class"]), axis=1
                )

        print(pivot.to_string(index=False))
        print()

        if has_actuals:
            print("─" * 100)
            print("  ACCURACY PER MODEL (on this sample):")
            for mname in model_names:
                n_correct = (pivot[f"{mname} ✓?"] == "Yes").sum()
                n_total   = len(pivot)
                print(f"  {mname:<22} : {n_correct}/{n_total}  ({n_correct / n_total * 100:.0f}%)")
            print()

    print("\n✅  Inference complete!")

    # ── Inference time summary ───────────────────────────────────────────────
    n_samples = len(X)
    print()
    print("=" * 55)
    print("  ⏱  INFERENCE TIME SUMMARY")
    print("=" * 55)
    print(f"  {'Model':<22}  {'Total':>8}  {'Per sample':>12}")
    print("-" * 55)
    total_infer = 0.0
    for mname, secs in infer_times.items():
        per_sample_ms = secs / n_samples * 1000
        print(f"  {mname:<22}  {secs:>7.3f}s  {per_sample_ms:>10.3f}ms")
        total_infer += secs
    print("-" * 55)
    per_sample_ms_total = total_infer / n_samples * 1000
    print(f"  {'Total (all models)':<22}  {total_infer:>7.3f}s  {per_sample_ms_total:>10.3f}ms")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
