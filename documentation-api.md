# API документация (для frontend команды)

Базовый URL: `/api/v1`

---

**Формат**: для каждого эндпоинта указаны: метод, путь, схема запроса, схема ответа, статус-коды и краткое описание.

**Общие схемы**

- `RequestAllObject` / `PaginationSchema` — общая пагинация и фильтрация (см. `src/schemas/base.py`).
- `BaseResponseSchema` — базовые поля ответа (включает: `id`, `created_at`, `updated_at`, `created_by`, `archived`).

---

## Аутентификация (open)

- POST `/api/v1/auth/login`
  - request: `src/schemas/auth/login.py::LoginSchema` (login, password)
  - response: `src/schemas/auth/login.py::LoginResponseSchema`
  - status: 200
  - описание: возвращает cookie с `access_token` и `refresh_token` и информацию о пользователе.
  - `LoginResponseSchema` поля (помимо `BaseResponseSchema`): `login`, `employee`, `firstname`, `lastname`, `middlename`, `active`, `staff_type`, `tenant_name`.

- POST `/api/v1/auth/refresh` — status 204 (обновление токенов)
- POST `/api/v1/auth/logout` — status 204 (выход)
- POST `/api/v1/auth/change-password` — status 204 (смена пароля)
- PATCH `/api/v1/auth/reset-password` — status 200, response: `str`

---

## Protected endpoints (требуют аутентификацию)

Ниже перечислены роуты, префиксы берутся из `src/routes/__init__.py`.

### Appointments (/api/v1/appointments)

- POST `` (create)
  - request: `src/schemas/appointment/create.py::AppointmentCreateSchema`
  - response: `src/schemas/appointment/response.py::AppointmentResponseSchema`
  - status: 201
- PATCH `` (update)
  - request: `src/schemas/appointment/update.py::AppointmentUpdateSchema`
  - response: `AppointmentResponseSchema`
  - status: 200
- POST `/get-all`
  - request: `src/schemas/base.py::RequestAllObject`
  - response: `src/schemas/base.py::PaginatedResponseSchema[AppointmentResponseSchema]`
  - status: 200
- GET `/{id}` — получить посещение по ID (200)
- PATCH `/{id}/cancel` — отмена посещения (200)
- GET `/{id}/receipts` — чекы по посещению (200)

### Appointment Records (/api/v1/appointments-records)

- POST `` (create record)
  - request: `src/schemas/appointment/create.py::AppointmentRecordsCreateSchema`
  - response: `src/schemas/appointment/response.py::AppointmentResponseSchema`
  - status: 201
- DELETE `/{id}` — удалить запись (возвращает `AppointmentResponseSchema`, status 200)

### Appointment Services (/api/v1/appointments-services)

- POST `` (create service record)
  - request: `src/schemas/appointment/create.py::AppointmentServicesCreateSchema`
  - response: `src/schemas/appointment/response.py::AppointmentResponseSchema`
  - status: 201
- PATCH `` (update)
  - request: `src/schemas/appointment/update.py::AppointmentServiceUpdateSchema`
  - response: `AppointmentResponseSchema`
  - status: 200
- DELETE `/{id}` — удалить запись, status 200

### Employees (/api/v1/employees)

- POST `` (create)
  - request: `src/schemas/employee/create.py::EmployeeCreateSchema`
  - response: `src/schemas/employee/response.py::EmployeeResponseBase`
  - status: 201
- POST `/get-all` — пагинированный список (`RequestAllObject` -> `PaginatedResponseSchema[EmployeeResponseBase]`)
- GET `/{id}` — получить сотрудника (200)
- PATCH `` — обновить (200)
- GET `/{id}/work-schedules` — рабочие графики и отсутствия (200)
- GET `/{id}/payrolls` — зарплаты сотрудника (пагинация)
- GET `/{id}/appointments` — посещения сотрудника (пагинация)

### Specializations (/api/v1/specializations)

- POST `` — create (`SpecializationCreateSchema`) -> `SpecializationResponseSchema` (201)
- PATCH `` — update (200)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)
- DELETE `/{id}` — delete (204)

### Work schedules (/api/v1/work-schedules)

- POST `` — create (`src/schemas/work_schedule/create.py`) -> `WorkScheduleResponseSchema` (201)
- PATCH `` — update (200)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)
- DELETE `/{id}` — delete (204)

