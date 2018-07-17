
import re
import logging

import abc
try:
    AbstractBaseClass = abc.ABC
except AttributeError:
    AbstractBaseClass = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

import suds.client
import suds.plugin
import suds.transport.https
import suds.wsse

from .exceptions import (EnumValueDoesNotExist, SoapServerException, TypeDoesNotExist,
                         MethodDoesNotExist, InvalidSignatureResponse, SoapClientException)
from .wsse_suds_plugin import SudsWssePlugin


def create_soap_client(wsdl_url, key_data, cert_data, tbk_cert_data, client_class=None):
    client_class = client_class or DefaultSoapClient
    return client_class(wsdl_url, key_data, cert_data, tbk_cert_data)


class SoapClient(AbstractBaseClass):

    @abc.abstractmethod
    def get_enum_value(self, enum_name, value):
        pass

    @abc.abstractmethod
    def create_object(self, type_name, **kwargs):
        pass

    @abc.abstractmethod
    def request(self, method_name, method_input):
        pass


class SudsRegisterRequestPlugin(suds.plugin.MessagePlugin):
    def __init__(self):
        self.last_sent = None
        self.last_received = None

    def sending(self, context):
        """Sign outgoing message envelope."""
        self.last_sent = context.envelope

    def received(self, context):
        """Verify signature of incoming reply envelope."""
        self.last_received = context.reply


class SudsSoapClient(SoapClient):

    def __init__(self, wsdl_url, key_data, cert_data, tbk_cert_data):
        self.client = create_suds_client(wsdl_url, key_data, cert_data, tbk_cert_data)
        self.logger = logging.getLogger('tbk.soap.client.SudsSoapClient')

    def get_instance(self, type_name):
        try:
            return self.client.factory.create(type_name)
        except suds.TypeNotFound:
            raise TypeDoesNotExist(type_name)

    def get_enum_value(self, enum_name, value):
        try:
            return getattr(self.get_instance(enum_name), value)
        except AttributeError:
            raise EnumValueDoesNotExist(enum_name, value)

    def create_object(self, type_name, **arguments):
        obj = self.get_instance(type_name)
        for key, argument in arguments.items():
            setattr(obj, key, argument)
        return obj

    def get_method(self, method_name):
        try:
            method = getattr(self.client.service, method_name)
        except suds.MethodNotFound:
            raise MethodDoesNotExist(method_name)
        else:
            return method

    def request(self, request):
        method = self.get_method(request.method_name)
        return self.do_request(method, *request.args, **request.kwargs)

    def do_request(self, method, *args, **kwargs):
        try:
            result = method(*args, **kwargs)
        except TypeError:  # hack for invalid signature
            raise InvalidSignatureResponse()
        except suds.WebFault as webfault:
            self.logger.exception("Suds WebFault")
            error, code = parse_tbk_error_message(webfault.fault.faultstring)
            raise SoapServerException(error, code)
        else:
            sent_envelope = self.get_last_sent_envelope()
            received_envelope = self.get_last_received_envelope()
            return result, sent_envelope, received_envelope

    def get_last_sent_envelope(self):
        plugin = self.get_register_plugin()
        return plugin.last_sent

    def get_last_received_envelope(self):
        plugin = self.get_register_plugin()
        return plugin.last_received

    def get_register_plugin(self):
        for plugin in self.client.options.plugins:
            if isinstance(plugin, SudsRegisterRequestPlugin):
                return plugin
        self.logger.warning("Suds client must use a SudsRegisterRequestPlugin")
        raise SoapClientException("Cannot retrieve envelopes content")


DefaultSoapClient = SudsSoapClient


def create_suds_client(wsdl_url, key_data, cert_data, tbk_cert_data):
    transport = suds.transport.https.HttpTransport()
    wsse = suds.wsse.Security()
    wsse_plugin = SudsWssePlugin.init_from_data(
        key_data=key_data,
        cert_data=cert_data,
        tbk_cert_data=tbk_cert_data,
    )
    register_request_plugin = SudsRegisterRequestPlugin()
    return suds.client.Client(
        url=wsdl_url,
        transport=transport,
        wsse=wsse,
        plugins=[wsse_plugin, register_request_plugin],
    )


def parse_tbk_error_message(raw_message):
    message_match = re.search(r'<!--(.+?)-->', raw_message)
    if message_match:
        message = message_match.group(1).strip()
        match = re.search(r'(.+?)\((\d+?)\)', message)
        if match:
            error = match.group(1)
            code = int(match.group(2))
            return error, code
        return message, -1
    return raw_message, -1
