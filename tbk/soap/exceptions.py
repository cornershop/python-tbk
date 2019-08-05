class SoapRequestException(Exception):
    def __init__(self, error, request):
        self.error = error
        self.request = request
        super(SoapRequestException, self).__init__(error)


class SoapServerException(Exception):
    def __init__(self, error, code, request):
        super(SoapServerException, self).__init__(error, code)
        self.error = error
        self.code = code
        self.request = request


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
    def __init__(self, envelope):
        super(InvalidSignatureResponse, self).__init__(envelope)
        self.envelope = envelope
