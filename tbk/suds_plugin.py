# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .wsse import sign_envelope_data, verify_envelope_data

import xmlsec
from suds.plugin import MessagePlugin


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
