from app.domain.exceptions.base import DomainException


class InvalidToken(DomainException):
    pass


class AccountAlreadyActivated(DomainException):
    pass


class UserAlreadyExists(DomainException):
    pass


class AccountIsNotActive(DomainException):
    pass


class InvalidCredentials(DomainException):
    pass


class PasswordTooShort(DomainException):
    pass
