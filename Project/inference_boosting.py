"""
inference_boosting.py
=====================
Standalone inference script for the three saved boosting models.

Usage:
  python inference_boosting.py                   # runs on 10 built-in sample cars
  python inference_boosting.py --model xgb       # only XGBoost
  python inference_boosting.py --model lgb       # only LightGBM
  python inference_boosting.py --model gb        # only Gradient Boosting
  python inference_boosting.py --csv my_cars.csv # predict from a CSV file

Requirements:
  Run  `python save_boosting_models.py`  first to generate the ./models/ folder.

Price class bins (same as training):
  Budget    :  < $15,000
  Mid-range :  $15,000 – $30,000
  Premium   :  $30,000 – $55,000
  Luxury    :  > $55,000
"""

import argparse
import os
import sys

import joblib
import numpy as np
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
MODEL_DIR = "models"

# ── Feature lists (must match training exactly) ────────────────────────────────
NUMERIC_FEATURES = [
    "mileage_num", "horsepower", "displacement", "car_age", "model_year",
    "has_accident", "clean_title_flag", "is_automatic",
    "num_cylinders", "has_turbo", "is_electric", "hp_per_liter",
    "trans_speeds",
]
CATEGORICAL_FEATURES = ["brand", "model", "fuel_type"]
ALL_FEATURES          = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# ── Price bin boundaries ───────────────────────────────────────────────────────
PRICE_BINS   = [0, 15_000, 30_000, 55_000, float("inf")]
PRICE_LABELS = ["Budget", "Mid-range", "Premium", "Luxury"]

PRICE_RANGES = {
    "Budget":    "< $15,000",
    "Mid-range": "$15,000 – $30,000",
    "Premium":   "$30,000 – $55,000",
    "Luxury":    "> $55,000",
}


def price_to_class(price: float) -> str:
    """Convert a numeric price to its class label using the training bins."""
    for i, upper in enumerate(PRICE_BINS[1:]):
        if price < upper:
            return PRICE_LABELS[i]
    return PRICE_LABELS[-1]


# ──────────────────────────────────────────────────────────────────────────────
# Sample inference data — 10 diverse used cars with ACTUAL listed prices
#
# actual_price  = real sale / listing price from the used_cars dataset (or
#                 realistic market reference for illustrative cars not in CSV)
# actual_class  = derived from actual_price using the same bins as training
# ──────────────────────────────────────────────────────────────────────────────
SAMPLE_CARS_RAW = pd.DataFrame([

    # ── 1. Budget ─────────────────────────────────────────────────────────────
    {
        "brand": "Ford", "model": "Utility Police Interceptor Base",
        "model_year": 2013, "milage": "51,000 mi.",
        "fuel_type": "E85 Flex Fuel",
        "engine": "300.0HP 3.7L V6 Cylinder Engine Flex Fuel Capable",
        "transmission": "6-Speed A/T",
        "accident": "At least 1 accident or damage reported", "clean_title": "Yes",
        # ── ground truth ──────────────────────────────────────────────────────
        "actual_price": 10_300,   # $10,300  → Budget
    },

    # ── 2. Budget ─────────────────────────────────────────────────────────────
    {
        "brand": "Honda", "model": "Civic LX",
        "model_year": 2015, "milage": "98,000 mi.",
        "fuel_type": "Gasoline",
        "engine": "1.8L I4 16V MPFI SOHC",
        "transmission": "Automatic",
        "accident": "None reported", "clean_title": "Yes",
        "actual_price": 9_500,    # $9,500   → Budget
    },

    # ── 3. Mid-range ──────────────────────────────────────────────────────────
    {
        "brand": "INFINITI", "model": "Q50 Hybrid Sport",
        "model_year": 2015, "milage": "88,900 mi.",
        "fuel_type": "Hybrid",
        "engine": "354.0HP 3.5L V6 Cylinder Engine Gas/Electric Hybrid",
        "transmission": "7-Speed A/T",
        "accident": "None reported", "clean_title": "Yes",
        "actual_price": 15_500,   # $15,500  → Mid-range
    },

    # ── 4. Mid-range ──────────────────────────────────────────────────────────
    {
        "brand": "Toyota", "model": "Camry XSE",
        "model_year": 2020, "milage": "28,000 mi.",
        "fuel_type": "Gasoline",
        "engine": "203.0HP 2.5L I4 16V GDI DOHC",
        "transmission": "8-Speed Automatic",
        "accident": "None reported", "clean_title": "Yes",
        "actual_price": 25_900,   # $25,900  → Mid-range
    },

    # ── 5. Premium ────────────────────────────────────────────────────────────
    {
        "brand": "Hyundai", "model": "Palisade SEL",
        "model_year": 2021, "milage": "34,742 mi.",
        "fuel_type": "Gasoline",
        "engine": "3.8L V6 24V GDI DOHC",
        "transmission": "8-Speed Automatic",
        "accident": "At least 1 accident or damage reported", "clean_title": "Yes",
        "actual_price": 38_005,   # $38,005  → Premium
    },

    # ── 6. Premium ────────────────────────────────────────────────────────────
    {
        "brand": "Audi", "model": "Q3 45 S line Premium Plus",
        "model_year": 2021, "milage": "9,835 mi.",
        "fuel_type": "Gasoline",
        "engine": "2.0L I4 16V GDI DOHC Turbo",
        "transmission": "8-Speed Automatic",
        "accident": "None reported", "clean_title": "Yes",
        "actual_price": 34_999,   # $34,999  → Premium
    },

    # ── 7. Premium (boundary — just below Luxury) ─────────────────────────────
    {
        "brand": "Lexus", "model": "RX 350 RX 350",
        "model_year": 2022, "milage": "22,372 mi.",
        "fuel_type": "Gasoline",
        "engine": "3.5 Liter DOHC",
        "transmission": "Automatic",
        "accident": "None reported", "clean_title": "Yes",
        "actual_price": 54_598,   # $54,598  → Premium (just under $55k)
    },

    # ── 8. Luxury ─────────────────────────────────────────────────────────────
    {
        "brand": "Mercedes-Benz", "model": "GLE 450 4MATIC",
        "model_year": 2023, "milage": "5,200 mi.",
        "fuel_type": "Gasoline",
        "engine": "362.0HP 3.0L I6 24V GDI DOHC Turbo",
        "transmission": "9-Speed Automatic",
        "accident": "None reported", "clean_title": "Yes",
        "actual_price": 76_500,   # $76,500  → Luxury
    },

    # ── 9. Luxury ─────────────────────────────────────────────────────────────
    {
        "brand": "Porsche", "model": "Cayenne",
        "model_year": 2022, "milage": "11,000 mi.",
        "fuel_type": "Gasoline",
        "engine": "335.0HP 3.0L V6 Cylinder Engine",
        "transmission": "8-Speed Automatic",
        "accident": "None reported", "clean_title": "Yes",
        "actual_price": 82_000,   # $82,000  → Luxury
    },

    # ── 10. Premium (EV edge-case) ────────────────────────────────────────────
    {
        "brand": "Tesla", "model": "Model 3 Long Range",
        "model_year": 2021, "milage": "18,000 mi.",
        "fuel_type": "Electric",
        "engine": "Electric Motor",
        "transmission": "1-Speed A/T",
        "accident": "None reported", "clean_title": "Yes",
        "actual_price": 42_000,   # $42,000  → Premium
    },
])