### Absences (/api/v1/absences)

- POST `` — create (`AbsenceCreateSchema`) -> `AbsenceResponseSchema` (201)
- PATCH `` — update (200)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)
- DELETE `/{id}` — delete (204)

### Transactions (/api/v1/transactions)

- POST `` — create (`src/schemas/transaction/create.py`) -> `TransactionResponseSchema` (201)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)
- POST `/{id}/cancel` — cancel transaction (200)

### Receipts (/api/v1/receipts)

- POST `` — create (`src/schemas/payment/create.py::ReceiptCreateSchema`) -> `ReceiptResponseSchema` (201)
- POST `/get-all` — paginated (200)
- POST `/cancel` — cancel receipt (200)

### Payments (/api/v1/payments)

- POST `` — create (`src/schemas/payment/create.py::PaymentCreateSchema`) -> `src/schemas/payment/response.py::ReceiptResponseSchema` (201)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)

### Payrolls (/api/v1/payrolls)

- POST `` — create (`src/schemas/payroll/create.py`) -> `PayrollResponseSchema` (201)
- PATCH `` — update (200)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)
- DELETE `/{id}` — delete (204)
- POST `/cancel` — cancel payroll (200)

### Payouts (/api/v1/payouts)

- POST `` — create (`src/schemas/payout/create.py`) -> `PayoutResponseSchema` (201)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)

### Clients (/api/v1/clients)

- POST `` — create (`src/schemas/client/create.py`) -> `ClientResponseSchema` (201)
- PATCH `` — update (200)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)
- POST `/update-deposit` — обновить депозит (`ClientDepositUpdateSchema`) -> `ClientResponseSchema` (200)
- GET `/{id}/appointments` — appointments for client (paginated)

### Materials (/api/v1/materials)

- POST `` — create (`src/schemas/material/create.py`) -> `MaterialResponseSchema` (201)
- PATCH `` — update (200)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)
- POST `/update-quantity` — update quantity (`MaterialQuantityUpdateSchema`) -> `MaterialResponseSchema` (200)

### Services (/api/v1/services)

- POST `` — create (`src/schemas/service.py::ServiceCreateSchema`) -> `ServiceResponseSchema` (201)
- PATCH `` — update (200)
- POST `/get-all` — paginated (200)
- GET `/{id}` — get (200)
- POST `/import` — импорт из Excel (file upload)

### Service categories (/api/v1/service-categories)

- (аналогично) CRUD + get-all (см. `src/routes/serviceCategory_router.py`)

### Notifications (/api/v1/notifications)

- POST `` — create (`src/schemas/notification/create.py`) -> `NotificationResponseSchema` (201)
- POST `/get-all` — paginated (200)
- GET `/stream` — Server-Sent Events (SSE) stream для текущего staff (подключение к Redis pubsub)
- GET `/{id}` — get (200)
- DELETE `/{id}` — archive (200)
- DELETE `/{id}` — delete (204)

### Audit logs (/api/v1/audit-logs)

- GET `` — paginated audit logs (200)

---

## Возможные ошибки (генерируются на уровне сервисов)

Ниже перечислены ключевые ошибки, которые возникают в сервисах (код ответа и сообщение), собраны из `src/services`:

- `appointment_service`:
  - 409 — "Appointment slot already taken by this client"
  - 404 — "Посещение с ID {id} не найден"
  - 400/409 — разные проверки целостности (архивированные сущности, некорректные операции)

- `appointmentRecords_service` / `appointmentServices_service`:
  - 400 — "Необходимо сначало отменить активный чек для этого посещения"
  - 404 — _entity_ not found (material/service/appointmentRecord)
  - 409 — попытка использовать архивированные объекты

- `auth_service`:
  - 404 — "Некорректный логин или пароль"
  - 401 — "Пользователь неактивен" / "Невалидный токен"

- `client_service`:
  - 4xx/409 — валидационные ошибки и конфликты (например дубликаты)

- `employee_service`:
  - 404 — связанные объекты не найдены
  - 409 — попытка привязать архивированную услугу/специализацию

- `material_service`, `receipt_service`, `service_service`:
  - 400 — валидация (пустые поля, некорректные операции)
  - 404 — сущность не найдена
  - 409 — использование архивированных сущностей

