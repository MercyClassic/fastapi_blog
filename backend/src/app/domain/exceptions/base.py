class DomainException(Exception):
    pass


class NotFound(DomainException):
    pass


class PermissionDenied(DomainException):
    pass
