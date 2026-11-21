// ILLUSTRATIVE SAMPLE ROUTES – NOT produced by any optimization algorithm.
// Each route is just an ordered list of IDs. The map resolves IDs to coordinates.
// Backend replacement: GET /api/routes?mode=baseline|optimized returning the same shape.

export const ROUTE_MODES = {
  BASELINE: 'baseline',
  OPTIMIZED: 'optimized',
}

// Baseline: scattered, criss-crossing trips (each starts at a machine, in a zig-zag order)
export const baselineRoutes = [
  { id: 'B-1', label: 'Trip A', color: '#fb923c', startId: 'CHC-01', stops: ['F-101', 'F-114', 'F-104', 'F-109', 'F-102'] },
  { id: 'B-2', label: 'Trip B', color: '#a78bfa', startId: 'CHC-04', stops: ['F-111', 'F-105', 'F-113', 'F-117', 'F-106'] },
  { id: 'B-3', label: 'Trip C', color: '#f472b6', startId: 'CHC-03', stops: ['F-108', 'F-116', 'F-110', 'F-103', 'F-112'] },
  { id: 'B-4', label: 'Trip D', color: '#60a5fa', startId: 'CHC-02', stops: ['F-107', 'F-115', 'F-118', 'F-113', 'F-101'] },
]

// Optimized (illustrative): farms grouped by nearby machine
export const optimizedRoutes = [
  { id: 'O-1', label: 'Patiala cluster', color: '#34d399', startId: 'CHC-01', stops: ['F-104', 'F-102', 'F-101', 'F-103'] },
  { id: 'O-2', label: 'Nabha cluster', color: '#22d3ee', startId: 'CHC-02', stops: ['F-118', 'F-106', 'F-105', 'F-107'] },
  { id: 'O-3', label: 'Samana cluster', color: '#a3e635', startId: 'CHC-03', stops: ['F-109', 'F-110', 'F-108'] },
  { id: 'O-4', label: 'Sangrur cluster', color: '#60a5fa', startId: 'CHC-04', stops: ['F-113', 'F-112', 'F-111', 'F-117'] },
  { id: 'O-5', label: 'Dhuri cluster', color: '#facc15', startId: 'CHC-05', stops: ['F-115', 'F-114', 'F-116'] },
]

export const BIOMASS_ROUTE_COLOR = '#f97316'
// Fallback routes (farm -> biomass facility) are derived from farms.biomassCenterId at draw time.

export const baselineLegend = [
  { color: '#fb923c', label: 'Trip A (from CHC-01)' },
  { color: '#a78bfa', label: 'Trip B (from CHC-04)' },
  { color: '#f472b6', label: 'Trip C (from CHC-03)' },
  { color: '#60a5fa', label: 'Trip D (from CHC-02)' },
]

export const optimizedLegend = [
  { color: '#34d399', label: 'Patiala cluster' },
  { color: '#22d3ee', label: 'Nabha cluster' },
  { color: '#a3e635', label: 'Samana cluster' },
  { color: '#60a5fa', label: 'Sangrur cluster' },
  { color: '#facc15', label: 'Dhuri cluster' },
  { color: BIOMASS_ROUTE_COLOR, label: 'Biomass fallback route', dashed: true },
]
