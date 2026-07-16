from __future__ import annotations
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.repository.staff.staff_model import Staff

class PermissionCode(IntEnum):
    MATERIAL_CREATE = 1001
    MATERIAL_UPDATE = 1002
    MATERIAL_READ = 1003
    MATERIAL_UPDATE_QUANTITY = 1004

    APPOINTMENT_CREATE = 2001
    APPOINTMENT_UPDATE = 2002
    APPOINTMENT_READ = 2003
    APPOINTMENT_CANCEL = 2004
    APPOINTMENT_RECORDS_CREATE = 2011
    APPOINTMENT_RECORDS_DELETE = 2012
    APPOINTMENT_SERVICES_CREATE = 2021
    APPOINTMENT_SERVICES_UPDATE = 2022
    APPOINTMENT_SERVICES_DELETE = 2023

    CLIENT_CREATE = 3001
    CLIENT_UPDATE = 3002
    CLIENT_READ = 3003
    CLIENT_UPDATE_DEPOSIT = 3004
    CLIENT_FINANCE_REPORT = 3005
    SEGMENTATION_CREATE = 3011

    EMPLOYEE_CREATE = 4001
    EMPLOYEE_UPDATE = 4002
    EMPLOYEE_READ = 4003

    SERVICE_CREATE = 5001
    SERVICE_UPDATE = 5002
    SERVICE_READ = 5003
    SERVICE_IMPORT = 5004
    SERVICE_CATEGORY_CREATE = 5011
    SERVICE_CATEGORY_UPDATE = 5012
    SERVICE_CATEGORY_READ = 5013

    SPECIALIZATION_CREATE = 6001
    SPECIALIZATION_UPDATE = 6002
    SPECIALIZATION_READ = 6003
    SPECIALIZATION_DELETE = 6004

    WORK_SCHEDULE_CREATE = 7001
    WORK_SCHEDULE_UPDATE = 7002
    WORK_SCHEDULE_READ = 7003
    WORK_SCHEDULE_DELETE = 7004
    ABSENCE_CREATE = 7011
    ABSENCE_UPDATE = 7012
    ABSENCE_READ = 7013
    ABSENCE_DELETE = 7014

    PAYROLL_CREATE = 8001
    PAYROLL_UPDATE = 8002
    PAYROLL_READ = 8003
    PAYROLL_DELETE = 8004
    PAYROLL_CANCEL = 8005
    PAYOUT_CREATE = 8011
    PAYOUT_READ = 8012

    RECEIPT_CREATE = 9001
    RECEIPT_READ = 9002
    RECEIPT_MAKE_PAYMENT = 9003
    RECEIPT_CANCEL = 9004
    TRANSACTION_CREATE = 9011
    TRANSACTION_READ = 9012
    TRANSACTION_CANCEL = 9013

    NOTIFICATION_CREATE = 10001
    NOTIFICATION_READ = 10002
    NOTIFICATION_ARCHIVE = 10003
    NOTIFICATION_DELETE = 10004

    AUDIT_LOGS_READ = 11001

    TENANT_INTEGRATIONS_READ = 12001
    TENANT_PREFERENCES_READ = 12002
    TENANT_PREFERENCES_UPDATE = 12003

