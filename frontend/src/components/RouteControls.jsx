import { ROUTE_MODES } from '../data/routes'

export default function RouteControls({ mode, onChange, showRoutes, onToggleRoutes }) {
  const baseline = mode === ROUTE_MODES.BASELINE
  return (
    <div className="panel">
      <h3>Route mode</h3>
      <div className="seg" role="group" aria-label="Route mode">
        <button className={baseline ? 'seg__btn seg__btn--on' : 'seg__btn'} aria-pressed={baseline} onClick={() => onChange(ROUTE_MODES.BASELINE)}>Today / Baseline</button>
        <button className={!baseline ? 'seg__btn seg__btn--on' : 'seg__btn'} aria-pressed={!baseline} onClick={() => onChange(ROUTE_MODES.OPTIMIZED)}>ParaliPool / Optimized</button>
      </div>
      <label className="check">
        <input type="checkbox" checked={showRoutes} onChange={onToggleRoutes} /> Show routes
      </label>
      <p className="note">
        {baseline
          ? 'Baseline demonstration: illustrative scattered trips, as collection can look today.'
          : 'Illustrative sample clusters for demonstration. No optimization algorithm is running.'}
      </p>
    </div>
  )
}
