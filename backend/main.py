"""
ParaliPool FastAPI Backend Service.
In-memory state initialized from backend/data.json.
Provides 5 core endpoints:
- GET /api/farms
- POST /api/farms/book
- POST /api/machines/add
- POST /api/simulate-risk
- GET /api/optimize
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from fastapi import Body, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from ml_engine import batch_predict, predict_risk
from routing_engine import run_optimization_comparison

# -----------------------------------------------------------------------------
# Data Models (Strictly Locked JSON Schemas)
# -----------------------------------------------------------------------------
class Farm(BaseModel):
    id: str
    village: str
    lat: float
    lng: float
    acres: float
    paddy_variety: str
    days_left: int
    has_heavy_tractor: bool
    rain_forecast: bool
    risk_score: float
    status: str = "pending"
    assigned_type: Literal["seeder", "biomass", "unassigned"] = "unassigned"
    assigned_to: Optional[str] = None


class Machine(BaseModel):
    id: str
    owner_name: str
    machine_type: Literal["Super Seeder", "Happy Seeder", "Baler"]
    tractor_hp: int
    price_per_acre: float
    lat: float
    lng: float
    capacity_acres_per_day: float
    available: bool = True


class MachineCreate(BaseModel):
    """
    Accepts standard fields or 'type' and 'hp' aliases for backwards/frontend compatibility.
    """
    id: Optional[str] = None
    owner_name: str
    machine_type: Optional[str] = None
    type: Optional[str] = None
    tractor_hp: Optional[int] = None
    hp: Optional[int] = None
    price_per_acre: float
    lat: float
    lng: float
    capacity_acres_per_day: float
    available: bool = True

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, values: Any) -> Any:
        if isinstance(values, dict):
            # Resolve type -> machine_type
            if not values.get("machine_type") and values.get("type"):
                values["machine_type"] = values["type"]
            # Resolve hp -> tractor_hp
            if values.get("tractor_hp") is None and values.get("hp") is not None:
                values["tractor_hp"] = values["hp"]
        return values


class BiomassHub(BaseModel):
    id: str
    name: str
    hub_type: Literal["Pellet Plant", "CBG Plant", "Brick Kiln"]
    lat: float
    lng: float
    capacity_tonnes_per_day: float


class FarmBookRequest(BaseModel):
    id: Optional[str] = None
    farm_id: Optional[str] = None
    village: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    acres: Optional[float] = None
    paddy_variety: Optional[str] = None
    days_left: Optional[int] = None
    has_heavy_tractor: Optional[bool] = None
    rain_forecast: Optional[bool] = None
    assigned_type: Optional[Literal["seeder", "biomass", "unassigned"]] = "unassigned"
    assigned_to: Optional[str] = None


# -----------------------------------------------------------------------------
# In-Memory State & Loading
# -----------------------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "data.json"

in_memory_farms: List[Dict[str, Any]] = []
in_memory_machines: List[Dict[str, Any]] = []
in_memory_biomass_hubs: List[Dict[str, Any]] = []


def load_in_memory_state():
    global in_memory_farms, in_memory_machines, in_memory_biomass_hubs
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"data.json not found at {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    in_memory_farms = raw_data.get("farms", [])
    in_memory_machines = raw_data.get("machines", [])
    in_memory_biomass_hubs = raw_data.get("biomass_hubs", [])


# Initialize state on module load
load_in_memory_state()

# -----------------------------------------------------------------------------
# FastAPI Application Setup
# -----------------------------------------------------------------------------
app = FastAPI(
    title="ParaliPool Backend Routing Engine",
    description="Risk-prioritized geospatial pooling & Ex-Situ biomass fallback for stubble burning prevention",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "ParaliPool API",
        "farms_count": len(in_memory_farms),
        "machines_count": len(in_memory_machines),
        "hubs_count": len(in_memory_biomass_hubs)
    }


# -----------------------------------------------------------------------------
# 1. GET /api/farms
# -----------------------------------------------------------------------------
@app.get("/api/farms", response_model=List[Farm])
def get_farms():
    """
    Returns all registered agricultural fields and their current allocation status.
    """
    return in_memory_farms


# -----------------------------------------------------------------------------
# 2. POST /api/farms/book
# -----------------------------------------------------------------------------
@app.post("/api/farms/book", response_model=Farm)
def book_farm(booking: FarmBookRequest):
    """
    Books a machine for an existing farm or registers a new farm booking request.
    Automatically scores burn-risk if a new farm is registered.
    """
    target_id = booking.farm_id or booking.id

    # Scenario A: Booking an existing farm
    if target_id:
        for farm in in_memory_farms:
            if farm["id"] == target_id:
                farm["status"] = "booked"
                if booking.assigned_to:
                    farm["assigned_to"] = booking.assigned_to
                    farm["assigned_type"] = booking.assigned_type or "seeder"
                return farm
        # If specific id wasn't found in memory, raise 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id '{target_id}' not found"
        )

    # Scenario B: Registering a new farm booking
    new_id = f"F{len(in_memory_farms) + 1:02d}"
    farm_dict = {
        "id": new_id,
        "village": booking.village or "Patiala Rural",
        "lat": float(booking.lat if booking.lat is not None else 30.34),
        "lng": float(booking.lng if booking.lng is not None else 76.38),
        "acres": float(booking.acres if booking.acres is not None else 4.0),
        "paddy_variety": booking.paddy_variety or "PUSA-44",
        "days_left": int(booking.days_left if booking.days_left is not None else 3),
        "has_heavy_tractor": bool(booking.has_heavy_tractor if booking.has_heavy_tractor is not None else False),
        "rain_forecast": bool(booking.rain_forecast if booking.rain_forecast is not None else True),
        "status": "booked",
        "assigned_type": booking.assigned_type or "unassigned",
        "assigned_to": booking.assigned_to
    }
    farm_dict["risk_score"] = predict_risk(farm_dict)
    in_memory_farms.append(farm_dict)
    return farm_dict


# -----------------------------------------------------------------------------
# 3. POST /api/machines/add
# -----------------------------------------------------------------------------
@app.post("/api/machines/add", response_model=Machine)
def add_machine(machine_in: MachineCreate):
    """
    Registers a new machine (Super Seeder / Happy Seeder / Baler) into the pooling network.
    Accepts aliases 'type' for machine_type and 'hp' for tractor_hp.
    """
    valid_types = ["Super Seeder", "Happy Seeder", "Baler"]
    m_type = machine_in.machine_type
    if m_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"machine_type must be one of {valid_types}, got '{m_type}'"
        )

    machine_id = machine_in.id or f"M{len(in_memory_machines) + 1:02d}"

    new_machine = {
        "id": machine_id,
        "owner_name": machine_in.owner_name,
        "machine_type": m_type,
        "tractor_hp": int(machine_in.tractor_hp if machine_in.tractor_hp is not None else 65),
        "price_per_acre": float(machine_in.price_per_acre),
        "lat": float(machine_in.lat),
        "lng": float(machine_in.lng),
        "capacity_acres_per_day": float(machine_in.capacity_acres_per_day),
        "available": bool(machine_in.available)
    }

    in_memory_machines.append(new_machine)
    return new_machine


# -----------------------------------------------------------------------------
# 4. POST /api/simulate-risk
# -----------------------------------------------------------------------------
@app.post("/api/simulate-risk")
def simulate_risk(payload: Optional[Dict[str, Any]] = Body(default=None)):
    """
    Runs deterministic ML risk scoring over agricultural fields.
    If custom farms are supplied in payload, scores them.
    Otherwise recalculates scores across in-memory farms (with optional weather simulation).
    """
    req_data = payload or {}

    # If explicit farms list supplied in body
    if "farms" in req_data and isinstance(req_data["farms"], list):
        custom_farms = req_data["farms"]
        scores = batch_predict(custom_farms)
        for farm, score in zip(custom_farms, scores):
            farm["risk_score"] = score
        return {
            "message": f"Successfully simulated burn-risk for {len(custom_farms)} farms",
            "farms": custom_farms
        }

    # Otherwise re-score in-memory farms
    rain_override = req_data.get("rain_forecast")
    days_left_override = req_data.get("days_left")

    for farm in in_memory_farms:
        if rain_override is not None:
            farm["rain_forecast"] = bool(rain_override)
        if days_left_override is not None:
            farm["days_left"] = int(days_left_override)
        farm["risk_score"] = predict_risk(farm)

    return {
        "message": "Risk simulation completed successfully across all registered farms",
        "farms": in_memory_farms,
        "total_farms": len(in_memory_farms),
        "high_risk_count": len([f for f in in_memory_farms if f.get("risk_score", 0) >= 80.0])
    }


# -----------------------------------------------------------------------------
# 5. GET /api/optimize
# -----------------------------------------------------------------------------
@app.get("/api/optimize")
def get_optimize():
    """
    Compares Baseline FCFS routing vs ParaliPool Risk-Prioritized Geospatial Neighbor Clustering
    and Automatic Ex-Situ Biomass Fallback.
    Returns Leaflet-ready polylines and comparative sustainability metrics:
    - farms_cleared_pct
    - total_transit_km
    - diesel_saved_liters
    - straw_diverted_tonnes
    - owner_pooled_earnings_inr
    """
    result = run_optimization_comparison(
        in_memory_farms,
        in_memory_machines,
        in_memory_biomass_hubs
    )

    # Synchronize in-memory farms with ParaliPool optimized allocations
    paralipool_data = result["paralipool"]
    assigned_map = {}

    for farm in paralipool_data.get("cleared_farms", []):
        assigned_map[farm["id"]] = ("seeder", farm.get("assigned_to"), "cleared")

    for farm in paralipool_data.get("biomass_fallback_farms", []):
        assigned_map[farm["id"]] = ("biomass", farm.get("assigned_to"), "cleared")

    for farm in in_memory_farms:
        if farm["id"] in assigned_map:
            atype, ato, stat = assigned_map[farm["id"]]
            farm["assigned_type"] = atype
            farm["assigned_to"] = ato
            farm["status"] = stat
        else:
            farm["assigned_type"] = "unassigned"
            farm["assigned_to"] = None
            farm["status"] = "pending"

    return result


# -----------------------------------------------------------------------------
# 6. POST /api/reset
# -----------------------------------------------------------------------------
@app.post("/api/reset")
def reset_state():
    """
    Resets live demo state: reloads backend/data.json and re-runs optimization
    to restore clean state between judging rounds.
    """
    load_in_memory_state()
    result = get_optimize()
    return {
        "status": "reset_successful",
        "message": "Demo state reset to original data and re-optimized",
        "baseline": result["baseline"],
        "paralipool": result["paralipool"],
        "comparison": result["comparison"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
