export default function StatCard({ label, value, hint, accent = '#34d399', progress }) {
  return (
    <div className="stat" style={{ '--accent': accent }}>
      <span className="stat__label">{label}</span>
      <span className="stat__value">{value}</span>
      {progress !== undefined ? (
        <div className="stat__bar" role="progressbar" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
          <span style={{ width: `${progress}%` }} />
        </div>
      ) : null}
      {hint ? <span className="stat__hint">{hint}</span> : null}
    </div>
  )
}
