class OperationException(Exception):
    def __init__(self, message):
        self.message = message


class VerificationException(Exception):
    def __init__(self, message):
        self.message = message


class AuthException(Exception):
    def __init__(self, message):
        self.message = message
