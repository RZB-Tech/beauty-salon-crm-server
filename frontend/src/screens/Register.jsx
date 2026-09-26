import { useState } from 'react'
import { register } from '../api'
import { getTelegramUser, requestContact } from '../telegram'
import ErrorBox from '../components/ErrorBox'

export default function RegisterForm({ onRegistered }) {
  const user = getTelegramUser()
  const [form, setForm] = useState({
    firstname: user?.first_name ?? '',
    lastname: user?.last_name ?? '',
    middlename: '',
    birth_date: '',
    sex: '',
    call_phone: '',
  })
  const [contact, setContact] = useState(null) // { response, phone }
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  async function sharePhone() {
    setError(null)
    try {
      setContact(await requestContact())
    } catch (e) {
      setError(e)
    }
  }

  async function submit(e) {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      onRegistered(await register({
        firstname: form.firstname.trim(),
        lastname: form.lastname.trim(),
        sex: form.sex,
        // Optional fields: send null rather than empty strings
        middlename: form.middlename.trim() || null,
        birth_date: form.birth_date || null,
        call_phone: form.call_phone.trim() || null,
        contact: contact.response,
      }))
    } catch (e) {
      setError(e)
    } finally {
      setBusy(false)
    }
  }

  const ready = form.firstname.trim() && form.lastname.trim() && form.sex && contact

  return (
    <form className="card" onSubmit={submit}>
      <h1>Регистрация</h1>
      <p className="muted">Данные нужны салону, чтобы записать вас. Заполняются один раз.</p>

      <label>Имя *<input value={form.firstname} onChange={set('firstname')} required maxLength={255} /></label>
      <label>Фамилия *<input value={form.lastname} onChange={set('lastname')} required maxLength={255} /></label>
      <label>Отчество<input value={form.middlename} onChange={set('middlename')} maxLength={255} /></label>
      <label>Дата рождения<input type="date" value={form.birth_date} onChange={set('birth_date')} /></label>

      <fieldset>
        <legend>Пол *</legend>
        <label className="inline"><input type="radio" name="sex" value="female" checked={form.sex === 'female'} onChange={set('sex')} /> Женский</label>
        <label className="inline"><input type="radio" name="sex" value="male" checked={form.sex === 'male'} onChange={set('sex')} /> Мужской</label>
      </fieldset>

      <div className="field">
        <span>Номер Telegram *</span>
        {contact
          ? <p className="ok">✓ {contact.phone ? `+${contact.phone.replace(/^\+/, '')}` : 'Номер получен'}</p>
          : <button type="button" className="secondary" onClick={sharePhone}>Поделиться номером</button>}
      </div>

      <label>Номер для звонков<input type="tel" value={form.call_phone} onChange={set('call_phone')} placeholder="Если отличается от номера Telegram" maxLength={50} /></label>

      {error && <ErrorBox error={error} />}

      <button type="submit" disabled={!ready || busy}>{busy ? 'Отправка…' : 'Зарегистрироваться'}</button>
    </form>
  )
}
