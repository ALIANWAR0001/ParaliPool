const items = [
  { id: 'command', label: 'Command Center', d: 'M3 12l9-9 9 9M5 10v10h14V10' },
  { id: 'map', label: 'Live Map', d: 'M9 3L3 5v16l6-2 6 2 6-2V3l-6 2-6-2zM9 3v16M15 5v16' },
  { id: 'analytics', label: 'Route Analytics', d: 'M4 20V10M10 20V4M16 20v-7M22 20H2' },
  { id: 'farms', label: 'Farm Network', d: 'M12 22V12M12 12C12 7 8 5 4 5c0 4 2 7 8 7zM12 14c0-4 3-6 8-6 0 4-2 6-8 6z' },
  { id: 'machinery', label: 'Machinery', d: 'M3 17H2V9h9l2 4h6l2 3v2h-2M10 9V5h4M7 20a3 3 0 100-6 3 3 0 000 6z' },
]

export default function Sidebar({ active, onSelect, open, onClose }) {
  return (
    <>
      <div className={`scrim ${open ? 'scrim--on' : ''}`} onClick={onClose} />
      <aside className={`sidebar ${open ? 'sidebar--open' : ''}`}>
        <div className="brand">
          <span className="brand__mark">P</span>
          <div>
            <div className="brand__name">ParaliPool</div>
            <div className="brand__sub">Stubble logistics</div>
          </div>
        </div>
        <nav>
          {items.map((it) => (
            <button
              key={it.id}
              className={`nav ${active === it.id ? 'nav--active' : ''}`}
              onClick={() => { onSelect(it.id); onClose() }}
            >
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d={it.d} /></svg>
              {it.label}
            </button>
          ))}
        </nav>
        <div className="sidebar__foot">Demo build · mock data</div>
      </aside>
    </>
  )
}
