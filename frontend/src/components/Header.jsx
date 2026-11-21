export default function Header({ title, onMenu }) {
  const today = new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
  return (
    <header className="header">
      <button className="header__menu" onClick={onMenu} aria-label="Open menu">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M4 6h16M4 12h16M4 18h16" /></svg>
      </button>
      <div className="header__title">
        <h1>{title}</h1>
        <span>Patiala–Sangrur, Punjab</span>
      </div>
      <div className="header__right">
        <span className="status"><i /> Map online</span>
        <span className="chip">Demo mode · {today}</span>
      </div>
    </header>
  )
}
