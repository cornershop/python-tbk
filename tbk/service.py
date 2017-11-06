# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

try:
    from typing import Text, Union, Any  # noqa
except ImportError:
    pass

from .commerce import Commerce  # noqa


class WebpayService(object):

    def __init__(self, commerce, soap_client):
        # type: (Commerce, SoapClient) -> None
        self.commerce = commerce
        self.soap_client = soap_client
        self.logger = logging.getLogger('tbk.service.{}'.format(self.__class__.__name__))

    @classmethod
    def init_for_commerce(cls, commerce):
        # type: (Commerce) -> WebpayService
        from .suds_client import SudsSoapClient
        soap_client = SudsSoapClient(
            cls.get_wsdl_url_for_environent(commerce.environment),
            commerce.key_data,
            commerce.cert_data,
            commerce.tbk_cert_data
        )
        return cls(commerce, soap_client)

    @classmethod
    def get_wsdl_url_for_environent(cls, environment):
        # type: (Text) -> Text
        try:
            return getattr(cls, 'WSDL_{}'.format(environment))
        except AttributeError:
            raise ValueError("Invalid environment {}".format(environment))


class SoapClient(object):

    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger('tbk.service.soap.{}'.format(self.__class__.__name__))

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
            self.logger.info("Starting request to method `{}`".format(method_name))
            self.logger.debug(method_input)
            result = self.do_request(method, method_input)
            self.logger.info("Successful request to method `{}`".format(method_name))
            self.logger.debug(result)
            return result
        except Exception:
            self.logger.error("Soap request method `{}` failed".format(method_name), exc_info=True)
            raise

    def create_instance(self, type_name):
        raise NotImplementedError()

    def get_method(self, method_name):
        raise NotImplementedError()

    def do_request(self, method, method_input):
        raise NotImplementedError()
