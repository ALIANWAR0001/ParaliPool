import L from 'leaflet'

// CSS-based markers (L.divIcon) – no image files, so nothing can go missing in the build.

export function farmIcon(color, pulse = false) {
  return L.divIcon({
    className: 'pp-marker-wrap',
    html: `<span class="pp-farm ${pulse ? 'pp-farm--pulse' : ''}" style="--c:${color}"></span>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -12],
  })
}

export function machineIcon(color) {
  return L.divIcon({
    className: 'pp-marker-wrap',
    html: `<span class="pp-machine" style="--c:${color}"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#06231a" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="17" r="3"/><circle cx="18" cy="18" r="2"/><path d="M3 17H2V9h9l2 4h6l2 3v2M10 9V5h4"/></svg></span>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -18],
  })
}

export function biomassIcon(kind) {
  const glyph = kind === 'Brick Kiln' ? 'K' : 'B'
  return L.divIcon({
    className: 'pp-marker-wrap',
    html: `<span class="pp-biomass"><b>${glyph}</b></span>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -18],
  })
}
