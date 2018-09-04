

class SoapServerException(Exception):
    def __init__(self, error, code):
        super(SoapServerException, self).__init__(error, code)
        self.error = error
        self.code = code


class SoapClientException(Exception):
    pass


class TypeDoesNotExist(SoapClientException):
    def __init__(self, type_name):
        super(TypeDoesNotExist, self).__init__(type_name)
        self.type_name = type_name


class MethodDoesNotExist(SoapClientException):
    def __init__(self, method_name):
        super(MethodDoesNotExist, self).__init__(method_name)
        self.method_name = method_name


class InvalidSignatureResponse(SoapClientException):
    pass
