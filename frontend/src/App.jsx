import { useMemo, useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import StatCard from './components/StatCard'
import MapView from './components/MapView'
import MapFilters from './components/MapFilters'
import RouteControls from './components/RouteControls'
import MapLegend from './components/MapLegend'
import { farms } from './data/farms'
import { machines } from './data/machines'
import { biomassCenters } from './data/biomassCenters'
import { ROUTE_MODES } from './data/routes'

const TITLES = {
  command: 'Command Center',
  map: 'Live Map',
  analytics: 'Route Analytics',
  farms: 'Farm Network',
  machinery: 'Machinery',
}

export default function App() {
  const [view, setView] = useState('command')
  const [menuOpen, setMenuOpen] = useState(false)
  const [filter, setFilter] = useState('all')
  const [mode, setMode] = useState(ROUTE_MODES.BASELINE)
  const [showRoutes, setShowRoutes] = useState(true)

  const stats = useMemo(() => {
    const high = farms.filter((f) => f.riskScore >= 70).length
    const fallback = farms.filter((f) => f.biomassFallback).length
    const available = machines.filter((m) => m.status === 'Available').length
    const collected = farms.filter((f) => f.pickupStatus === 'Collected').length
    return {
      total: farms.length,
      high,
      fallback,
      available,
      machines: machines.length,
      progress: Math.round((collected / farms.length) * 100),
      collected,
    }
  }, [])

  const counts = { all: farms.length, high: stats.high, biomass: stats.fallback }

  const visible = useMemo(() => {
    if (filter === 'high') {
      const fs = farms.filter((f) => f.riskScore >= 70)
      const mIds = new Set(fs.map((f) => f.assignedMachine))
      return { farms: fs, machines: machines.filter((m) => mIds.has(m.id)), biomass: [] }
    }
    if (filter === 'biomass') {
      const fs = farms.filter((f) => f.biomassFallback)
      const bIds = new Set(fs.map((f) => f.biomassCenterId))
      return { farms: fs, machines: [], biomass: biomassCenters.filter((b) => bIds.has(b.id)) }
    }
    return { farms, machines, biomass: biomassCenters }
  }, [filter])

  const isMap = view === 'command' || view === 'map'

  return (
    <div className="app">
      <Sidebar active={view} onSelect={setView} open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="main">
        <Header title={TITLES[view]} onMenu={() => setMenuOpen(true)} />
        {isMap ? (
          <div className="content">
            <section className="stats">
              <StatCard label="Total Farms" value={stats.total} hint="Patiala–Sangrur belt" accent="#38bdf8" />
              <StatCard label="High-Risk Farms" value={stats.high} hint="Risk score 70 or more" accent="#ef4444" />
              <StatCard label="Available Machines" value={`${stats.available}/${stats.machines}`} hint="CHC / Super Seeders" accent="#34d399" />
              <StatCard label="Biomass Fallback" value={stats.fallback} hint={`farms · ${biomassCenters.length} facilities`} accent="#f97316" />
              <StatCard label="Collection Progress" value={`${stats.progress}%`} hint={`${stats.collected} of ${stats.total} farms collected`} accent="#34d399" progress={stats.progress} />
            </section>

            <section className="workspace">
              <div className="mapcard">
                <MapView
                  farms={visible.farms}
                  machines={visible.machines}
                  biomassCenters={visible.biomass}
                  allFarms={farms}
                  allMachines={machines}
                  allBiomass={biomassCenters}
                  mode={mode}
                  showRoutes={showRoutes}
                />
                <div className={`modebadge ${mode === ROUTE_MODES.OPTIMIZED ? 'modebadge--opt' : ''}`}>
                  {showRoutes
                    ? mode === ROUTE_MODES.BASELINE
                      ? 'Baseline demonstration · sample routes'
                      : 'Optimized view · sample routes, not live optimization'
                    : 'Routes hidden'}
                </div>
              </div>
              <div className="controls">
                <MapFilters value={filter} onChange={setFilter} counts={counts} />
                <RouteControls mode={mode} onChange={setMode} showRoutes={showRoutes} onToggleRoutes={() => setShowRoutes((s) => !s)} />
                <MapLegend mode={mode} showRoutes={showRoutes} />
              </div>
            </section>
          </div>
        ) : (
          <div className="content">
            <div className="placeholder">
              <h2>{TITLES[view]}</h2>
              <p>This section belongs to another part of the ParaliPool project. The map and route tools live in Command Center and Live Map.</p>
              <button className="seg__btn seg__btn--on" onClick={() => setView('command')}>Back to Command Center</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
