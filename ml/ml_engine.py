from pathlib import Path
from typing import Any

import joblib
import pandas as pd

_BASE_DIR = Path(__file__).resolve().parent
_MODEL_PATH = _BASE_DIR / "artifacts" / "risk_model.joblib"

_MODEL_BUNDLE: dict[str, Any] | None = None


def _get_bundle() -> dict[str, Any]:
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model artifact not found at {_MODEL_PATH}. Run all cells in ml/train_model.ipynb first."
            )
        _MODEL_BUNDLE = joblib.load(_MODEL_PATH)
    return _MODEL_BUNDLE


def _classify_risk_level(risk_score: float, thresholds: dict[str, float]) -> str:
    if risk_score >= thresholds.get("high", 70.0):
        return "HIGH"
    if risk_score >= thresholds.get("medium", 35.0):
        return "MEDIUM"
    return "LOW"


def predict_farm_risk(farm_data: dict[str, Any]) -> dict[str, Any]:
    """
    Predicts deadline-miss risk for a single farm using the frozen v1 schema.
    """
    bundle = _get_bundle()
    pipeline = bundle["pipeline"]
    feature_columns: list[str] = bundle["feature_columns"]
    thresholds: dict[str, float] = bundle.get("thresholds", {"medium": 35.0, "high": 70.0})
    risk_type: str = bundle.get("risk_type", "DEADLINE_MISS")

    missing = [col for col in feature_columns if col not in farm_data]
    if missing:
        raise ValueError(f"Missing required farm_data fields: {missing}")

    row = {col: float(farm_data[col]) for col in feature_columns}
    input_df = pd.DataFrame([row], columns=feature_columns)

    miss_prob = float(pipeline.predict_proba(input_df)[0][1])
    risk_score = round(miss_prob * 100.0, 1)
    risk_level = _classify_risk_level(risk_score, thresholds)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_type": risk_type,
    }


def predict_batch_risk(farms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Vectorized scoring helper for ranking all farms in a cluster."""
    if not farms:
        return []

    bundle = _get_bundle()
    pipeline = bundle["pipeline"]
    feature_columns: list[str] = bundle["feature_columns"]
    thresholds: dict[str, float] = bundle.get("thresholds", {"medium": 35.0, "high": 70.0})
    risk_type: str = bundle.get("risk_type", "DEADLINE_MISS")

    rows = [{col: float(farm[col]) for col in feature_columns} for farm in farms]
    input_df = pd.DataFrame(rows, columns=feature_columns)
    probs = pipeline.predict_proba(input_df)[:, 1]

    results = []
    for prob in probs:
        score = round(float(prob) * 100.0, 1)
        results.append(
            {
                "risk_score": score,
                "risk_level": _classify_risk_level(score, thresholds),
                "risk_type": risk_type,
            }
        )
    return results


if __name__ == "__main__":
    sample_scenarios = [
        (
            "Low-Risk Farm (12 days left, 0 queue, 4 machines)",
            {
                "days_to_deadline": 12,
                "farm_acres": 5.0,
                "distance_to_chc_km": 3.0,
                "queue_acres_ahead": 0.0,
                "machine_capacity_per_day": 8.0,
                "rain_delay_days": 0,
                "available_machines_nearby": 4,
            },
        ),
        (
            "Medium-Risk Farm (5 days left, 18 acres queue)",
            {
                "days_to_deadline": 5,
                "farm_acres": 9.0,
                "distance_to_chc_km": 9.5,
                "queue_acres_ahead": 18.0,
                "machine_capacity_per_day": 6.5,
                "rain_delay_days": 0,
                "available_machines_nearby": 2,
            },
        ),
        (
            "High-Risk Urgent Farm (2 days left, 32 acres queue, 1 day rain)",
            {
                "days_to_deadline": 2,
                "farm_acres": 14.0,
                "distance_to_chc_km": 14.0,
                "queue_acres_ahead": 32.0,
                "machine_capacity_per_day": 5.5,
                "rain_delay_days": 1,
                "available_machines_nearby": 1,
            },
        ),
    ]

    for label, payload in sample_scenarios:
        print(f"{label}\n  -> {predict_farm_risk(payload)}\n")