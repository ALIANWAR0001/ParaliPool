import { RISK_LEVELS } from '../data/farms'
import { ROUTE_MODES, baselineLegend, optimizedLegend } from '../data/routes'

export default function MapLegend({ mode, showRoutes }) {
  const routes = mode === ROUTE_MODES.BASELINE ? baselineLegend : optimizedLegend
  return (
    <div className="panel">
      <h3>Legend</h3>
      <ul className="legend">
        {Object.values(RISK_LEVELS).map((r) => (
          <li key={r.label}><i className="dot" style={{ background: r.color }} />{r.label} <small>{r.min === 70 ? '70–100' : r.min === 40 ? '40–69' : '0–39'}</small></li>
        ))}
        <li><i className="sw sw--machine" />CHC / Super Seeder</li>
        <li><i className="sw sw--biomass" />Biomass centre / brick kiln</li>
      </ul>
      {showRoutes ? (
        <>
          <h4>{mode === ROUTE_MODES.BASELINE ? 'Baseline routes (illustrative)' : 'Optimized routes (illustrative)'}</h4>
          <ul className="legend">
            {routes.map((r) => (
              <li key={r.label}><i className="line" style={{ borderTopColor: r.color, borderTopStyle: r.dashed ? 'dashed' : 'solid' }} />{r.label}</li>
            ))}
          </ul>
        </>
      ) : null}
    </div>
  )
}
