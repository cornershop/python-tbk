# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import re

from .exceptions import WebpayServiceException


class WebpayService(object):
    INTEGRACION = 'INTEGRACION'
    CERTIFICACION = 'CERTIFICACION'
    PRODUCCION = 'PRODUCCION'

    def __init__(self, commerce, soap_client):
        self.commerce = commerce
        self.soap_client = soap_client
        self.logger = logging.getLogger('tbk.service.{}'.format(self.__class__.__name__))

    @classmethod
    def init_for_commerce(cls, commerce):
        soap_client = SudsSoapClient(
            cls.get_wsdl_url_for_environent(commerce.environment),
            commerce.key_data,
            commerce.cert_data,
            commerce.tbk_cert_data
        )
        return cls(commerce, soap_client)

    @classmethod
    def get_wsdl_url_for_environent(cls, environment):
        try:
            return getattr(cls, 'WSDL_{}'.format(environment))
        except AttributeError:
            raise ValueError("Invalid environment {}".format(environment))


class SudsSoapClient(object):
    def __init__(self, wsdl_url, key_data, cert_data, webpay_cert_data):
        self.client = self.create_client(wsdl_url, key_data, cert_data, webpay_cert_data)
        self.logger = logging.getLogger('tbk.service.soap.{}'.format(self.__class__.__name__))

    @classmethod
    def create_client(cls, wsdl_url, key_data, cert_data, tbk_cert_data):
        from .suds_plugin import WssePlugin

        from suds.client import Client
        from suds.wsse import Security
        from suds.transport.https import HttpTransport

        transport = HttpTransport()
        wsse = Security()
        wsse_plugin = WssePlugin.init_from_data(
            key_data=key_data,
            cert_data=cert_data,
            tbk_cert_data=tbk_cert_data,
        )

        return Client(
            wsdl_url,
            transport=transport,
            wsse=wsse,
            plugins=[wsse_plugin],
        )

    def do_request(self, method_name, method_input):
        from suds import WebFault
        try:
            method = getattr(self.service, method_name)
            self.logger.info("Starting request to method `{}`.".format(method_name))
            self.logger.debug(method_input)
            result = method(method_input)
            self.logger.info("Successful request to method `{}`.".format(method_name))
            self.logger.debug(result)
            return result
        except WebFault as e:
            self.logger.warn("Soap request method `{}` failed.".format(method_name), exc_info=True)
            error, code = _parse_suds_webfault(e)
            raise WebpayServiceException(error, code)

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

    def create_instance(self, type_name):
        return self.factory.create(type_name)

    @property
    def factory(self):
        return self.client.factory

    @property
    def service(self):
        return self.client.service


def _parse_suds_webfault(webfault):
    raw_message = webfault.args[0]
    message = re.search(r'\'<!--(.+?)-->\'', raw_message).group(1).strip()
    match = re.search(r'(.+?)\((\d+?)\)', message)
    error = match.group(1)
    code = int(match.group(2))
    return error, code
