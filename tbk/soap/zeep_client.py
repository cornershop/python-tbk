
import zeep
import zeep.plugins
import zeep.wsse.utils
import zeep.helpers
import xmlsec

from .requestor import SoapClient
from .wsse import sign_envelope, verify_envelope
from .exceptions import (InvalidSignatureResponse, SoapServerException, MethodDoesNotExist,
                         TypeDoesNotExist)
from .utils import load_key_from_data, parse_tbk_error_message


class ZeepSoapClient(SoapClient):

    def __init__(self, wsdl_url, key_data, cert_data, tbk_cert_data):
        super(ZeepSoapClient, self).__init__(wsdl_url, key_data, cert_data, tbk_cert_data)
        wsse = ZeepWsseSignature.init_from_data(key_data, cert_data, tbk_cert_data)
        self.history = zeep.plugins.HistoryPlugin()
        self.client = zeep.Client(wsdl_url, wsse=wsse, plugins=[self.history])

    def create_object(self, type_name, *args, **kwargs):
        try:
            object_type = self.client.get_type('ns0:{}'.format(type_name))
        except LookupError:
            raise TypeDoesNotExist(type_name)
        else:
            return object_type(*args, **kwargs)

    def get_enum_value(self, enum_name, value):
        return self.create_object(enum_name, value)

    def request(self, method_name, *args, **kwargs):
        method = self.get_method(method_name)
        try:
            method = getattr(self.client.service, method_name)
            result = method(*args, **kwargs)
        except zeep.exceptions.Fault as fault:
            self.logger.exception("Suds WebFault")
            error, code = parse_tbk_error_message(fault.message)
            raise SoapServerException(error, code)
        else:
            serialized = zeep.helpers.serialize_object(result)
            return serialized, self.history.last_sent, self.history.last_received

    def get_method(self, method_name):
        try:
            return getattr(self.client.service, method_name)
        except AttributeError:
            raise MethodDoesNotExist(method_name)


class ZeepWsseSignature(object):
    """Sign given SOAP envelope with WSSE sig using given key and cert."""

    def __init__(self, key, tbk_cert):
        self.key = key
        self.tbk_cert = tbk_cert

    @classmethod
    def init_from_data(cls, key_data, cert_data, tbk_cert_data, password=None):
        key = load_key_from_data(key_data, cert_data, password)
        tbk_cert = load_key_from_data(tbk_cert_data, key_format=xmlsec.KeyFormat.CERT_PEM)
        return cls(key, tbk_cert)

    def apply(self, envelope, headers):
        zeep.wsse.utils.get_security_header(envelope)  # create security header
        sign_envelope(envelope, self.key)
        return envelope, headers

    def verify(self, envelope):
        if not verify_envelope(envelope, self.tbk_cert):
            raise InvalidSignatureResponse()
        return envelope
