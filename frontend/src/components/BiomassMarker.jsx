import { Marker, Popup } from 'react-leaflet'
import { biomassIcon } from './markerIcons'

export default function BiomassMarker({ center }) {
  return (
    <Marker position={[center.lat, center.lng]} icon={biomassIcon(center.type)}>
      <Popup>
        <div className="pp-popup">
          <div className="pp-popup__head">
            <strong>{center.name}</strong>
          </div>
          <dl>
            <dt>Facility type</dt><dd>{center.type}</dd>
            <dt>Location</dt><dd>{center.location}</dd>
            <dt>Est. biomass capacity</dt><dd>{center.capacity}</dd>
            <dt>Collection</dt><dd>{center.collection}</dd>
          </dl>
        </div>
      </Popup>
    </Marker>
  )
}
