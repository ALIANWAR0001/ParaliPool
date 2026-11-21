// MOCK DATA – replace with GET /api/farms from the FastAPI backend.
// riskScore is a sample value, NOT output of a real neural network.

export const RISK_LEVELS = {
  HIGH: { label: 'HIGH RISK', color: '#ef4444', min: 70 },
  MEDIUM: { label: 'MEDIUM RISK', color: '#f5b72e', min: 40 },
  LOW: { label: 'LOW RISK', color: '#34d399', min: 0 },
}

export function getRiskCategory(score) {
  if (score >= 70) return 'HIGH'
  if (score >= 40) return 'MEDIUM'
  return 'LOW'
}

const raw = [
  ['F-101', 30.356, 76.43, 82, 'PR-126', 'CHC-01', 'Pending', null],
  ['F-102', 30.298, 76.465, 45, 'PUSA-44', 'CHC-01', 'Scheduled', null],
  ['F-103', 30.385, 76.355, 91, 'PR-128', 'CHC-01', 'In Progress', 'BIO-01'],
  ['F-104', 30.26, 76.39, 28, 'PR-126', 'CHC-01', 'Collected', null],
  ['F-105', 30.4, 76.19, 74, 'PUSA-44', 'CHC-02', 'Pending', 'BIO-02'],
  ['F-106', 30.35, 76.1, 52, 'PR-121', 'CHC-02', 'Scheduled', null],
  ['F-107', 30.42, 76.13, 33, 'PR-128', 'CHC-02', 'Collected', null],
  ['F-118', 30.31, 76.25, 66, 'PR-121', 'CHC-02', 'In Progress', null],
  ['F-108', 30.13, 76.24, 88, 'PUSA-44', 'CHC-03', 'Pending', 'BIO-02'],
  ['F-109', 30.2, 76.15, 41, 'PR-126', 'CHC-03', 'Scheduled', null],
  ['F-110', 30.18, 76.29, 19, 'PR-121', 'CHC-03', 'Collected', null],
  ['F-111', 30.28, 75.8, 77, 'PR-128', 'CHC-04', 'Pending', 'BIO-03'],
  ['F-112', 30.21, 75.89, 58, 'PUSA-44', 'CHC-04', 'In Progress', null],
  ['F-113', 30.23, 75.77, 36, 'PR-126', 'CHC-04', 'Collected', null],
  ['F-117', 30.28, 76.03, 71, 'PR-121', 'CHC-04', 'Pending', 'BIO-02'],
  ['F-114', 30.395, 75.83, 93, 'PR-128', 'CHC-05', 'Pending', 'BIO-03'],
  ['F-115', 30.35, 75.91, 47, 'PUSA-44', 'CHC-05', 'Scheduled', null],
  ['F-116', 30.43, 75.9, 22, 'PR-126', 'CHC-05', 'Collected', null],
]

export const farms = raw.map(([id, lat, lng, riskScore, cropVariety, assignedMachine, pickupStatus, biomassCenterId]) => ({
  id,
  lat,
  lng,
  riskScore,
  riskCategory: getRiskCategory(riskScore),
  cropVariety,
  assignedMachine,
  pickupStatus, // Pending | Scheduled | In Progress | Collected
  biomassFallback: biomassCenterId !== null,
  biomassCenterId, // which facility receives fallback straw
}))
