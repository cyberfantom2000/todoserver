
class ApiCoreException(Exception):
    pass


class InvalidCredentials(ApiCoreException):
    def __init__(self):
        ApiCoreException.__init__(self, 'Invalid username or password')


class CouldNotValidateCredentials(ApiCoreException):
    def __init__(self):
        ApiCoreException.__init__(self, 'Could not validate credentials')


class EntityNotFound(ApiCoreException):
    def __init__(self, entity):
        ApiCoreException.__init__(self, f'{entity} not found!')


class AccessDenied(ApiCoreException):
    def __init__(self):
        ApiCoreException.__init__(self, 'Access denied')


class InvalidArguments(ApiCoreException):
    pass


class InvalidCall(ApiCoreException):
    pass


class UnknownError(ApiCoreException):
    def __init__(self, msg):
        ApiCoreException.__init__(self, 'Unknown error: ' + msg)
