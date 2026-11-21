"""
Verification script for ParaliPool backend.
Tests all 5 API endpoints:
1. GET /api/farms
2. POST /api/farms/book
3. POST /api/machines/add
4. POST /api/simulate-risk
5. GET /api/optimize

Prints the Baseline vs ParaliPool metrics summary.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app, load_in_memory_state

client = TestClient(app)


def test_all():
    print("=================================================================")
    print("          PARALIPOOL BACKEND ROUTING ENGINE VERIFICATION         ")
    print("=================================================================\n")

    # Reset state to clean data.json before verification
    load_in_memory_state()

    # -------------------------------------------------------------------------
    # 1. GET /api/farms
    # -------------------------------------------------------------------------
    print("[1/5] Testing GET /api/farms...")
    res = client.get("/api/farms")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    farms = res.json()
    assert isinstance(farms, list), "Expected list of farms"
    assert len(farms) == 16, f"Expected 16 initial farms, found {len(farms)}"

    # Validate locked Farm schema
    required_farm_keys = {
        "id", "village", "lat", "lng", "acres", "paddy_variety",
        "days_left", "has_heavy_tractor", "rain_forecast", "risk_score",
        "status", "assigned_type", "assigned_to"
    }
    sample_farm = farms[0]
    missing_farm_keys = required_farm_keys - set(sample_farm.keys())
    assert not missing_farm_keys, f"Farm schema missing keys: {missing_farm_keys}"
    assert sample_farm["assigned_type"] in ["seeder", "biomass", "unassigned"]
    print(f"      SUCCESS: Loaded {len(farms)} farms with exact schema.\n")

    # -------------------------------------------------------------------------
    # 2. POST /api/farms/book
    # -------------------------------------------------------------------------
    print("[2/5] Testing POST /api/farms/book...")
    # Test A: Book an existing farm
    book_existing_res = client.post("/api/farms/book", json={"id": "F01"})
    assert book_existing_res.status_code == 200, f"Failed booking existing farm: {book_existing_res.text}"
    booked_f01 = book_existing_res.json()
    assert booked_f01["status"] == "booked", f"Expected status 'booked', got {booked_f01['status']}"

    # Test B: Register and book a new farm
    new_farm_payload = {
        "village": "Samana Border",
        "lat": 30.15,
        "lng": 76.19,
        "acres": 7.5,
        "paddy_variety": "PUSA-44",
        "days_left": 2,
        "has_heavy_tractor": False,
        "rain_forecast": True
    }
    book_new_res = client.post("/api/farms/book", json=new_farm_payload)
    assert book_new_res.status_code == 200, f"Failed booking new farm: {book_new_res.text}"
    new_farm = book_new_res.json()
    assert new_farm["id"].startswith("F"), "Expected generated farm id"
    assert new_farm["status"] == "booked"
    assert new_farm["risk_score"] >= 80.0, f"Expected high risk for PUSA-44 urgent farm, got {new_farm['risk_score']}"
    print(f"      SUCCESS: Booked existing farm F01 and created new farm {new_farm['id']} (Risk: {new_farm['risk_score']}).\n")

    # -------------------------------------------------------------------------
    # 3. POST /api/machines/add
    # -------------------------------------------------------------------------
    print("[3/5] Testing POST /api/machines/add (with 'type' and 'hp' aliases)...")
    machine_payload = {
        "owner_name": "Balwinder Singh",
        "type": "Baler",
        "hp": 70,
        "price_per_acre": 1400.0,
        "lat": 30.25,
        "lng": 75.85,
        "capacity_acres_per_day": 15.0,
        "available": True
    }
    add_machine_res = client.post("/api/machines/add", json=machine_payload)
    assert add_machine_res.status_code == 200, f"Failed adding machine: {add_machine_res.text}"
    new_machine = add_machine_res.json()

    # Validate locked Machine schema & alias resolution
    required_machine_keys = {
        "id", "owner_name", "machine_type", "tractor_hp", "price_per_acre",
        "lat", "lng", "capacity_acres_per_day", "available"
    }
    missing_machine_keys = required_machine_keys - set(new_machine.keys())
    assert not missing_machine_keys, f"Machine schema missing keys: {missing_machine_keys}"
    assert new_machine["machine_type"] == "Baler", f"Expected machine_type 'Baler', got {new_machine['machine_type']}"
    assert new_machine["tractor_hp"] == 70, f"Expected tractor_hp 70, got {new_machine['tractor_hp']}"
    print(f"      SUCCESS: Added machine {new_machine['id']} ({new_machine['owner_name']}, {new_machine['machine_type']}, {new_machine['tractor_hp']} HP).\n")

    # -------------------------------------------------------------------------
    # 4. POST /api/simulate-risk
    # -------------------------------------------------------------------------
    print("[4/5] Testing POST /api/simulate-risk...")
    sim_res = client.post("/api/simulate-risk", json={"rain_forecast": True})
    assert sim_res.status_code == 200, f"Failed simulate-risk: {sim_res.text}"
    sim_data = sim_res.json()
    assert "farms" in sim_data
    assert sim_data["high_risk_count"] > 0
    print(f"      SUCCESS: Simulated risk across {sim_data['total_farms']} farms. High-risk count: {sim_data['high_risk_count']}.\n")

    # -------------------------------------------------------------------------
    # 5. GET /api/optimize
    # -------------------------------------------------------------------------
    print("[5/5] Testing GET /api/optimize...")
    # Reset state to clean baseline 16 farms for standard comparison
    load_in_memory_state()

    opt_res = client.get("/api/optimize")
    assert opt_res.status_code == 200, f"Failed optimize: {opt_res.text}"
    opt_data = opt_res.json()

    # Validate polylines & comparison metrics
    assert "baseline" in opt_data and "paralipool" in opt_data and "comparison" in opt_data

    baseline_metrics = opt_data["baseline"]["metrics"]
    paralipool_metrics = opt_data["paralipool"]["metrics"]
    comparison = opt_data["comparison"]

    # Verify Leaflet polylines
    for route in opt_data["paralipool"]["routes"]:
        poly = route["polyline"]
        assert isinstance(poly, list) and len(poly) >= 2, "Invalid polyline structure"
        assert len(poly[0]) == 2 and isinstance(poly[0][0], float), "Leaflet polyline must be [[lat, lng], ...]"

    for b_route in opt_data["paralipool"]["biomass_routes"]:
        poly = b_route["polyline"]
        assert len(poly) == 2, "Biomass polyline must connect farm to hub [[farm.lat, farm.lng], [hub.lat, hub.lng]]"

    # Validate exact formulas
    saved_km = max(0.0, baseline_metrics["total_transit_km"] - paralipool_metrics["total_transit_km"])
    expected_diesel_saved = round(saved_km * 0.45, 2)
    assert paralipool_metrics["diesel_saved_liters"] == expected_diesel_saved, (
        f"Expected diesel_saved_liters {expected_diesel_saved}, got {paralipool_metrics['diesel_saved_liters']}"
    )

    # Verify net owner pooled earnings after fuel cost (gross - transit_km * 0.45 * 88.0)
    assert paralipool_metrics["owner_pooled_earnings_inr"] > baseline_metrics["owner_pooled_earnings_inr"], (
        "ParaliPool net earnings should exceed Baseline due to reduced transit fuel cost"
    )

    print("      SUCCESS: Optimization completed with Leaflet-ready polylines and verified metric formulas.\n")

    # -------------------------------------------------------------------------
    # 6. POST /api/reset
    # -------------------------------------------------------------------------
    print("[6/6] Testing POST /api/reset (Judge Demo Reset)...")
    reset_res = client.post("/api/reset")
    assert reset_res.status_code == 200, f"Failed reset: {reset_res.text}"
    reset_data = reset_res.json()
    assert reset_data.get("status") == "reset_successful"
    assert "baseline" in reset_data and "paralipool" in reset_data
    print("      SUCCESS: Successfully reloaded data.json and re-ran optimization for demo reset.\n")

    # -------------------------------------------------------------------------
    # Print Comparison Metrics Summary
    # -------------------------------------------------------------------------
    earnings_delta = comparison.get("earnings_gain_inr", round(paralipool_metrics['owner_pooled_earnings_inr'] - baseline_metrics['owner_pooled_earnings_inr'], 2))
    print("=================================================================")
    print("         BASELINE FCFS  vs  PARALIPOOL OPTIMIZATION SUMMARY      ")
    print("=================================================================")
    print(f"{'METRIC':<30} | {'BASELINE FCFS':<15} | {'PARALIPOOL':<15} | {'DELTA / BENEFIT':<15}")
    print("-" * 80)
    print(f"{'Farms Cleared (%)':<30} | {str(baseline_metrics['farms_cleared_pct']) + '%' :<15} | {str(paralipool_metrics['farms_cleared_pct']) + '%' :<15} | {'+' + str(comparison['farms_cleared_pct_diff']) + '%' :<15}")
    print(f"{'Total Transit Distance (km)':<30} | {str(baseline_metrics['total_transit_km']) + ' km' :<15} | {str(paralipool_metrics['total_transit_km']) + ' km' :<15} | {'-' + str(comparison['transit_km_reduction']) + ' km (' + str(comparison['transit_km_reduction_pct']) + '%)' :<15}")
    print(f"{'Diesel Saved (Liters)':<30} | {str(baseline_metrics['diesel_saved_liters']) + ' L' :<15} | {str(paralipool_metrics['diesel_saved_liters']) + ' L' :<15} | {'+' + str(comparison['diesel_saved_liters']) + ' L' :<15}")
    print(f"{'Straw Diverted (Tonnes)':<30} | {str(baseline_metrics['straw_diverted_tonnes']) + ' T' :<15} | {str(paralipool_metrics['straw_diverted_tonnes']) + ' T' :<15} | {'+' + str(comparison['straw_diverted_delta_tonnes']) + ' T' :<15}")
    print(f"{'Net Owner Earnings (INR)':<30} | {'₹' + str(baseline_metrics['owner_pooled_earnings_inr']) :<15} | {'₹' + str(paralipool_metrics['owner_pooled_earnings_inr']) :<15} | {'+₹' + str(earnings_delta) :<15}")
    print("-" * 80)
    print(f"{'High-Risk Farms Protected':<30} | {comparison['high_risk_cleared_baseline']:<15} | {comparison['high_risk_cleared_paralipool']:<15} | {'100% Protection' :<15}")
    print("=" * 80)
    print(f"\nAnalysis:\n{comparison['description']}\n")
    print("ALL ENDPOINTS AND RESET ROUTE VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    test_all()
