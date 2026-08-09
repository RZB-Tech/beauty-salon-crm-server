from .base import BaseAppException

class AppointmentNotFound(BaseAppException):
    statusCode = 404
    errorCode = "APPOINTMENT_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Appointment ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class AppointmentCancelled(BaseAppException):
    statusCode = 409
    errorCode = "APPOINTMENT_IS_CANCELLED"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Appointment ID {id} is cancelled",
            errorCode = self.errorCode,
            id = id
        )

class AppointmentHasActiveReceipts(BaseAppException):
    statusCode = 409
    errorCode = "APPOINTMENT_HAS_ACTIVE_RECEIPT"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Appointment ID {id} has active receipt",
            errorCode = self.errorCode,
            id = id
        )

class AppointmentIsPaid(BaseAppException):
    statusCode = 409
    errorCode = "APPOINTMENT_IS_PAID"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Appointment ID {id} is paid",
            errorCode = self.errorCode,
            id = id
        )

class ClientAppointmentConflict(BaseAppException):
    statusCode = 409
    errorCode = "CLIENT_APPOINTMENT_TIME_CONFLICT"
    def __init__(self):
        super().__init__(
            detail=f"Client already has appointment on this time",
            errorCode = self.errorCode,
        )

class EmployeeAppointmentConflict(BaseAppException):
    statusCode = 409
    errorCode = "EMPLYOYEE_APPOINTMENT_TIME_CONFLICT"
    def __init__(self, id: int, firstname: str):
        super().__init__(
            detail = f"Employee {firstname} (ID {id}) is busy during these hours",
            errorCode = self.errorCode,
            id = id,
            firstname = firstname
        )

class AppointmentRecordNotFound(BaseAppException):
    statusCode = 404
    errorCode = "APPOINTMENT_RECORD_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail=f"Appointment record ID {id} not found",
            errorCode = self.errorCode,
            id = id
        )

class AppointmentServiceNotFound(BaseAppException):
    statusCode = 404
    errorCode = "APPOINTMENT_SERVICE_NOT_FOUND"
    def __init__(self, id: int):
        super().__init__(
            detail = "Appointment record's service not found",
            errorCode = self.errorCode,
            id = id
        )

class AppointmentServiceHasToContainOnlyOne(BaseAppException):
    statusCode = 400
    errorCode = "APPOINTMENT_SERVICE_HAS_TO_CONTAIN_SERVICE_OR_MATERIAL"
    def __init__(self):
        super().__init__(
            detail = "Appointment record's service has to contain Service or Material",
            errorCode = self.errorCode
        )