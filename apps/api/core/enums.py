import enum


class SystemSettingKey(enum.Enum):
    VIOLATION_TICKET_DUE_DATE = "violation_ticket_due_date"


class AccountStateType(enum.Enum):
    TYPE = "account_state"

    ACTIVE = "account_state_active"
    SUSPENDED = "account_state_suspended"
    DELETED = "account_state_deleted"