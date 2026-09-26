import { useEffect, useMemo, useState } from 'react'
import { createRequest, getServices } from '../api'
import { formatDuration, formatPrice, toLocalInputValue } from '../format'
import { useBackButton } from '../telegram'
import ErrorBox from '../components/ErrorBox'

const MAX_QUANTITY = 20

export default function Booking({ tenant, onBack, onBooked }) {
  const hasNativeBack = useBackButton(onBack)
  const [services, setServices] = useState(null)
  const [loadError, setLoadError] = useState(null)
  const [quantities, setQuantities] = useState({}) // service id -> quantity
  const [start, setStart] = useState('')           // datetime-local value, local time
  const [comment, setComment] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    getServices(tenant.id).then(setServices, setLoadError)
  }, [tenant.id])

  const selected = useMemo(
    () => (services ?? []).filter((s) => quantities[s.id] > 0).map((s) => ({ ...s, quantity: quantities[s.id] })),
    [services, quantities],
  )
  const totalPrice = selected.reduce((sum, s) => sum + Number(s.price) * s.quantity, 0)
  const totalMinutes = selected.reduce((sum, s) => sum + s.estimated_time * s.quantity, 0)

  const change = (id, delta) => setQuantities((q) => ({
    ...q, [id]: Math.min(MAX_QUANTITY, Math.max(0, (q[id] ?? 0) + delta)),
  }))

  async function submit(e) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      onBooked(await createRequest({
        tenant_id: tenant.id,
        services: selected.map((s) => ({ service_id: s.id, quantity: s.quantity })),
        // The picked local time as an exact instant (the API stores UTC)
        start_time_est: new Date(start).toISOString(),
        comment: comment.trim() || null,
      }))
    } catch (err) {
      setError(err)
    } finally {
      setBusy(false)
    }
  }

  const back = !hasNativeBack && <button type="button" className="link" onClick={onBack}>‹ Все салоны</button>

  if (loadError) return <div className="card">{back}<ErrorBox error={loadError} /></div>
  if (!services) return <p className="center muted">Загрузка…</p>

  return (
    <form className="card" onSubmit={submit}>
      {back}
      <h1>{tenant.name}</h1>

      <h2>Услуги</h2>
      {services.length === 0 && <p className="muted">В этом салоне пока нет услуг для онлайн-записи.</p>}
      <ul className="list">
        {services.map((s) => (
          <li key={s.id} className="service">
            <div>
              <div>{s.name}</div>
              <div className="muted small">{formatPrice(s.price)} · {formatDuration(s.estimated_time)}</div>
            </div>
            <div className="stepper">
              <button type="button" onClick={() => change(s.id, -1)} disabled={!quantities[s.id]} aria-label="Меньше">−</button>
              <span>{quantities[s.id] ?? 0}</span>
              <button type="button" onClick={() => change(s.id, 1)} disabled={quantities[s.id] >= MAX_QUANTITY} aria-label="Больше">+</button>
            </div>
          </li>
        ))}
      </ul>

      {selected.length > 0 && (
        <p className="total">Итого: {formatPrice(totalPrice)} · примерно {formatDuration(totalMinutes)}</p>
      )}

      <label>Желаемое время начала *
        <input type="datetime-local" value={start} min={toLocalInputValue(new Date())} onChange={(e) => setStart(e.target.value)} required />
      </label>
      <p className="muted small">Салон подтвердит время или предложит другое — вам придет сообщение в Telegram.</p>

      <label>Комментарий
        <textarea value={comment} onChange={(e) => setComment(e.target.value)} maxLength={1000} rows={3} placeholder="Например, к какому мастеру хотите" />
      </label>

      {error && <ErrorBox error={error} />}

      <button type="submit" disabled={!selected.length || !start || busy}>{busy ? 'Отправка…' : 'Отправить заявку'}</button>
    </form>
  )
}
