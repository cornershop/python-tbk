import logging

from .exceptions import SoapServerException, SoapClientException


class SoapRequest(object):
    def __init__(self, method_name, args, kwargs):
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        arguments = ", ".join(
            [
                part
                for part in [
                    ", ".join(str(arg) for arg in self.args),
                    ", ".join(
                        ["=".join(map(str, items)) for items in self.kwargs.items()]
                    ),
                ]
                if part
            ]
        )
        return "{method_name}({arguments})".format(
            method_name=self.method_name, arguments=arguments
        )


class SoapResponse(object):
    def __init__(self, result, request, envelope_sent, envelope_received):
        self.result = result
        self.request = request
        self.envelope_sent = envelope_sent
        self.envelope_received = envelope_received

    def __getitem__(self, key):
        return self.result[key]

    def __str__(self):
        return str(self.result)


class SoapRequestor(object):
    def __init__(self, soap_client):
        self.soap_client = soap_client
        self.logger = logging.getLogger(
            "tbk.soap.requestor.{}".format(self.__class__.__name__)
        )

    def get_enum_value(self, enum_name, value):
        try:
            return self.soap_client.get_enum_value(enum_name, value)
        except SoapClientException:
            self.logger.error("Cannot get `%s` from enum `%s`", value, enum_name)
            raise

    def create_object(self, type_name, *args, **kwargs):
        try:
            return self.soap_client.create_object(type_name, *args, **kwargs)
        except SoapClientException:
            self.logger.error("Cannot create instance of type `%s`", type_name)
            raise

    def request(self, method_name, *args, **kwargs):
        try:
            timeout = kwargs.pop("timeout", None)
            request = SoapRequest(method_name=method_name, args=args, kwargs=kwargs)
            self.logger.info("Starting request to method `%s`", method_name)
            self.logger.debug(request)
            result, envelope_sent, envelope_received = self.soap_client.request(
                request, timeout=timeout
            )
        except SoapServerException:
            self.logger.exception("SOAP server exception on method `%s`", method_name)
            raise
        except Exception:
            self.logger.exception(
                "SOAP request method `%s` failed with unexpected exception", method_name
            )
            raise
        else:
            response = SoapResponse(
                result=result,
                request=request,
                envelope_sent=envelope_sent,
                envelope_received=envelope_received,
            )
            self.logger.info("Successful request to method `%s`", method_name)
            self.logger.debug(response)
            return response
