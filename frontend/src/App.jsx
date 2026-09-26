import { useCallback, useEffect, useState } from 'react'
import { ApiError, getProfile, register } from './api'
import { getInitData, getTelegramUser, requestContact } from './telegram'

export default function App() {
  // loading | outside-telegram | register | profile | error
  const [screen, setScreen] = useState('loading')
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    if (!getInitData()) {
      setScreen('outside-telegram')
      return
    }
    setScreen('loading')
    try {
      setProfile(await getProfile())
      setScreen('profile')
    } catch (e) {
      if (e instanceof ApiError && e.code === 'GLOBAL_CLIENT_NOT_REGISTERED') {
        setScreen('register')
      } else {
        setError(e)
        setScreen('error')
      }
    }
  }, [])

  useEffect(() => { load() }, [load])

  if (screen === 'loading') return <p className="center muted">Загрузка…</p>

  if (screen === 'outside-telegram') {
    return (
      <div className="card">
        <h1>Откройте в Telegram</h1>
        <p className="muted">Это мини-приложение работает только внутри Telegram — откройте его через бота.</p>
      </div>
    )
  }

  if (screen === 'error') {
    return (
      <div className="card">
        <h1>Ошибка</h1>
        <ErrorBox error={error} />
        <button onClick={load}>Повторить</button>
      </div>
    )
  }

  if (screen === 'register') {
    return <RegisterForm onRegistered={(p) => { setProfile(p); setScreen('profile') }} />
  }

  return <Profile profile={profile} onRefresh={load} />
}

function RegisterForm({ onRegistered }) {
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

function Profile({ profile, onRefresh }) {
  const rows = [
    ['Имя', `${profile.firstname} ${profile.lastname}${profile.middlename ? ` ${profile.middlename}` : ''}`],
    ['Пол', profile.sex === 'female' ? 'Женский' : 'Мужской'],
    ['Дата рождения', profile.birth_date],
    ['Номер Telegram', profile.telegram_phone],
    ['Номер для звонков', profile.call_phone],
    ['Telegram ID', profile.telegram_user_id],
    ['Username', profile.telegram_username && `@${profile.telegram_username}`],
    ['Зарегистрирован', new Date(profile.created_at).toLocaleString()],
  ].filter(([, value]) => value)

  return (
    <div className="card">
      <h1>Вы зарегистрированы</h1>
      <dl>
        {rows.map(([label, value]) => (
          <div key={label} className="row"><dt>{label}</dt><dd>{value}</dd></div>
        ))}
      </dl>
      <button className="secondary" onClick={onRefresh}>Обновить</button>
    </div>
  )
}

function ErrorBox({ error }) {
  return (
    <div className="error">
      <p>{error.message}</p>
      {/* Error codes help while testing against the backend */}
      {error.code && <code>{error.code}{error.status ? ` · ${error.status}` : ''}</code>}
      {error.metadata?.field && <code>{error.metadata.field}: {error.metadata.message}</code>}
    </div>
  )
}
