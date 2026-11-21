import { useEffect } from 'react'
import { MapContainer, TileLayer, Polyline, Tooltip, useMap } from 'react-leaflet'
import FarmMarker from './FarmMarker'
import MachineMarker from './MachineMarker'
import BiomassMarker from './BiomassMarker'
import { ROUTE_MODES, baselineRoutes, optimizedRoutes, BIOMASS_ROUTE_COLOR } from '../data/routes'

const CENTER = [30.29, 76.12] // between Patiala and Sangrur
const BOUNDS = [[30.08, 75.72], [30.47, 76.52]]

// Keeps tiles correct if the container size changes (sidebar, mobile rotate, etc.)
function ResizeFix() {
  const map = useMap()
  useEffect(() => {
    const el = map.getContainer()
    const ro = new ResizeObserver(() => map.invalidateSize())
    ro.observe(el)
    return () => ro.disconnect()
  }, [map])
  return null
}

function FitRegion() {
  const map = useMap()
  useEffect(() => { map.fitBounds(BOUNDS) }, [map])
  return null
}

export default function MapView({ farms, machines, biomassCenters, allFarms, allMachines, allBiomass, mode, showRoutes }) {
  const visibleFarmIds = new Set(farms.map((f) => f.id))
  const point = (id) => {
    const o = allFarms.find((f) => f.id === id) || allMachines.find((m) => m.id === id) || allBiomass.find((b) => b.id === id)
    return o ? [o.lat, o.lng] : null
  }

  const routeList = mode === ROUTE_MODES.BASELINE ? baselineRoutes : optimizedRoutes
  const lines = showRoutes
    ? routeList
        .map((r) => {
          const stops = r.stops.filter((id) => visibleFarmIds.has(id))
          const start = point(r.startId)
          const pts = [start, ...stops.map(point)].filter(Boolean)
          return { ...r, pts, hasFarms: stops.length > 0 }
        })
        .filter((r) => r.hasFarms && r.pts.length > 1)
    : []

  const fallbackLines =
    showRoutes && mode === ROUTE_MODES.OPTIMIZED
      ? farms.filter((f) => f.biomassFallback).map((f) => ({ id: f.id, pts: [[f.lat, f.lng], point(f.biomassCenterId)], to: f.biomassCenterId }))
      : []

  return (
    <MapContainer center={CENTER} zoom={10} minZoom={8} scrollWheelZoom zoomControl className="map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        maxZoom={19}
      />
      <ResizeFix />
      <FitRegion />

      {lines.map((r) => (
        <Polyline key={`${mode}-${r.id}`} positions={r.pts} pathOptions={{ color: r.color, weight: 4, opacity: 0.9 }}>
          <Tooltip sticky>{r.label} · {mode === ROUTE_MODES.BASELINE ? 'baseline (sample)' : 'optimized (sample)'}</Tooltip>
        </Polyline>
      ))}
      {fallbackLines.map((r) => (
        <Polyline key={`fb-${r.id}`} positions={r.pts} pathOptions={{ color: BIOMASS_ROUTE_COLOR, weight: 3, dashArray: '8 8', opacity: 0.95 }}>
          <Tooltip sticky>Biomass fallback: {r.id} → {r.to}</Tooltip>
        </Polyline>
      ))}

      {biomassCenters.map((b) => <BiomassMarker key={b.id} center={b} />)}
      {machines.map((m) => <MachineMarker key={m.id} machine={m} />)}
      {farms.map((f) => <FarmMarker key={f.id} farm={f} />)}
    </MapContainer>
  )
}
