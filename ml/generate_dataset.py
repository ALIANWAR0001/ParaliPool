from pathlib import Path
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "days_to_deadline",
    "farm_acres",
    "distance_to_chc_km",
    "queue_acres_ahead",
    "machine_capacity_per_day",
    "rain_delay_days",
    "available_machines_nearby",
]
TARGET_COLUMN = "deadline_miss"


def generate_synthetic_dataset(n_samples: int = 100_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Baseline Patiala-Sangrur harvest distributions
    days_to_deadline = rng.integers(1, 16, size=n_samples)
    farm_acres = np.round(rng.uniform(1.5, 22.0, size=n_samples), 1)
    distance_to_chc_km = np.round(rng.uniform(0.5, 22.0, size=n_samples), 1)
    queue_acres_ahead = np.round(rng.uniform(0.0, 50.0, size=n_samples), 1)
    machine_capacity_per_day = np.round(rng.uniform(5.0, 9.5, size=n_samples), 1)
    rain_delay_days = rng.choice([0, 1, 2, 3], size=n_samples, p=[0.68, 0.18, 0.10, 0.04])
    available_machines_nearby = rng.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.28, 0.30, 0.22, 0.12, 0.08])

    # --- Inject Real-World Operational Anomalies ---
    anomaly_roll = rng.random(size=n_samples)

    # Anomaly 1 (~10%): Machinery breakdown / blade clogging -> steep drop in daily capacity
    is_breakdown = anomaly_roll < 0.10
    machine_capacity_per_day = np.where(
        is_breakdown,
        np.round(rng.uniform(2.5, 4.2, size=n_samples), 1),
        machine_capacity_per_day,
    )

    # Anomaly 2 (~8%): Unseasonal western disturbance rainstorm -> 3 to 5 delay days + wet soil drag
    is_rainstorm = (anomaly_roll >= 0.10) & (anomaly_roll < 0.18)
    rain_delay_days = np.where(
        is_rainstorm,
        rng.integers(3, 6, size=n_samples),
        rain_delay_days,
    )

    # Anomaly 3 (~8%): Peak-week CHC congestion surge -> tight deadline + heavy queue + single machine
    is_peak_surge = (anomaly_roll >= 0.18) & (anomaly_roll < 0.26)
    days_to_deadline = np.where(is_peak_surge, rng.integers(1, 5, size=n_samples), days_to_deadline)
    queue_acres_ahead = np.where(
        is_peak_surge,
        np.round(rng.uniform(35.0, 65.0, size=n_samples), 1),
        queue_acres_ahead,
    )
    available_machines_nearby = np.where(is_peak_surge, 1, available_machines_nearby)

    # --- Operational Clearance Physics ---
    own_farm_days = farm_acres / machine_capacity_per_day
    parallel_queue_factor = 1.0 + 0.40 * (available_machines_nearby - 1)
    queue_clear_days = queue_acres_ahead / (machine_capacity_per_day * parallel_queue_factor)

    single_machine_penalty = np.where(available_machines_nearby == 1, 0.35, 0.10)
    travel_delay_days = (distance_to_chc_km / 25.0) + single_machine_penalty

    # Extra wet-soil harvesting friction during rainstorms + field variance
    wet_soil_drag = np.where(is_rainstorm, 0.50, 0.0)
    operational_noise = rng.normal(loc=0.0, scale=0.35, size=n_samples)

    required_days = (
        own_farm_days
        + queue_clear_days
        + travel_delay_days
        + rain_delay_days
        + wet_soil_drag
        + operational_noise
    )

    deadline_miss = (required_days > days_to_deadline).astype(int)

    return pd.DataFrame(
        {
            "days_to_deadline": days_to_deadline,
            "farm_acres": farm_acres,
            "distance_to_chc_km": distance_to_chc_km,
            "queue_acres_ahead": queue_acres_ahead,
            "machine_capacity_per_day": machine_capacity_per_day,
            "rain_delay_days": rain_delay_days,
            "available_machines_nearby": available_machines_nearby,
            TARGET_COLUMN: deadline_miss,
        }
    )


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    output_path = base_dir / "data" / "farm_risk_dataset.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_synthetic_dataset(n_samples=100_000, seed=42)
    df.to_csv(output_path, index=False)

    counts = df[TARGET_COLUMN].value_counts()
    pct = df[TARGET_COLUMN].value_counts(normalize=True) * 100

    print(f"Saved {len(df):,} rows to: {output_path}\n")
    print("Class Balance (deadline_miss):")
    print(f"  0 (On-Time Clearance): {counts[0]:,} ({pct[0]:.2f}%)")
    print(f"  1 (Deadline Miss):     {counts[1]:,} ({pct[1]:.2f}%)\n")
    print("Feature Correlations with deadline_miss:")
    print(df.corr(numeric_only=True)[TARGET_COLUMN].drop(TARGET_COLUMN).round(3).to_string())


if __name__ == "__main__":
    main()