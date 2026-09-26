import { useCallback, useEffect, useState } from 'react'
import { ApiError, getProfile } from './api'
import { getInitData } from './telegram'
import ErrorBox from './components/ErrorBox'
import Booking from './screens/Booking'
import Profile from './screens/Profile'
import RegisterForm from './screens/Register'
import Requests from './screens/Requests'
import Salons from './screens/Salons'

export default function App() {
  // loading | outside-telegram | register | main | error
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
      setScreen('main')
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
    return <RegisterForm onRegistered={(p) => { setProfile(p); setScreen('main') }} />
  }

  return <Main profile={profile} onRefreshProfile={load} />
}

const TABS = [
  ['salons', 'Салоны'],
  ['requests', 'Мои заявки'],
  ['profile', 'Профиль'],
]

function Main({ profile, onRefreshProfile }) {
  const [tab, setTab] = useState('salons')
  const [tenant, setTenant] = useState(null) // salon being booked, within the "salons" tab
  const [notice, setNotice] = useState(null)

  const openTab = (next) => {
    setTab(next)
    setTenant(null)
    setNotice(null)
  }
  const backToSalons = useCallback(() => setTenant(null), [])

  function booked(request) {
    setNotice(`Заявка в «${request.tenant_name}» отправлена — ждем подтверждения салона.`)
    setTenant(null)
    setTab('requests')
  }

  return (
    <>
      <nav className="tabs">
        {TABS.map(([id, label]) => (
          <button key={id} className={tab === id ? 'active' : ''} onClick={() => openTab(id)}>{label}</button>
        ))}
      </nav>

      {notice && <p className="notice">{notice}</p>}

      {tab === 'salons' && (tenant
        ? <Booking tenant={tenant} onBack={backToSalons} onBooked={booked} />
        : <Salons onSelect={setTenant} />)}
      {tab === 'requests' && <Requests />}
      {tab === 'profile' && <Profile profile={profile} onRefresh={onRefreshProfile} />}
    </>
  )
}
