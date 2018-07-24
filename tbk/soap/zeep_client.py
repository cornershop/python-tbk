
import zeep
import zeep.plugins
import zeep.helpers
import zeep.exceptions

from .soap_client import SoapClient
from .wsse import sign_envelope, verify_envelope
from .exceptions import (InvalidSignatureResponse, SoapServerException, MethodDoesNotExist,
                         TypeDoesNotExist)
from .utils import load_key_from_data, parse_tbk_error_message, xml_to_string


class ZeepSoapClient(SoapClient):

    def __init__(self, wsdl_url, key_data, cert_data, tbk_cert_data, password=None):
        super(ZeepSoapClient, self).__init__(wsdl_url, key_data, cert_data, tbk_cert_data)
        wsse = ZeepWsseSignature.init_from_data(key_data, cert_data, tbk_cert_data, password=password)
        self.history = zeep.plugins.HistoryPlugin()
        self.client = zeep.Client(wsdl_url, wsse=wsse, plugins=[self.history])

    def create_object(self, type_name, *args, **kwargs):
        try:
            object_type = self.client.get_type('ns0:{}'.format(type_name))
        except zeep.exceptions.LookupError:
            raise TypeDoesNotExist(type_name)
        else:
            return object_type(*args, **kwargs)

    def get_enum_value(self, enum_name, value):
        return self.create_object(enum_name, value)

    def request(self, method_name, *args, **kwargs):
        try:
            method = self.get_method(method_name)
            result = method(*args, **kwargs)
        except zeep.exceptions.Fault as fault:
            self.logger.exception("Fault")
            error, code = parse_tbk_error_message(fault.message)
            raise SoapServerException(error, code)
        else:
            serialized = zeep.helpers.serialize_object(result)
            last_sent = self.get_last_sent_envelope()
            last_received = self.get_last_received_envelope()
            return serialized, last_sent, last_received

    def get_method(self, method_name):
        try:
            return getattr(self.client.service, method_name)
        except AttributeError:
            raise MethodDoesNotExist(method_name)

    def get_last_sent_envelope(self):
        return xml_to_string(self.history.last_sent['envelope'])

    def get_last_received_envelope(self):
        return xml_to_string(self.history.last_received['envelope'])


class ZeepWsseSignature(object):

    def __init__(self, key, tbk_cert):
        self.key = key
        self.tbk_cert = tbk_cert

    @classmethod
    def init_from_data(cls, key_data, cert_data, tbk_cert_data, password=None):
        key = load_key_from_data(key_data, cert_data, password)
        tbk_cert = load_key_from_data(tbk_cert_data, key_format='CERT_PEM')
        return cls(key, tbk_cert)

    def apply(self, envelope, headers):
        sign_envelope(envelope, self.key)
        return envelope, headers

    def verify(self, envelope):
        if not verify_envelope(envelope, self.tbk_cert):
            raise InvalidSignatureResponse()
        return envelope
