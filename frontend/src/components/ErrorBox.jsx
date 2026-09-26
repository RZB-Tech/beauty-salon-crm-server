// Plain-language text for errors a client can run into; the raw code is always shown too,
// which helps while testing against the backend
function friendlyMessage(error) {
  switch (error.code) {
    case 'TOO_MANY_PENDING_APPOINTMENT_REQUESTS':
      return error.metadata?.scope === 'total'
        ? `У вас уже ${error.metadata.limit} заявок в ожидании во всех салонах. Дождитесь ответа или отмените одну из них.`
        : `У вас уже ${error.metadata?.limit} заявки в ожидании в этом салоне. Дождитесь ответа или отмените одну из них.`
    case 'CLIENT_APPOINTMENT_REQUEST_TIME_CONFLICT':
      return 'У вас уже есть заявка или запись на это время.'
    case 'BOOKING_TIME_IN_PAST':
      return 'Выбранное время уже прошло.'
    case 'TENANT_BOOKING_UNAVAILABLE':
      return 'Этот салон сейчас не принимает онлайн-запись.'
    case 'SERVICE_NOT_BOOKABLE':
      return `Услугу «${error.metadata?.name ?? ''}» сейчас нельзя заказать онлайн.`
    case 'APPOINTMENT_REQUEST_CANNOT_BE_CANCELLED':
      return 'Эту заявку уже нельзя отменить.'
    case 'APPOINTMENT_IS_FINISHED':
      return 'Визит уже состоялся — отменить нельзя.'
    default:
      return error.message
  }
}

export default function ErrorBox({ error }) {
  return (
    <div className="error">
      <p>{friendlyMessage(error)}</p>
      {error.code && <code>{error.code}{error.status ? ` · ${error.status}` : ''}</code>}
      {error.metadata?.field && <code>{error.metadata.field}: {error.metadata.message}</code>}
    </div>
  )
}
