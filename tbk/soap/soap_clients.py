
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
                         MethodDoesNotExist, InvalidSignatureResponse)
from .wsse_suds_plugin import SudsWssePlugin


def create_default_client(wsdl_url, key_data, cert_data, tbk_cert_data):
    return SudsSoapClient(wsdl_url, key_data, cert_data, tbk_cert_data)


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

    def request(self, method_name, method_input):
        method = self.get_method(method_name)
        return self.do_request(method, method_input)

    def do_request(self, method, method_input):
        try:
            result = method(method_input)
        except TypeError:  # hack on invalid signature
            raise InvalidSignatureResponse()
        except suds.WebFault as webfault:
            self.logger.exception("Suds WebFault")
            error, code = parse_tbk_error_message(webfault.fault.faultstring)
            raise SoapServerException(error, code)
        else:
            return result


def create_suds_client(wsdl_url, key_data, cert_data, tbk_cert_data):
    transport = suds.transport.https.HttpTransport()
    wsse = suds.wsse.Security()
    wsse_plugin = SudsWssePlugin.init_from_data(
        key_data=key_data,
        cert_data=cert_data,
        tbk_cert_data=tbk_cert_data,
    )
    return suds.client.Client(
        url=wsdl_url,
        transport=transport,
        wsse=wsse,
        plugins=[wsse_plugin],
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
