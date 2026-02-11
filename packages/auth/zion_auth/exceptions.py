class ZionAuthError(RuntimeError):
    """
    A Generic, Zion Auth specific error.
    """


class ImproperlyConfiguredError(ZionAuthError):
    """
    An error is thrown when there is a problem with a setting value during the
    execution time
    """


class AuthenticationError(ZionAuthError):
    pass


class ValidationError(ZionAuthError):
    pass
