export const FILTERS = [
  { id: 'all', label: 'All Farms' },
  { id: 'high', label: 'High Risk Only' },
  { id: 'biomass', label: 'Biomass Fallback' },
]

export default function MapFilters({ value, onChange, counts }) {
  return (
    <div className="panel">
      <h3>Filter</h3>
      <div className="seg" role="group" aria-label="Map filter">
        {FILTERS.map((f) => (
          <button key={f.id} className={value === f.id ? 'seg__btn seg__btn--on' : 'seg__btn'} aria-pressed={value === f.id} onClick={() => onChange(f.id)}>
            {f.label}
            <b>{counts[f.id]}</b>
          </button>
        ))}
      </div>
    </div>
  )
}
