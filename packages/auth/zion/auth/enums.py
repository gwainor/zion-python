from enum import StrEnum


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class CredentialType(StrEnum):
    EMAIL = "email"
    USERNAME = "username"
