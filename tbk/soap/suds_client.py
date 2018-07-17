
import xmlsec
import suds.client
import suds.plugin
import suds.transport.https
import suds.plugin
import suds.wsse

from .wsse import sign_envelope_data, verify_envelope_data

from .exceptions import (EnumValueDoesNotExist, SoapServerException, TypeDoesNotExist,
                         MethodDoesNotExist, InvalidSignatureResponse)

from .requestor import SoapClient
from .utils import parse_tbk_error_message, load_key_from_data


class SudsSoapClient(SoapClient):

    def __init__(self, wsdl_url, key_data, cert_data, tbk_cert_data):
        super(SudsSoapClient, self).__init__(wsdl_url, key_data, cert_data, tbk_cert_data)
        self.transport = suds.transport.https.HttpTransport()
        wsse = suds.wsse.Security()
        wsse_plugin = SudsWssePlugin.init_from_data(
            key_data=key_data,
            cert_data=cert_data,
            tbk_cert_data=tbk_cert_data,
        )
        self.history = SudsHistoryPlugin()
        self.client = suds.client.Client(
            url=wsdl_url,
            transport=self.transport,
            wsse=wsse,
            plugins=[wsse_plugin, self.history],
        )

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

    def request(self, method_name, *args, **kwargs):
        try:
            method = self.get_method(method_name)
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
        return self.history.last_sent

    def get_last_received_envelope(self):
        return self.history.last_received


class SudsHistoryPlugin(suds.plugin.MessagePlugin):

    def __init__(self):
        self.last_sent = None
        self.last_received = None

    def sending(self, context):
        """Sign outgoing message envelope."""
        self.last_sent = context.envelope

    def received(self, context):
        """Verify signature of incoming reply envelope."""
        self.last_received = context.reply


class SudsWssePlugin(suds.plugin.MessagePlugin):
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
        if not context.reply or not verify_envelope_data(context.reply, self.tbk_cert):
            context.reply = None
