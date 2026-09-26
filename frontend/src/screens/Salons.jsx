import { useEffect, useState } from 'react'
import { getTenants } from '../api'
import ErrorBox from '../components/ErrorBox'

export default function Salons({ onSelect }) {
  const [tenants, setTenants] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getTenants().then(setTenants, setError)
  }, [])

  if (error) return <div className="card"><ErrorBox error={error} /></div>
  if (!tenants) return <p className="center muted">Загрузка…</p>

  return (
    <div className="card">
      <h1>Салоны</h1>
      {tenants.length === 0
        ? <p className="muted">Пока нет салонов с онлайн-записью.</p>
        : (
          <ul className="list">
            {tenants.map((tenant) => (
              <li key={tenant.id}>
                <button className="list-item" onClick={() => onSelect(tenant)}>
                  <span>{tenant.name}</span>
                  <span className="chevron">›</span>
                </button>
              </li>
            ))}
          </ul>
        )}
    </div>
  )
}
