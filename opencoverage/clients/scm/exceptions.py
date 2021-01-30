class APIException(Exception):
    ...


class NotFoundException(APIException):
    ...


class AuthorizationException(APIException):
    ...


class InstallationException(APIException):
    ...