- `payout_service`, `payroll_service`, `transaction_service`:
  - 404 — не найдено
  - 400/409 — логика бизнес-ограничений (например, нельзя отменять автоматически сгенерированные транзакции/выплаты)

Обратите внимание: сообщения ошибок могут содержать русские тексты с контекстом (см. соответствующие файлы в `src/services/*_service.py`).

---

## Полезные файлы и схемы

- Общие схемы: `src/schemas/base.py`
- Аутентификация: `src/schemas/auth/login.py`
- Модели сущностей и поля ответов находятся в `src/schemas/*/response.py` и запросов в `src/schemas/*/create.py` / `update.py`.

---

## Рекомендации для frontend команды

- Для всех `get-all` endpoints используйте `RequestAllObject` (`filters`, `page`, `pageSize`).
- SSE: подключение к `/api/v1/notifications/stream` требует авторизации (cookie) и поддерживает события `connected` и `notification`.
- Для операций, которые изменяют состояние (create/update/delete), следите за статус-кодами 201/200/204 и обрабатывайте 4xx ошибки, где тело ошибки содержит `detail`.
- Для операций, которые изменяют состояние (create/update/delete), следите за статус-кодами 201/200/204 и обрабатывайте 4xx ошибки, где тело ошибки содержит `detail`.

---

## Доступные фильтры для `get-all` (поля)

Вы можете получить схему доступных фильтров программно через endpoint:
`GET /api/v1/docs/filters/{table}` — где `{table}` берётся из enum `FilterTables` (например: `appointments`, `clients`, `employees` и т.д.).

Ниже перечислены поля, которые можно указывать в `filters` у `RequestAllObject` для основных таблиц (в формате `field: type`):

- `appointments`:
  - `client_id`: number
  - `start_time_est`: datetime
  - `end_time_est`: datetime
  - `status`: enum (awaiting, cancelled, started, finished)
  - `paid`: boolean
  - `archived`: boolean

- `clients`:
  - `firstname`: string
  - `lastname`: string
  - `middlename`: string
  - `phone`: string
  - `birth_date`: date
  - `sex`: enum (male, female)
  - `archived`: boolean

- `employees`:
  - `firstname`: string
  - `lastname`: string
  - `middlename`: string
  - `phone`: string
  - `active`: boolean
  - `specialization_id`: number
  - `archived`: boolean

- `services`:
  - `name`: string
  - `price`: number
  - `category_id`: number
  - `archived`: boolean

- `service-categories`:
  - `name`: string
  - `archived`: boolean

- `materials`:
  - `article`: string
  - `name`: string
  - `measurement_unit`: enum (piece, pack, box, bottle, milliliter, liter, gramm, kilogram)
  - `quantity`: number
  - `volume`: number
  - `sell_price`: number
  - `archived`: boolean

- `notifications`:
  - `client_id`: number
  - `type`: enum (reminder, other)
  - `delivered_at`: datetime
  - `archived`: boolean

- `receipts`:
  - `total_amount`: number
  - `receipt_type`: enum (appointment, direct sale)
  - `status`: enum (pending, paid, cancelled)
  - `archived`: boolean

- `payments`:
  - `amount`: number
  - `receipt_id`: number
  - `method`: enum (cash, card, deposit)
  - `archived`: boolean

- `transactions`:
  - `amount`: number
  - `type`: enum (income, expense)
  - `method`: enum (card, cash, bank transfer, deposit)
  - `category`: enum (receipt, employee payment, utility, internet, telephone, other)
  - `cancelled`: boolean
  - `auto_generated`: boolean
  - `archived`: boolean

- `employee_work_schedules`:
  - `day`: date
  - `start_time`: string (time)
  - `end_time`: string (time)
  - `archived`: boolean

- `employee_absences`:
  - `employee_id`: number
  - `start_date`: date
  - `end_date`: date
  - `absence_type`: enum (sick, vacation, day off, weekend, other)
  - `archived`: boolean

---

## Схемы запросов (какие поля можно отправлять и правила валидации)

Ниже — краткая сводка основных Pydantic-схем запросов из `src/schemas` с перечислением полей и важными правилами валидации.