# Derive actual_class from actual_price using the same bins as training
SAMPLE_CARS_RAW["actual_class"] = SAMPLE_CARS_RAW["actual_price"].apply(price_to_class)


# ──────────────────────────────────────────────────────────────────────────────
# Feature engineering  (raw CSV row → model-ready row)
# ──────────────────────────────────────────────────────────────────────────────
def engineer_features(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Converts a raw-data DataFrame (original CSV columns) into the engineered
    feature DataFrame expected by the sklearn Pipelines.
    """
    if set(ALL_FEATURES).issubset(raw.columns):
        return raw[ALL_FEATURES].copy()

    d = raw.copy()

    # mileage
    if "mileage_num" not in d.columns:
        d["mileage_num"] = (
            d["milage"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.extract(r"(\d+)")[0]
            .astype(float)
        )

    # engine-derived features
    if "horsepower" not in d.columns:
        d["horsepower"] = d["engine"].str.extract(r"(\d+\.?\d*)HP")[0].astype(float)
    if "displacement" not in d.columns:
        d["displacement"] = d["engine"].str.extract(r"(\d+\.?\d*)L")[0].astype(float)
    if "num_cylinders" not in d.columns:
        d["num_cylinders"] = d["engine"].str.extract(r"(\d+)\s*Cylinder")[0].astype(float)
    if "has_turbo" not in d.columns:
        d["has_turbo"] = (
            d["engine"].str.contains("Turbo|Turbocharged", case=False, na=False).astype(int)
        )
    if "is_electric" not in d.columns:
        d["is_electric"] = (
            d["engine"].str.contains("Electric", case=False, na=False).astype(int)
        )
    if "hp_per_liter" not in d.columns:
        d["hp_per_liter"] = d["horsepower"] / d["displacement"].replace(0, float("nan"))

    # age
    if "car_age" not in d.columns:
        d["car_age"] = 2025 - d["model_year"].astype(int)

    # accident / title
    if "has_accident" not in d.columns:
        d["has_accident"] = (
            d["accident"].str.contains("accident", case=False, na=False).astype(int)
        )
    if "clean_title_flag" not in d.columns:
        d["clean_title_flag"] = (d["clean_title"] == "Yes").astype(int)

    # transmission
    if "is_automatic" not in d.columns:
        d["is_automatic"] = (
            d["transmission"]
            .str.contains("A/T|Automatic|CVT|DCT", case=False, na=False)
            .astype(int)
        )
    if "trans_speeds" not in d.columns:
        d["trans_speeds"] = (
            d["transmission"].str.extract(r"(\d+)-Speed")[0].astype(float)
        )

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
# Run predictions for all selected models
# ──────────────────────────────────────────────────────────────────────────────
def predict(X: pd.DataFrame, pipelines, le, class_names) -> pd.DataFrame:
    results = []

    for model_name, (pipeline, use_encoded) in pipelines.items():
        proba = pipeline.predict_proba(X)           # shape: (n_samples, n_classes)

        if use_encoded:
            enc_preds = pipeline.predict(X)
            str_preds = le.inverse_transform(enc_preds)
        else:
            str_preds = pipeline.predict(X)

        for i, (pred, prob_row) in enumerate(zip(str_preds, proba)):
            conf = prob_row.max() * 100
            prob_dict = {f"P({c})": f"{p:.1%}" for c, p in zip(class_names, prob_row)}
            results.append({
                "sample"     : i + 1,
                "model"      : model_name,
                "prediction" : pred,
                "confidence" : f"{conf:.1f}%",
                **prob_dict,
            })

    return pd.DataFrame(results)


# ──────────────────────────────────────────────────────────────────────────────
# Pretty-print helpers
# ──────────────────────────────────────────────────────────────────────────────
def fmt_price(p: float) -> str:
    return f"${p:,.0f}"


def fmt_correct(pred: str, actual: str) -> str:
    return "✅" if pred == actual else "❌"


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry-point
# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Run inference with the saved boosting models on used-car price classification."
    )
    parser.add_argument(
        "--model", choices=["xgb", "lgb", "gb", "all"], default="all",
        help="Which model(s) to use  (default: all three)."
    )
    parser.add_argument(
        "--csv", default=None,
        help=(
            "Path to a CSV with raw car columns (same schema as used_cars.csv). "
            "Add an 'actual_price' column to enable accuracy reporting. "
            "Omit to use the 10 built-in sample cars."
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
    else:
        raw = SAMPLE_CARS_RAW.copy()
        has_actuals = True
        print(f"\n🚗  Using {len(raw)} built-in sample cars (actual prices included).")

    # ── Engineer features ────────────────────────────────────────────────────
    X = engineer_features(raw)

    # ── Predict ──────────────────────────────────────────────────────────────
    print("\n⚙️   Running inference …\n")
    results = predict(X, pipelines, le, class_names)

    # Attach readable car label
    if "brand" in raw.columns and "model" in raw.columns:
        car_labels = (raw["brand"] + " " + raw["model"].str[:28]).tolist()
    else:
        car_labels = [f"Car {i + 1}" for i in range(len(raw))]

    results.insert(1, "car", results["sample"].apply(lambda s: car_labels[s - 1]))

    # Attach actual price / class if available
    if has_actuals:
        actual_prices  = raw["actual_price"].tolist()
        actual_classes = raw["actual_class"].tolist()
        results["actual_price"] = results["sample"].apply(lambda s: fmt_price(actual_prices[s - 1]))
        results["actual_class"] = results["sample"].apply(lambda s: actual_classes[s - 1])
        results["correct?"]     = results.apply(
            lambda r: fmt_correct(r["prediction"], r["actual_class"]), axis=1
        )

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 180)
    pd.set_option("display.max_colwidth", 30)

    model_names = results["model"].unique()

    # ── Per-model detailed table ─────────────────────────────────────────────
    for mname in model_names:
        sub = results[results["model"] == mname].copy()
        print("=" * 90)
        print(f"  MODEL : {mname}")
        print("=" * 90)

        if has_actuals:
            display_cols = (
                ["sample", "car", "actual_price", "actual_class",
                 "prediction", "confidence", "correct?"]
                + [c for c in sub.columns if c.startswith("P(")]
            )
        else:
            display_cols = (
                ["sample", "car", "prediction", "confidence"]
                + [c for c in sub.columns if c.startswith("P(")]
            )

        print(sub[display_cols].to_string(index=False))

        if has_actuals:
            n_correct = (sub["correct?"] == "✅").sum()
            n_total   = len(sub)
            acc_pct   = n_correct / n_total * 100
            print(f"\n  Sample accuracy: {n_correct}/{n_total} ({acc_pct:.0f}%)\n")
        else:
            print()

    # ── Side-by-side summary across models ───────────────────────────────────
    if len(model_names) > 1:
        print("=" * 90)
        print("  SIDE-BY-SIDE SUMMARY  (prediction per model)")
        print("=" * 90)

        idx_cols  = ["sample", "car"]
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
                    lambda r: fmt_correct(r[mname], r["actual_class"]), axis=1
                )

        print(pivot.to_string(index=False))
        print()

        if has_actuals:
            print("─" * 90)
            print("  ACCURACY PER MODEL (on this sample):")
            for mname in model_names:
                n_correct = (pivot[f"{mname} ✓?"] == "✅").sum()
                n_total   = len(pivot)
                print(f"  {mname:<22}: {n_correct}/{n_total}  ({n_correct/n_total*100:.0f}%)")
            print()

    print("✅  Inference complete!\n")


if __name__ == "__main__":
    main()
