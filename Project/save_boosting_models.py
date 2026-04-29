"""
save_boosting_models.py
=======================
Trains all three boosting models (XGBoost, LightGBM, Gradient Boosting)
exactly as in 02_boosting_pipeline.ipynb, then serialises them to disk.

Saved artefacts (in ./models/):
  xgb_pipeline.joblib   – XGBoost sklearn Pipeline  (preprocessor + classifier)
  lgb_pipeline.joblib   – LightGBM sklearn Pipeline
  gb_pipeline.joblib    – sklearn GradientBoosting Pipeline
  label_encoder.joblib  – fitted LabelEncoder  (int ↔ price-class string)
  class_names.joblib    – sorted list of class-name strings

Run:
  python save_boosting_models.py
"""

import warnings
warnings.filterwarnings("ignore")

import os
import time
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
import xgboost as xgb
import lightgbm as lgb

# ── Constants ──────────────────────────────────────────────────────────────────
SEED      = 42
DATA_FILE = "used_cars.csv"
MODEL_DIR = "models"

NUMERIC_FEATURES = [
    "mileage_num", "horsepower", "displacement", "car_age", "model_year",
    "has_accident", "clean_title_flag", "is_automatic",
    "num_cylinders", "has_turbo", "is_electric", "hp_per_liter",
    "trans_speeds",
]
CATEGORICAL_FEATURES = ["brand", "model", "fuel_type"]
ALL_FEATURES          = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET                = "price_class"

os.makedirs(MODEL_DIR, exist_ok=True)

# ── 1. Load raw data ────────────────────────────────────────────────────────────
print("Loading data …")
df = pd.read_csv(DATA_FILE)

# ── 2. Feature engineering (identical to notebook) ────────────────────────────
def preprocess(df):
    data = df.copy()

    data["price_num"] = (
        data["price"]
        .str.replace(r"[$,]", "", regex=True)
        .astype(float)
    )
    data["mileage_num"] = (
        data["milage"]
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+)")[0]
        .astype(float)
    )
    data["horsepower"] = (
        data["engine"].str.extract(r"(\d+\.?\d*)HP")[0].astype(float)
    )
    data["displacement"] = (
        data["engine"].str.extract(r"(\d+\.?\d*)L")[0].astype(float)
    )
    data["num_cylinders"] = (
        data["engine"].str.extract(r"(\d+)\s*Cylinder")[0].astype(float)
    )
    data["has_turbo"] = (
        data["engine"]
        .str.contains("Turbo|Turbocharged", case=False, na=False)
        .astype(int)
    )
    data["is_electric"] = (
        data["engine"]
        .str.contains("Electric", case=False, na=False)
        .astype(int)
    )
    data["hp_per_liter"] = data["horsepower"] / data["displacement"].replace(0, float("nan"))
    data["car_age"]          = 2025 - data["model_year"]
    data["has_accident"]     = data["accident"].str.contains("accident", case=False, na=False).astype(int)
    data["clean_title_flag"] = (data["clean_title"] == "Yes").astype(int)
    data["is_automatic"]     = data["transmission"].str.contains("A/T|Automatic|CVT|DCT", case=False, na=False).astype(int)
    data["trans_speeds"]     = (
        data["transmission"].str.extract(r"(\d+)-Speed")[0].astype(float)
    )
    return data

data = preprocess(df)

bins   = [0, 15000, 30000, 55000, float("inf")]
labels = ["Budget", "Mid-range", "Premium", "Luxury"]
data["price_class"] = pd.cut(data["price_num"], bins=bins, labels=labels)

# ── 3. Train / test split ──────────────────────────────────────────────────────
X = data[ALL_FEATURES].copy()
y = data[TARGET].copy()

mask = y.notna()
X, y = X[mask], y[mask]
y = y.astype(str)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED, stratify=y
)
CLASS_NAMES = sorted(y_train.unique())
print(f"Train: {X_train.shape} | Test: {X_test.shape}")
print("Classes:", CLASS_NAMES)

# ── 4. Preprocessor ────────────────────────────────────────────────────────────
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
])
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("ohe",     OneHotEncoder(handle_unknown="ignore", sparse_output=False, max_categories=50)),
])
preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer,     NUMERIC_FEATURES),
    ("cat", categorical_transformer, CATEGORICAL_FEATURES),
])