- `AppointmentCreateSchema` (`src/schemas/appointment/create.py`)
  - client_id: int (>=1)
  - start_time_est, end_time_est: datetime (микросекунды обрезаются); требуется `start_time_est < end_time_est`.
  - records: опциональный список `AppointmentRecordsCreateOptionalSchema`.
  - notes: str | None

- `AppointmentRecordsCreateSchema` / `AppointmentServicesCreateSchema`
  - AppointmentRecordsCreate: `appointment_id` (>=1), `employee_id` (>=1), `services` — список сервисов.
  - AppointmentServicesCreate: `appointment_record_id` (>=1, опционально для вложённых форм), `service_id` или `material_id` (обязательно один из двух, нельзя оба), `quantity` (>=1, по умолчанию 1), `price` (>=1, опционально), `price_changed_reason` (min_length=5 при изменении цены), `notes`.

- `AppointmentUpdateSchema` / `AppointmentServiceUpdateSchema` / `AppointmentCancelSchema` (`src/schemas/appointment/update.py`)
  - `id` (>=1) и остальные поля в `BaseUpdateSchema` (по крайней мере одно поле должно быть указано).
  - `status` ограничен набором {AWAITING, STARTED, FINISHED} при обновлении.
  - При обновлении услуги/товара нельзя одновременно указывать `service_id` и `material_id`.
  - `AppointmentCancelSchema` содержит `reason` (enum) и `id`.

- `ReceiptCreateSchema` / `PaymentCreateSchema` (`src/schemas/payment/create.py`)
  - `ReceiptCreateSchema`:
    - `receipt_type`: enum (APPOINTMENT или DIRECT_SALE)
    - Для `APPOINTMENT` требуется `appointment_id` (и нельзя указывать `client_id` или `receipt_items`)
    - Для прямой продажи (`DIRECT_SALE`) требуется `receipt_items` — список `material_id`+`quantity`; нельзя одновременно указать `appointment_id` и `receipt_items`.
  - `PaymentCreateSchema`:
    - `receipt_id` (>=1), `amount` (>=1), `method` (enum `PaymentMethodsEnum`), `add_change_to_deposit` (bool).
    - При `method == DEPOSIT` сервер дополнительно проверяет баланс клиента и может вернуть 400 при недостатке.

- `TransactionCreateSchema` (`src/schemas/transaction/create.py`)
  - `type`, `category`, `method` (enums), `amount` (>=1), `notes`.
  - Есть запрет на ручное создание транзакций для категорий `RECEIPT` и `EMPLOYEE_PAYMENT` (валидатор выбросит ошибку).

- `PayrollCreateSchema` / `PayrollUpdateSchema` (`src/schemas/payroll/*`)
  - `employee_id` (>=1), `amount` (>=1), `type` (enum), `notes`, `appointment_id` (опционально).
  - При обновлении `id` обязателен; на уровне сервисов есть дополнительные ограничения для `auto_generated` и `payout_id`.

- `PayoutCreateSchema` (`src/schemas/payout/create.py`)
  - `employee_id` (>=1), `type` (enum), `amount` (опционально), `method` (enum), `payrolls` (список id) или `start_date`/`end_date` для формирования по периоду.
  - Валидатор запрещает передавать одновременно `payrolls` и период; при `type` == SALARY/ADVANCE нельзя передавать `payrolls` или период.

- `ClientCreateSchema` / `ClientUpdateSchema` (`src/schemas/client/*`)
  - Create: `firstname`, `lastname`?, `middlename`?, `phone`?, `birth_date`?, `sex` (enum), `deposit` (int, default 0), `notes`.
  - Update: `id` обязателен; поля опциональны; `ClientDepositUpdateSchema` использует `operation` (1 или -1) и `amount` (>=1). Сервер запрещает отрицательный депозит.

- `EmployeeCreateSchema` / `EmployeeUpdateSchema` (`src/schemas/employee/*`)
  - Create: `firstname`, `lastname`?, `phone`?, `birth_date`, `active` (bool), `specialization_id`?, `services_ids` (list[int]), `salary_fixed`, `percent_from_services`, `percent_from_sales`.
  - Update: `id` обязателен; `services` — список id (>=1); при привязке проверяется, что услуги существуют и не архивированы.

