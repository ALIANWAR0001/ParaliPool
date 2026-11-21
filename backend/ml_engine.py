"""
Temporary deterministic burn-risk scorer (0-100) for agricultural fields in Punjab.
Designed with exact signatures:
    predict_risk(farm_dict) -> float
    batch_predict(farms_list) -> list[float]
Ready for ML lead to drop in a 3-layer MLP or XGBoost model with zero changes to main.py.
"""
from typing import Any, Dict, List, Union


def predict_risk(farm_dict: Union[Dict[str, Any], Any]) -> float:
    """
    Computes a deterministic fire burn-risk score between 0.0 and 100.0 based on:
    - paddy_variety: High biomass varieties like PUSA-44 leave stubborn, heavy stubble
      with late harvest, whereas PR-126 or Basmati leave easily manageable or marketable straw.
    - days_left: Urgent countdown to wheat sowing window (panic window < 4 days).
    - has_heavy_tractor: Lack of >=55HP tractor prevents in-situ mulching/direct drilling.
    - rain_forecast: Upcoming rain destroys straw drying window, triggering panic burns.
    - acres: Small-to-medium land parcels face acute time-crunch for custom machinery hiring.
    """
    # Safe getter supporting dicts or Pydantic models
    if hasattr(farm_dict, "model_dump"):
        data = farm_dict.model_dump()
    elif isinstance(farm_dict, dict):
        data = farm_dict
    else:
        data = getattr(farm_dict, "__dict__", {})

    variety = str(data.get("paddy_variety", "")).strip().upper()
    days_left = int(data.get("days_left", 7))
    has_heavy_tractor = bool(data.get("has_heavy_tractor", True))
    rain_forecast = bool(data.get("rain_forecast", False))
    acres = float(data.get("acres", 5.0))

    # 1. Baseline risk score
    score = 10.0

    # 2. Paddy Variety Weight
    if "PUSA-44" in variety or "PUSA 44" in variety:
        score += 30.0  # High straw volume, long duration, primary contributor to stubble fires
    elif any(v in variety for v in ["PR-121", "PR-128", "PR-118", "HYBRID"]):
        score += 18.0
    elif "PR-126" in variety:
        score += 8.0   # Short duration, manageable straw
    elif "BASMATI" in variety:
        score += 2.0   # High economic value fodder, rarely burned
    else:
        score += 15.0

    # 3. Urgency / Wheat Sowing Window (days_left)
    if days_left <= 2:
        score += 35.0  # Panic burning threshold
    elif days_left <= 4:
        score += 25.0
    elif days_left <= 7:
        score += 15.0
    elif days_left <= 10:
        score += 5.0
    else:
        score += 0.0

    # 4. Mechanization Capacity (Heavy Tractor)
    if not has_heavy_tractor:
        score += 20.0  # Cannot pull super-seeder or happy-seeder alone
    else:
        score -= 5.0

    # 5. Rain Forecast (Forces immediate burn before rains render fields unworkable)
    if rain_forecast:
        score += 15.0

    # 6. Acreage factor
    if acres >= 8.0:
        score += 3.0
    elif acres <= 3.0:
        score -= 3.0

    # Strict clamping between 0.0 and 100.0
    final_score = max(0.0, min(100.0, score))
    return float(round(final_score, 1))


def batch_predict(farms_list: List[Union[Dict[str, Any], Any]]) -> List[float]:
    """
    Computes deterministic burn-risk scores for a batch of farms.
    Signature: batch_predict(farms_list) -> list[float]
    """
    return [predict_risk(farm) for farm in farms_list]