PERMISSIONS: dict[int, dict[str, str]] = {
    PermissionCode.MATERIAL_CREATE: {"resource": "материал", "name": "Создать материал"},
    PermissionCode.MATERIAL_UPDATE: {"resource": "материал", "name": "Обновить материал"},
    PermissionCode.MATERIAL_READ: {"resource": "материал", "name": "Просмотр материала"},
    PermissionCode.MATERIAL_UPDATE_QUANTITY: {"resource": "материал", "name": "Обновить количество материала"},

    PermissionCode.APPOINTMENT_CREATE: {"resource": "запись", "name": "Создать запись"},
    PermissionCode.APPOINTMENT_UPDATE: {"resource": "запись", "name": "Обновить запись"},
    PermissionCode.APPOINTMENT_READ: {"resource": "запись", "name": "Просмотр записи"},
    PermissionCode.APPOINTMENT_CANCEL: {"resource": "запись", "name": "Отменить запись"},
    PermissionCode.APPOINTMENT_RECORDS_CREATE: {"resource": "посещение", "name": "Создать посещение"},
    PermissionCode.APPOINTMENT_RECORDS_DELETE: {"resource": "посещение", "name": "Удалить посещение"},
    PermissionCode.APPOINTMENT_SERVICES_CREATE: {"resource": "услуга в записи", "name": "Добавить услугу в запись"},
    PermissionCode.APPOINTMENT_SERVICES_UPDATE: {"resource": "услуга в записи", "name": "Обновить услугу в записи"},
    PermissionCode.APPOINTMENT_SERVICES_DELETE: {"resource": "услуга в записи", "name": "Удалить услугу из записи"},

    PermissionCode.CLIENT_CREATE: {"resource": "клиент", "name": "Создать клиента"},
    PermissionCode.CLIENT_UPDATE: {"resource": "клиент", "name": "Обновить клиента"},
    PermissionCode.CLIENT_READ: {"resource": "клиент", "name": "Просмотр клиента"},
    PermissionCode.CLIENT_UPDATE_DEPOSIT: {"resource": "клиент", "name": "Обновить депозит клиента"},
    PermissionCode.CLIENT_FINANCE_REPORT: {"resource": "клиент", "name": "Просмотр финансового отчёта клиента"},
    PermissionCode.SEGMENTATION_CREATE: {"resource": "сегментация", "name": "Создать сегментацию"},

    PermissionCode.EMPLOYEE_CREATE: {"resource": "сотрудник", "name": "Создать сотрудника"},
    PermissionCode.EMPLOYEE_UPDATE: {"resource": "сотрудник", "name": "Обновить сотрудника"},
    PermissionCode.EMPLOYEE_READ: {"resource": "сотрудник", "name": "Просмотр сотрудника"},

    PermissionCode.SERVICE_CREATE: {"resource": "услуга", "name": "Создать услугу"},
    PermissionCode.SERVICE_UPDATE: {"resource": "услуга", "name": "Обновить услугу"},
    PermissionCode.SERVICE_READ: {"resource": "услуга", "name": "Просмотр услуги"},
    PermissionCode.SERVICE_IMPORT: {"resource": "услуга", "name": "Импорт услуг из Excel"},
    PermissionCode.SERVICE_CATEGORY_CREATE: {"resource": "категория услуг", "name": "Создать категорию услуг"},
    PermissionCode.SERVICE_CATEGORY_UPDATE: {"resource": "категория услуг", "name": "Обновить категорию услуг"},
    PermissionCode.SERVICE_CATEGORY_READ: {"resource": "категория услуг", "name": "Просмотр категории услуг"},

    PermissionCode.SPECIALIZATION_CREATE: {"resource": "специализация", "name": "Создать специализацию"},
    PermissionCode.SPECIALIZATION_UPDATE: {"resource": "специализация", "name": "Обновить специализацию"},
    PermissionCode.SPECIALIZATION_READ: {"resource": "специализация", "name": "Просмотр специализации"},
    PermissionCode.SPECIALIZATION_DELETE: {"resource": "специализация", "name": "Удалить специализацию"},

    PermissionCode.WORK_SCHEDULE_CREATE: {"resource": "график работы", "name": "Создать график работы"},
    PermissionCode.WORK_SCHEDULE_UPDATE: {"resource": "график работы", "name": "Обновить график работы"},
    PermissionCode.WORK_SCHEDULE_READ: {"resource": "график работы", "name": "Просмотр графика работы"},
    PermissionCode.WORK_SCHEDULE_DELETE: {"resource": "график работы", "name": "Удалить график работы"},
    PermissionCode.ABSENCE_CREATE: {"resource": "отсутствие", "name": "Создать отсутствие"},
    PermissionCode.ABSENCE_UPDATE: {"resource": "отсутствие", "name": "Обновить отсутствие"},
    PermissionCode.ABSENCE_READ: {"resource": "отсутствие", "name": "Просмотр отсутствия"},
    PermissionCode.ABSENCE_DELETE: {"resource": "отсутствие", "name": "Удалить отсутствие"},

    PermissionCode.PAYROLL_CREATE: {"resource": "расчёт зарплаты", "name": "Создать расчёт зарплаты"},
    PermissionCode.PAYROLL_UPDATE: {"resource": "расчёт зарплаты", "name": "Обновить расчёт зарплаты"},
    PermissionCode.PAYROLL_READ: {"resource": "расчёт зарплаты", "name": "Просмотр расчёта зарплаты"},
    PermissionCode.PAYROLL_DELETE: {"resource": "расчёт зарплаты", "name": "Удалить расчёт зарплаты"},
    PermissionCode.PAYROLL_CANCEL: {"resource": "расчёт зарплаты", "name": "Отменить расчёт зарплаты"},
    PermissionCode.PAYOUT_CREATE: {"resource": "выплата", "name": "Создать выплату"},
    PermissionCode.PAYOUT_READ: {"resource": "выплата", "name": "Просмотр выплаты"},

    PermissionCode.RECEIPT_CREATE: {"resource": "чек", "name": "Создать чек"},
    PermissionCode.RECEIPT_READ: {"resource": "чек", "name": "Просмотр чека"},
    PermissionCode.RECEIPT_MAKE_PAYMENT: {"resource": "чек", "name": "Провести оплату по чеку"},
    PermissionCode.RECEIPT_CANCEL: {"resource": "чек", "name": "Отменить чек"},
    PermissionCode.TRANSACTION_CREATE: {"resource": "транзакция", "name": "Создать транзакцию"},
    PermissionCode.TRANSACTION_READ: {"resource": "транзакция", "name": "Просмотр транзакции"},
    PermissionCode.TRANSACTION_CANCEL: {"resource": "транзакция", "name": "Отменить транзакцию"},

    PermissionCode.NOTIFICATION_CREATE: {"resource": "уведомление", "name": "Создать уведомление"},
    PermissionCode.NOTIFICATION_READ: {"resource": "уведомление", "name": "Просмотр уведомления"},
    PermissionCode.NOTIFICATION_ARCHIVE: {"resource": "уведомление", "name": "Архивировать уведомление"},
    PermissionCode.NOTIFICATION_DELETE: {"resource": "уведомление", "name": "Удалить уведомление"},

    PermissionCode.AUDIT_LOGS_READ: {"resource": "журнал аудита", "name": "Просмотр журнала аудита"},

    PermissionCode.TENANT_INTEGRATIONS_READ: {"resource": "интеграции организации", "name": "Просмотр интеграций организации"},
    PermissionCode.TENANT_PREFERENCES_READ: {"resource": "настройки организации", "name": "Просмотр настроек организации"},
    PermissionCode.TENANT_PREFERENCES_UPDATE: {"resource": "настройки организации", "name": "Обновить настройки организации"},
}

def compute_effective_permissions(staff: "Staff") -> list[int]:
    """Union of a staff's direct permission overrides and every role they hold. Assumes staff.roles is already loaded."""
    effective = set(staff.permissions or [])
    for role in staff.roles:
        effective.update(role.permissions or [])
    return sorted(effective)