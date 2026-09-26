export default function Profile({ profile, onRefresh }) {
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
