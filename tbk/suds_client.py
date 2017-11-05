# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from .exceptions import WebpayServiceException
from .service import SoapClient
from .wsse import sign_envelope_data, verify_envelope_data

import xmlsec

from suds import WebFault
from suds.client import Client
from suds.wsse import Security
from suds.transport.https import HttpTransport
from suds.plugin import MessagePlugin


class SudsSoapClient(SoapClient):

    def __init__(self, wsdl_url, key_data, cert_data, tbk_cert_data):
        client = create_suds_client(wsdl_url, key_data, cert_data, tbk_cert_data)
        super(SudsSoapClient, self).__init__(client=client)

    def get_method(self, method_name):
        return getattr(self.client.service, method_name)

    def create_instance(self, type_name):
        return self.client.factory.create(type_name)

    def do_request(self, method, method_input):
        try:
            return method(method_input)
        except WebFault as webfault:
            error, code = parse_suds_webfault(webfault.args[0])
            raise WebpayServiceException(error, code)


def create_suds_client(wsdl_url, key_data, cert_data, tbk_cert_data):
    transport = HttpTransport()
    wsse = Security()
    wsse_plugin = WssePlugin.init_from_data(
        key_data=key_data,
        cert_data=cert_data,
        tbk_cert_data=tbk_cert_data,
    )
    return Client(
        url=wsdl_url,
        transport=transport,
        wsse=wsse,
        plugins=[wsse_plugin],
    )


def parse_suds_webfault(raw_message):
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


class WssePlugin(MessagePlugin):
    """Suds message plugin that performs WS-Security(ish) signing and encryption.

    Signs outgoing messages (the soap:Body, which must be present); verifies signature on
    incoming messages.

    Uses X509 certificates for signing. Requires our cert
    and its private key, and their cert (all as file paths).

    Expects to sign an outgoing SOAP message looking something like
    this (xmlns attributes omitted for readability):

    <soap:Envelope>
      <soap:Header>
        <wsse:Security mustUnderstand="true">
        </wsse:Security>
      </soap:Header>
      <soap:Body>
        ...
      </soap:Body>
    </soap:Envelope>

    """
    def __init__(self, key, tbk_cert):
        self.key = key
        self.tbk_cert = tbk_cert

    @classmethod
    def init_from_data(cls, key_data, cert_data, tbk_cert_data, password=None):
        key = load_key_from_data(key_data, cert_data, password)
        tbk_cert = load_key_from_data(tbk_cert_data, key_format=xmlsec.KeyFormat.CERT_PEM)
        return cls(key, tbk_cert)

    def sending(self, context):
        """Sign outgoing message envelope."""
        context.envelope = sign_envelope_data(context.envelope, self.key)

    def received(self, context):
        """Verify signature of incoming reply envelope."""
        if context.reply:
            verify_envelope_data(context.reply, self.tbk_cert)


def load_key_from_data(key_data, cert_data=None, password=None, key_format=xmlsec.KeyFormat.PEM):
    key = xmlsec.Key.from_memory(key_data, key_format, password)
    if cert_data:
        key.load_cert_from_memory(cert_data, key_format)
    return key