- `MaterialCreateSchema` / `MaterialUpdateSchema` (`src/schemas/material/*`)
  - Create: `article`, `name`, `description`?, `quantity` (>=0), `measurement_unit` (enum), `volume` (>=0), `sell_price` (>=0).
  - Update: `id` обязателен; `MaterialQuantityUpdateSchema` использует `operation` (1 или -1) и `quantity` (>=1); нельзя получить отрицательный остаток.

- `ServiceCreateSchema` / `ServiceUpdateSchema` / `ServiceCategoryCreateSchema` (`src/schemas/service*`)
  - Service: `name`, `price` (>=0), `category_id` (opt). При архивировании услуги связи с сотрудниками очищаются.
  - ServiceCategory: `name`.

- `SpecializationCreateSchema` / `SpecializationUpdateSchema` — `name` (строка, max_length 255).

- `NotificationCreateSchema` (`src/schemas/notification/create.py`)
  - `client_id`?, `title` (max 50)?, `body` (строка), `type` (enum), `scheduled_at` (datetime).

- `SegmentationCreateSchema` (`src/schemas/segmentation/create.py`)
  - `name`, `description`, `criteria` (правила), `client_ids` (список id) — результат сохраняется в БД.

---

### Примеры `RequestAllObject` для `/get-all`

Ниже компактные JSON-примеры тела запроса `RequestAllObject` (поле `filters` — словарь фильтров, `page`/`pageSize` — пагинация, `sort` — опционально `field:direction`).

- `appointments/get-all` — ожидающие, неоплаченные посещения клиента `client_id=12`:

```json
{
  "filters": { "client_id": 12, "status": "awaiting", "paid": false },
  "page": 1,
  "pageSize": 20,
  "sort": "start_time_est:asc"
}
```

- `clients/get-all` — поиск по имени/телефону:

```json
{
  "filters": { "firstname": "Анна", "phone": "+79991234567" },
  "page": 1,
  "pageSize": 50
}
```

- `receipts/get-all` — оплаченные чеки прямых продаж:

```json
{
  "filters": { "receipt_type": "direct sale", "status": "paid" },
  "page": 1,
  "pageSize": 30,
  "sort": "total_amount:desc"
}
```

- `transactions/get-all` — приходные транзакции по карте:

```json
{
  "filters": { "type": "income", "method": "card" },
  "page": 1,
  "pageSize": 25
}
```

- `employees/get-all` — активные сотрудники с заданной специализацией:

```json
{
  "filters": { "active": true, "specialization_id": 3 },
  "page": 1,
  "pageSize": 20,
  "sort": "lastname:asc"
}
```

- `services/get-all` — услуги из категории `5` с ценой >= (серверная фильтрация по диапазону реализуется на клиенте через два запроса или дополнительный фильтр):

```json
{
  "filters": { "category_id": 5 },
  "page": 1,
  "pageSize": 50
}
```

- `service-categories/get-all` — категории по имени:

```json
{
  "filters": { "name": "Брови" },
  "page": 1,
  "pageSize": 25
}
```

- `materials/get-all` — материалы с определённой единицей измерения и минимальным количеством:

```json
{
  "filters": { "measurement_unit": "bottle", "quantity": 5 },
  "page": 1,
  "pageSize": 30
}
```

- `notifications/get-all` — непрочитанные напоминания для клиента `7`:

```json
{
  "filters": { "client_id": 7, "type": "reminder" },
  "page": 1,
  "pageSize": 20,
  "sort": "scheduled_at:asc"
}
```

- `payments/get-all` — платежи по конкретному чеку:

```json
{
  "filters": { "receipt_id": 42 },
  "page": 1,
  "pageSize": 20
}
```

- `payouts/get-all` — выплаты сотруднику `15`, только не отменённые:

```json
{
  "filters": { "employee_id": 15, "cancelled": false },
  "page": 1,
  "pageSize": 10
}
```

- `employee_work_schedules/get-all` — графики на определённый день:

```json
{
  "filters": { "day": "2026-07-06" },
  "page": 1,
  "pageSize": 50
}
```

- `employee_absences/get-all` — отсутствия сотрудника `9` в периоде (по start_date/end_date):

```json
{
  "filters": {
    "employee_id": 9,
    "start_date": "2026-07-01",
    "end_date": "2026-07-31"
  },
  "page": 1,
  "pageSize": 20
}
```
