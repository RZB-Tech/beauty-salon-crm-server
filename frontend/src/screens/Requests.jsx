import { useCallback, useEffect, useState } from 'react'
import { cancelRequest, getRequests } from '../api'
import { APPOINTMENT_STATUS, CANCELLED_REASON, REQUEST_STATUS, formatDateTime, formatPrice } from '../format'
import ErrorBox from '../components/ErrorBox'

const PAGE_SIZE = 20
const CANCELLABLE = ['pending', 'confirmed']

export default function Requests() {
  const [items, setItems] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [error, setError] = useState(null)
  const [loadingMore, setLoadingMore] = useState(false)

  const load = useCallback(async (pageToLoad) => {
    setError(null)
    try {
      const data = await getRequests(pageToLoad, PAGE_SIZE)
      setItems((prev) => (pageToLoad === 1 ? data.items : [...(prev ?? []), ...data.items]))
      setPage(pageToLoad)
      setTotalPages(data.totalPages)
    } catch (e) {
      setError(e)
    }
  }, [])

  useEffect(() => { load(1) }, [load])

  async function loadMore() {
    setLoadingMore(true)
    await load(page + 1)
    setLoadingMore(false)
  }

  const replace = (updated) => setItems((list) => list.map((r) => (r.id === updated.id ? updated : r)))

  if (!items && error) return <div className="card"><ErrorBox error={error} /><button onClick={() => load(1)}>Повторить</button></div>
  if (!items) return <p className="center muted">Загрузка…</p>

  return (
    <div className="card">
      <div className="header-row">
        <h1>Мои заявки</h1>
        <button className="link" onClick={() => load(1)}>Обновить</button>
      </div>
      {items.length === 0 && <p className="muted">Заявок пока нет — выберите салон и отправьте первую.</p>}
      {items.map((request) => <RequestCard key={request.id} request={request} onChanged={replace} />)}
      {error && <ErrorBox error={error} />}
      {page < totalPages && (
        <button className="secondary" onClick={loadMore} disabled={loadingMore}>{loadingMore ? 'Загрузка…' : 'Показать еще'}</button>
      )}
    </div>
  )
}

function RequestCard({ request, onChanged }) {
  const [cancelling, setCancelling] = useState(false) // the reason form is open
  const [reason, setReason] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const status = REQUEST_STATUS[request.status] ?? { label: request.status, tone: 'muted' }
  const total = request.services.reduce((sum, s) => sum + Number(s.price) * s.quantity, 0)

  async function confirmCancel() {
    setError(null)
    setBusy(true)
    try {
      onChanged(await cancelRequest(request.id, reason.trim()))
      setCancelling(false)
    } catch (e) {
      setError(e)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="request">
      <div className="header-row">
        <strong>{request.tenant_name}</strong>
        <span className={`badge ${status.tone}`}>{status.label}</span>
      </div>
      <div className="muted small">Желаемое время: {formatDateTime(request.start_time_est)}</div>

      <ul className="plain small">
        {request.services.map((s) => (
          <li key={s.service_id}>{s.name} × {s.quantity} — {formatPrice(Number(s.price) * s.quantity)}</li>
        ))}
      </ul>
      <div className="small">Итого: {formatPrice(total)}</div>

      {request.comment && <div className="muted small">Комментарий: {request.comment}</div>}
      {request.status === 'pending' && (
        <div className="muted small">Ждем ответа салона до {formatDateTime(request.expires_at)}</div>
      )}
      {request.appointment_status && (
        <div className="small">Визит: {APPOINTMENT_STATUS[request.appointment_status] ?? request.appointment_status}</div>
      )}
      {request.decline_reason && <div className="small">Причина отказа: {request.decline_reason}</div>}
      {request.status === 'cancelled' && (
        <div className="muted small">
          {CANCELLED_REASON[request.cancelled_reason] ?? request.cancelled_reason}
          {request.cancel_comment && `: ${request.cancel_comment}`}
        </div>
      )}

      {CANCELLABLE.includes(request.status) && !cancelling && (
        <button className="link danger" onClick={() => setCancelling(true)}>Отменить заявку</button>
      )}
      {cancelling && (
        <div className="cancel-form">
          <label>Причина отмены (необязательно)
            <textarea value={reason} onChange={(e) => setReason(e.target.value)} maxLength={1000} rows={2} />
          </label>
          {request.status === 'confirmed' && <p className="muted small">Запись в салоне тоже будет отменена.</p>}
          <div className="button-row">
            <button className="secondary" onClick={() => setCancelling(false)} disabled={busy}>Назад</button>
            <button className="danger-fill" onClick={confirmCancel} disabled={busy}>{busy ? 'Отмена…' : 'Отменить'}</button>
          </div>
        </div>
      )}
      {error && <ErrorBox error={error} />}
    </div>
  )
}
