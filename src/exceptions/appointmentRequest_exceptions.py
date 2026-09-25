from .base import BaseAppException

class AppointmentRequestNotFound(BaseAppException):
    statusCode = 404
    errorCode = "APPOINTMENT_REQUEST_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Appointment request ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class AppointmentRequestNotPending(BaseAppException):
    statusCode = 409
    errorCode = "APPOINTMENT_REQUEST_NOT_PENDING"
    def __init__(self, id: int, status: str):
        super().__init__(
            detail = f"Appointment request ID {id} is already {status}",
            errorCode = self.errorCode,
            id = id,
            status = status
        )

class AppointmentRequestExpired(BaseAppException):
    statusCode = 409
    errorCode = "APPOINTMENT_REQUEST_EXPIRED"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Appointment request ID {id} is past its confirmation time",
            errorCode = self.errorCode,
            id = id
        )

class AppointmentRequestServiceMissing(BaseAppException):
    statusCode = 409
    errorCode = "APPOINTMENT_REQUEST_SERVICE_DELETED"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Service of appointment request ID {id} no longer exists",
            errorCode = self.errorCode,
            id = id
        )

class AppointmentRequestCannotBeCancelled(BaseAppException):
    statusCode = 409
    errorCode = "APPOINTMENT_REQUEST_CANNOT_BE_CANCELLED"
    def __init__(self, id: int, status: str):
        super().__init__(
            detail = f"Appointment request ID {id} is {status}, only pending or confirmed requests can be cancelled",
            errorCode = self.errorCode,
            id = id,
            status = status
        )

class AppointmentIsFinished(BaseAppException):
    statusCode = 409
    errorCode = "APPOINTMENT_IS_FINISHED"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Appointment ID {id} is finished",
            errorCode = self.errorCode,
            id = id
        )

class TooManyPendingAppointmentRequests(BaseAppException):
    statusCode = 429
    errorCode = "TOO_MANY_PENDING_APPOINTMENT_REQUESTS"
    def __init__(self, limit: int):
        super().__init__(
            detail = f"No more than {limit} pending appointment requests per organization are allowed",
            errorCode = self.errorCode,
            limit = limit
        )

class ClientAppointmentRequestConflict(BaseAppException):
    statusCode = 409
    errorCode = "CLIENT_APPOINTMENT_REQUEST_TIME_CONFLICT"
    def __init__(self):
        super().__init__(
            detail = "Client already has an appointment request on this time",
            errorCode = self.errorCode
        )

class BookingSlotUnavailable(BaseAppException):
    statusCode = 409
    errorCode = "BOOKING_SLOT_UNAVAILABLE"
    def __init__(self):
        super().__init__(
            detail = "No employee is available for this service at this time",
            errorCode = self.errorCode
        )

class BookingTimeInPast(BaseAppException):
    statusCode = 400
    errorCode = "BOOKING_TIME_IN_PAST"
    def __init__(self):
        super().__init__(
            detail = "Requested time has already passed",
            errorCode = self.errorCode
        )

class ServiceNotBookable(BaseAppException):
    statusCode = 409
    errorCode = "SERVICE_NOT_BOOKABLE"
    def __init__(self, id: int, name: str):
        super().__init__(
            detail = f"Service {name} (ID {id}) cannot be booked online: it has no duration or no active employees",
            errorCode = self.errorCode,
            id = id,
            name = name
        )

class TenantBookingUnavailable(BaseAppException):
    statusCode = 404
    errorCode = "TENANT_BOOKING_UNAVAILABLE"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Organization {id} not found or does not accept Telegram bookings",
            errorCode = self.errorCode,
            id = id
        )

class GlobalClientProfileIncomplete(BaseAppException):
    statusCode = 409
    errorCode = "PROFILE_INCOMPLETE"
    def __init__(self, missing: list[str]):
        super().__init__(
            detail = f"Fill in the profile before requesting an appointment: {', '.join(missing)}",
            errorCode = self.errorCode,
            missing = missing
        )

class ContactNotOwnedByUser(BaseAppException):
    statusCode = 403
    errorCode = "TELEGRAM_CONTACT_NOT_OWNED"
    def __init__(self):
        super().__init__(
            detail = "Shared contact does not belong to the current Telegram user",
            errorCode = self.errorCode
        )

class ContactPhoneAlreadyUsed(BaseAppException):
    statusCode = 409
    errorCode = "CONTACT_PHONE_ALREADY_USED"
    def __init__(self):
        super().__init__(
            detail = "This phone number is already linked to another Telegram account",
            errorCode = self.errorCode
        )

class ClientLinkedToAnotherGlobalClient(BaseAppException):
    statusCode = 409
    errorCode = "CLIENT_LINKED_TO_ANOTHER_TELEGRAM_CLIENT"
    def __init__(self, id: int):
        super().__init__(
            detail = f"Client ID {id} is already linked to another Telegram client",
            errorCode = self.errorCode,
            id = id
        )

class GlobalClientAlreadyLinked(BaseAppException):
    statusCode = 409
    errorCode = "TELEGRAM_CLIENT_ALREADY_LINKED"
    def __init__(self, client_id: int):
        super().__init__(
            detail = f"This Telegram client is already linked to client ID {client_id}",
            errorCode = self.errorCode,
            client_id = client_id
        )