# Encode labels as integers for XGBoost / LightGBM
le          = LabelEncoder()
y_train_enc = le.fit_transform(y_train)

print("\nLabel mapping:", dict(zip(le.classes_, le.transform(le.classes_))))

# ── 5. Train models ────────────────────────────────────────────────────────────
train_times = {}
total_start = time.perf_counter()

print("\n[1/3] Training XGBoost …")
xgb_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", xgb.XGBClassifier(
        n_estimators       = 400,
        max_depth          = 6,
        learning_rate      = 0.05,
        subsample          = 0.8,
        colsample_bytree   = 0.8,
        gamma              = 0.1,
        reg_alpha          = 0.1,
        reg_lambda         = 1.0,
        use_label_encoder  = False,
        eval_metric        = "mlogloss",
        random_state       = SEED,
        n_jobs             = -1,
    )),
])
t0 = time.perf_counter()
xgb_pipeline.fit(X_train, y_train_enc)
train_times["XGBoost"] = time.perf_counter() - t0
print(f"   XGBoost trained ✓  ({train_times['XGBoost']:.2f}s)")

print("[2/3] Training LightGBM …")
lgb_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", lgb.LGBMClassifier(
        n_estimators     = 400,
        max_depth        = -1,
        num_leaves       = 63,
        learning_rate    = 0.05,
        subsample        = 0.8,
        colsample_bytree = 0.8,
        reg_alpha        = 0.1,
        reg_lambda       = 1.0,
        class_weight     = "balanced",
        random_state     = SEED,
        n_jobs           = -1,
        verbose          = -1,
    )),
])
t0 = time.perf_counter()
lgb_pipeline.fit(X_train, y_train_enc)
train_times["LightGBM"] = time.perf_counter() - t0
print(f"   LightGBM trained ✓  ({train_times['LightGBM']:.2f}s)")

print("[3/3] Training Gradient Boosting (sklearn) …")
gb_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", GradientBoostingClassifier(
        n_estimators  = 200,
        max_depth     = 5,
        learning_rate = 0.05,
        subsample     = 0.8,
        max_features  = "sqrt",
        random_state  = SEED,
    )),
])
t0 = time.perf_counter()
gb_pipeline.fit(X_train, y_train)   # sklearn GBC accepts string labels
train_times["GradientBoosting"] = time.perf_counter() - t0
print(f"   Gradient Boosting trained ✓  ({train_times['GradientBoosting']:.2f}s)")

total_train_time = time.perf_counter() - total_start

# ── 6. Save artefacts ──────────────────────────────────────────────────────────
print("\nSaving artefacts to ./models/ …")
joblib.dump(xgb_pipeline,  os.path.join(MODEL_DIR, "xgb_pipeline.joblib"))
joblib.dump(lgb_pipeline,  os.path.join(MODEL_DIR, "lgb_pipeline.joblib"))
joblib.dump(gb_pipeline,   os.path.join(MODEL_DIR, "gb_pipeline.joblib"))
joblib.dump(le,            os.path.join(MODEL_DIR, "label_encoder.joblib"))
joblib.dump(CLASS_NAMES,   os.path.join(MODEL_DIR, "class_names.joblib"))

print("Saved:")
for f in ["xgb_pipeline.joblib", "lgb_pipeline.joblib",
          "gb_pipeline.joblib", "label_encoder.joblib", "class_names.joblib"]:
    path = os.path.join(MODEL_DIR, f)
    size = os.path.getsize(path) / 1024
    print(f"  {path}  ({size:.1f} KB)")

# ── 7. Training time summary ───────────────────────────────────────────────────
print("\n" + "=" * 45)
print("  ⏱  TRAINING TIME SUMMARY")
print("=" * 45)
for model_name, secs in train_times.items():
    print(f"  {model_name:<22} : {secs:>7.2f}s")
print("-" * 45)
print(f"  {'Total (all 3 models)':<22} : {total_train_time:>7.2f}s")
print("=" * 45)

print("\n✅ All boosting models saved successfully!")
