"""
Production Farm Risk Intelligence Engine for ParaliPool.
Connects the trained 3-layer MLP neural network (ml/artifacts/risk_model.joblib)
to FastAPI endpoints with exact signatures:
    predict_risk(farm_dict) -> float
    batch_predict(farms_list) -> list[float]
"""
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Union

import joblib
import pandas as pd

_BACKEND_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _BACKEND_DIR.parent
_MODEL_PATH = _REPO_ROOT / "ml" / "artifacts" / "risk_model.joblib"
_DATA_PATH = _BACKEND_DIR / "data.json"

_MODEL_BUNDLE: Dict[str, Any] | None = None
_CONTEXT_CACHE: Dict[str, Any] | None = None


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2.0) ** 2
    )
    return r * (2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)))


def _get_bundle() -> Dict[str, Any]:
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained MLP artifact not found at {_MODEL_PATH}. Run ml/train_model.ipynb first."
            )
        _MODEL_BUNDLE = joblib.load(_MODEL_PATH)
    return _MODEL_BUNDLE


def _get_regional_context() -> Dict[str, Any]:
    global _CONTEXT_CACHE
    if _CONTEXT_CACHE is None:
        if _DATA_PATH.exists():
            with open(_DATA_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            _CONTEXT_CACHE = {
                "farms": raw.get("farms", []),
                "machines": raw.get("machines", []),
            }
        else:
            _CONTEXT_CACHE = {"farms": [], "machines": []}
    return _CONTEXT_CACHE


def _to_dict(farm_obj: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    if hasattr(farm_obj, "model_dump"):
        return farm_obj.model_dump()
    if isinstance(farm_obj, dict):
        return farm_obj
    return getattr(farm_obj, "__dict__", {})


def _extract_mlp_features(
    data: Dict[str, Any],
    peer_farms: List[Dict[str, Any]],
    machines: List[Dict[str, Any]],
) -> Dict[str, float]:
    lat = float(data.get("lat", 30.34))
    lng = float(data.get("lng", 76.38))
    acres = float(data.get("acres", 5.0))
    days_left = max(1, min(15, int(data.get("days_left", 7))))
    has_heavy_tractor = bool(data.get("has_heavy_tractor", True))
    rain_forecast = bool(data.get("rain_forecast", False))
    variety = str(data.get("paddy_variety", "")).strip().upper()
    farm_id = data.get("id")

    # 1. Geospatial distance & nearby seeder availability
    seeders = [
        m for m in machines
        if m.get("available", True) and m.get("machine_type") in ("Super Seeder", "Happy Seeder")
    ]
    if not seeders:
        seeders = machines

    if seeders:
        distances = [_haversine_km(lat, lng, float(m["lat"]), float(m["lng"])) for m in seeders]
        dist_to_chc = max(0.5, min(22.0, min(distances)))
        nearby_pairs = [(m, d) for m, d in zip(seeders, distances) if d <= 22.0]
        if not nearby_pairs:
            nearest_idx = min(range(len(distances)), key=lambda i: distances[i])
            nearby_pairs = [(seeders[nearest_idx], distances[nearest_idx])]

        available_nearby = max(1, min(5, len(nearby_pairs)))
        avg_capacity = sum(float(m.get("capacity_acres_per_day", 7.0)) for m, _ in nearby_pairs) / len(nearby_pairs)
    else:
        dist_to_chc = 6.5
        available_nearby = 2
        avg_capacity = 7.0

    # Lacking >=55 HP tractor requires paired tractor dispatch, reducing effective daily clearance
    if not has_heavy_tractor:
        avg_capacity *= 0.75
    machine_capacity = max(2.5, min(9.5, avg_capacity))

    # 2. Local cluster queue ahead (competing urgent farms within 16 km + residue load)
    competing_acres = 0.0
    for peer in peer_farms:
        if farm_id and peer.get("id") == farm_id:
            continue
        if peer.get("status") == "cleared":
            continue
        if int(peer.get("days_left", 7)) <= days_left:
            d_peer = _haversine_km(lat, lng, float(peer.get("lat", lat)), float(peer.get("lng", lng)))
            if d_peer <= 16.0:
                competing_acres += float(peer.get("acres", 4.0))

    if "PUSA-44" in variety or "PUSA 44" in variety:
        variety_queue_offset = 10.0
    elif any(v in variety for v in ("PR-121", "PR-128", "PR-118", "HYBRID")):
        variety_queue_offset = 4.0
    elif "PR-126" in variety:
        variety_queue_offset = 0.0
    elif "BASMATI" in variety:
        variety_queue_offset = -8.0
    else:
        variety_queue_offset = 3.0

    queue_acres_ahead = max(0.0, min(65.0, (competing_acres * 0.65) + variety_queue_offset))

    # 3. Weather delay window
    rain_delay_days = 2.0 if rain_forecast else 0.0

    return {
        "days_to_deadline": float(days_left),
        "farm_acres": acres,
        "distance_to_chc_km": round(dist_to_chc, 2),
        "queue_acres_ahead": round(queue_acres_ahead, 2),
        "machine_capacity_per_day": round(machine_capacity, 2),
        "rain_delay_days": rain_delay_days,
        "available_machines_nearby": float(available_nearby),
    }


def batch_predict(farms_list: List[Union[Dict[str, Any], Any]]) -> List[float]:
    """
    Computes neural network deadline-miss risk scores (0.0 - 100.0) for a batch of farms.
    Signature: batch_predict(farms_list) -> list[float]
    """
    if not farms_list:
        return []

    bundle = _get_bundle()
    pipeline = bundle["pipeline"]
    feature_columns: List[str] = bundle["feature_columns"]

    ctx = _get_regional_context()
    farm_dicts = [_to_dict(f) for f in farms_list]
    peer_pool = farm_dicts if len(farm_dicts) > 1 else ctx["farms"]

    rows = [_extract_mlp_features(d, peer_pool, ctx["machines"]) for d in farm_dicts]
    input_df = pd.DataFrame(rows, columns=feature_columns)
    probs = pipeline.predict_proba(input_df)[:, 1]

    return [float(round(max(0.0, min(100.0, float(p) * 100.0)), 1)) for p in probs]


def predict_risk(farm_dict: Union[Dict[str, Any], Any]) -> float:
    """
    Computes neural network deadline-miss risk score (0.0 - 100.0) for a single farm.
    Signature: predict_risk(farm_dict) -> float
    """
    return batch_predict([farm_dict])[0]