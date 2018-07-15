
import logging

from .exceptions import SoapClientException


class SoapRequestor(object):

    def __init__(self, soap_client):
        self.soap_client = soap_client
        self.logger = logging.getLogger('tbk.soap.requestor.{}'.format(self.__class__.__name__))

    def get_enum_value(self, enum_name, value):
        try:
            return self.soap_client.get_enum_value(enum_name, value)
        except SoapClientException:
            self.logger.error("Cannot get `%s` from enum `%s`", value, enum_name)
            raise

    def create_object(self, type_name, **kwargs):
        try:
            return self.soap_client.create_object(type_name, **kwargs)
        except SoapClientException:
            self.logger.error("Cannot create instance of type `%s`", type_name)
            raise

    def request(self, method_name, method_input):
        try:
            self.logger.info("Starting request to method `%s`", method_name)
            self.logger.debug(method_input)
            result = self.soap_client.request(method_name, method_input)
        except SoapClientException:
            self.logger.exception("SOAP client exception on method `%s`", method_name)
            raise
        except Exception:
            self.logger.exception(
                "SOAP request method `%s` failed with unexpected exception", method_name)
            raise
        else:
            self.logger.info("Successful request to method `%s`", method_name)
            self.logger.debug(result)
            return result
