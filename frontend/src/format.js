// Prices come from the API as strings ("100000.00")
export const formatPrice = (value) => `${Number(value).toLocaleString('ru-RU')} сум`

export function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return [h && `${h} ч`, m && `${m} мин`].filter(Boolean).join(' ') || '0 мин'
}

// The API works in UTC; show times in the phone's local time
export const formatDateTime = (iso) =>
  new Date(iso).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })

// Value for <input type="datetime-local"> (local time, minutes precision)
export function toLocalInputValue(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export const REQUEST_STATUS = {
  pending: { label: 'Ожидает подтверждения', tone: 'warn' },
  confirmed: { label: 'Подтверждена', tone: 'ok' },
  declined: { label: 'Отклонена', tone: 'danger' },
  cancelled: { label: 'Отменена', tone: 'muted' },
}

export const CANCELLED_REASON = {
  'cancelled by client': 'Отменена вами',
  'automatically: time to make action passed': 'Салон не ответил вовремя',
}

// Status of the appointment a confirmed request became (AppointmentStatus on the backend)
export const APPOINTMENT_STATUS = {
  awaiting: 'Запланирована',
  started: 'Идет',
  finished: 'Завершена',
  cancelled: 'Отменена салоном',
}
