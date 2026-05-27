from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    SUPPORT_AGENT = "support_agent"
