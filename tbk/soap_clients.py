# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import logging

from .exceptions import WebpayServiceException

try:
    import suds
except ImportError:
    suds = None
else:
    import suds.client
    import suds.plugin
    import suds.transport.https
    import suds.wsse
    from .wsse_suds_plugin import SudsWssePlugin


class SoapClient(object):

    @classmethod
    def create_default_client(cls, wsdl_url, key_data, cert_data, tbk_cert_data):
        if suds:
            return SudsSoapClient(wsdl_url, key_data, cert_data, tbk_cert_data)
        else:
            raise NotImplementedError()

    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger('tbk.soap.{}'.format(self.__class__.__name__))

    def create_input(self, type_name, instance_arguments):
        input_instance = self.create_instance(type_name)
        if isinstance(instance_arguments, list):
            instance_arguments = self.create_input_list(instance_arguments)
        self.set_instance_attributes(input_instance, instance_arguments)
        return input_instance

    def create_input_list(self, elements):
        return [
            self.create_input(type_name, arguments)
            for type_name, arguments in elements
        ]

    def set_instance_attributes(self, input_instance, instance_arguments):
        for argument_name, arguments in instance_arguments.items():
            if isinstance(arguments, list):
                arguments = self.create_input_list(arguments)
            if isinstance(arguments, tuple):
                arguments = self.create_input(*arguments)
            setattr(input_instance, argument_name, arguments)

    def request(self, method_name, method_input):
        method = self.get_method(method_name)
        try:
            self.logger.info("Starting request to method `%s`", method_name)
            self.logger.debug(method_input)
            result = self.do_request(method, method_input)
            self.logger.info("Successful request to method `%s`", method_name)
            self.logger.debug(result)
            return result
        except Exception:
            self.logger.exception("SOAP request method `%s` failed", method_name)
            raise

    def create_instance(self, type_name):
        raise NotImplementedError

    def get_method(self, method_name):
        raise NotImplementedError

    def do_request(self, method, method_input):
        raise NotImplementedError


class SudsSoapClient(SoapClient):

    @staticmethod
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

    def __init__(self, wsdl_url, key_data, cert_data, tbk_cert_data):
        client = self.create_suds_client(wsdl_url, key_data, cert_data, tbk_cert_data)
        super(SudsSoapClient, self).__init__(client=client)

    def get_method(self, method_name):
        method = getattr(self.client.service, method_name)
        print method
        return method

    def create_instance(self, type_name):
        return self.client.factory.create(type_name)

    def do_request(self, method, method_input):
        try:
            return method(method_input)
        except suds.WebFault as webfault:
            self.logger.error("Suds WebFault", exc_info=True)
            error, code = parse_error_message(webfault.args[0])
            raise WebpayServiceException(error, code)


def parse_error_message(raw_message):
    message_match = re.search(r'\'<!--(.+?)-->\'', raw_message)
    if message_match:
        message = message_match.group(1).strip()
        match = re.search(r'(.+?)\((\d+?)\)', message)
        if match:
            error = match.group(1)
            code = int(match.group(2))
            return error, code
        return message, -1
    return raw_message, -1
