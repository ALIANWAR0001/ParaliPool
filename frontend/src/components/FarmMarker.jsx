import { Marker, Popup } from 'react-leaflet'
import { farmIcon } from './markerIcons'
import { RISK_LEVELS } from '../data/farms'

export default function FarmMarker({ farm }) {
  const level = RISK_LEVELS[farm.riskCategory]
  return (
    <Marker position={[farm.lat, farm.lng]} icon={farmIcon(level.color, farm.riskCategory === 'HIGH')}>
      <Popup>
        <div className="pp-popup">
          <div className="pp-popup__head">
            <strong>{farm.id}</strong>
            <span className="pp-pill" style={{ '--c': level.color }}>{level.label}</span>
          </div>
          <dl>
            <dt>Risk score</dt><dd>{farm.riskScore} / 100</dd>
            <dt>Crop variety</dt><dd>{farm.cropVariety}</dd>
            <dt>Assigned machine</dt><dd>{farm.assignedMachine}</dd>
            <dt>Pickup status</dt><dd>{farm.pickupStatus}</dd>
            <dt>Biomass fallback</dt><dd>{farm.biomassFallback ? `Required (${farm.biomassCenterId})` : 'Not required'}</dd>
          </dl>
          <p className="pp-popup__note">Sample score for demo only</p>
        </div>
      </Popup>
    </Marker>
  )
}
