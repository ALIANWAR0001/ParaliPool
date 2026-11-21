import { Marker, Popup } from 'react-leaflet'
import { machineIcon } from './markerIcons'

const STATUS_COLOR = { Available: '#34d399', Busy: '#f5b72e', 'Under Maintenance': '#ef4444' }

export default function MachineMarker({ machine }) {
  const color = STATUS_COLOR[machine.status] || '#34d399'
  return (
    <Marker position={[machine.lat, machine.lng]} icon={machineIcon('#38bdf8')}>
      <Popup>
        <div className="pp-popup">
          <div className="pp-popup__head">
            <strong>{machine.id}</strong>
            <span className="pp-pill" style={{ '--c': color }}>{machine.status}</span>
          </div>
          <dl>
            <dt>Name</dt><dd>{machine.name}</dd>
            <dt>Location</dt><dd>{machine.location}</dd>
            <dt>Machine type</dt><dd>{machine.type}</dd>
            <dt>Assigned capacity</dt><dd>{machine.capacity}</dd>
          </dl>
        </div>
      </Popup>
    </Marker>
  )
}
