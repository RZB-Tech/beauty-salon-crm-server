import { useEffect } from 'react'

// Thin wrapper over window.Telegram.WebApp (loaded in index.html)
export const tg = window.Telegram?.WebApp

export function initTelegram() {
  tg?.ready()   // hide Telegram's loading placeholder
  tg?.expand()  // full height instead of half-screen
}

// Signed launch data - sent to the backend as `Authorization: tma <initData>`.
// Empty when the page is opened outside Telegram.
export const getInitData = () => tg?.initData || ''

export const getTelegramUser = () => tg?.initDataUnsafe?.user ?? null

/**
 * Asks the user to share their Telegram phone number. Resolves with
 * { response, phone }: `response` is the raw string Telegram signed - the backend
 * verifies it, so send it exactly as received; `phone` is for display only.
 */
export function requestContact() {
  return new Promise((resolve, reject) => {
    if (!tg?.requestContact) {
      reject(new Error('Эта версия Telegram не умеет делиться номером — обновите приложение.'))
      return
    }
    try {
      tg.requestContact((shared, event) => {
        if (!shared) {
          reject(new Error('Вы не поделились номером.'))
        } else if (!event?.response) {
          // telegram-web-app.js gives up fetching the signed contact after 3 s
          reject(new Error('Telegram не вернул номер — попробуйте еще раз.'))
        } else {
          resolve({ response: event.response, phone: event.responseUnsafe?.contact?.phone_number ?? '' })
        }
      })
    } catch (e) {
      // Unsupported version, or a request is already open
      reject(new Error(`Не удалось запросить номер: ${e.message}`))
    }
  })
}

// Telegram's native back button (top-left in the mini app header) while a screen is open.
// Returns false when it isn't available, so the screen can render its own back link.
export function useBackButton(onBack) {
  const button = tg?.isVersionAtLeast?.('6.1') ? tg.BackButton : null
  useEffect(() => {
    if (!button || !onBack) return
    button.onClick(onBack)
    button.show()
    return () => {
      button.offClick(onBack)
      button.hide()
    }
  }, [button, onBack])
  return Boolean(button)
}
