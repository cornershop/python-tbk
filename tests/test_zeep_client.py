
import unittest
import copy

import requests_mock
import xmlsec
import zeep.exceptions

from tbk.soap import SoapClient
from tbk.soap.zeep_client import ZeepSoapClient, ZeepWsseSignature
from tbk.soap.exceptions import InvalidSignatureResponse, TypeDoesNotExist, SoapServerException
from tbk.soap.wsse import sign_envelope, verify_envelope
from tbk.soap.utils import load_key_from_data

from .utils import mock, get_fixture_url, get_fixture_data, assert_equal_xml, get_xml_envelope


@requests_mock.Mocker()
class ZeepClientTest(unittest.TestCase):

    def setUp(self):
        self.wsdl_url = get_fixture_url('WsWebpayService.wsdl')
        self.key_data = get_fixture_data('597020000547.key')

        self.cert_data = get_fixture_data('597020000547.crt')
        self.tbk_cert_data = get_fixture_data('tbk.pem')

    def test_init(self, requests):
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)
        self.assertIsInstance(zeep_client, SoapClient)

    def test_get_enum_value(self, requests):
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)

        for value in ('TR_NORMAL_WS', 'TR_NORMAL_WS_WPM', 'TR_MALL_WS'):
            enum_value = zeep_client.get_enum_value('wsTransactionType', value)
            self.assertEqual(value, enum_value)

    def test_get_enum_value_type_error(self, requests):
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)

        self.assertRaises(TypeDoesNotExist, zeep_client.get_enum_value, 'does_not_exist', 'TR_NORMAL_WS')

    def test_create_object(self, requests):
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)
        client = zeep_client.client
        cardDetail = client.get_type('ns0:cardDetail')
        expected = cardDetail(cardNumber='1234', cardExpirationDate='12/20')

        new_object = zeep_client.create_object('cardDetail', cardNumber='1234', cardExpirationDate='12/20')

        self.assertEqual(expected, new_object)

    def test_create_object_type_error(self, requests):
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)

        self.assertRaises(
            TypeDoesNotExist,
            zeep_client.create_object, 'does_not_exist', cardNumber='1234', cardExpirationDate='12/20')

    def test_create_object_arguments_error(self, requests):
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)

        self.assertRaises(TypeError, zeep_client.create_object, 'cardDetail', does_not_exist='1234')

    def test_request_server_exception(self, requests):
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)
        method = mock.Mock()
        method_name = 'methodName'
        setattr(zeep_client.client.service, method_name, method)
        message = '<!-- Invalid amount(304) -->'
        code = 'soap:Server'
        method.side_effect = zeep.exceptions.Fault(message, code)

        with self.assertRaises(SoapServerException) as context:
            zeep_client.request(method_name)
        self.assertEqual(context.exception.error, 'Invalid amount')
        self.assertEqual(context.exception.code, 304)

    def test_request_verified(self, requests):
        expected_response = get_fixture_data('acknowledgeTransaction.response.xml').encode('utf-8')
        requests.register_uri(
            'POST',
            'https://webpay3g.transbank.cl:443/WSWebpayTransaction/cxf/WSWebpayService',
            content=expected_response)
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)

        with mock.patch('tbk.soap.zeep_client.verify_envelope', return_value=True):
            zeep_client.request('acknowledgeTransaction', 'token')

    @mock.patch('tbk.soap.zeep_client.verify_envelope', return_value=True)
    def test_request_with_signature(self, requests, __):
        expected_response = get_fixture_data('acknowledgeTransaction.response.xml').encode('utf-8')
        requests.register_uri(
            'POST',
            'https://webpay3g.transbank.cl:443/WSWebpayTransaction/cxf/WSWebpayService',
            content=expected_response)
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)

        with mock.patch('tbk.soap.zeep_client.sign_envelope', return_value=None) as signer:
            zeep_client.request('acknowledgeTransaction', 'token')
            self.assertEqual(1, signer.call_count)

    def test_request_not_verified(self, requests):
        expected_response = get_fixture_data('acknowledgeTransaction.response.xml').encode('utf-8')
        requests.register_uri(
            'POST',
            'https://webpay3g.transbank.cl:443/WSWebpayTransaction/cxf/WSWebpayService',
            content=expected_response)
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)

        with mock.patch('tbk.soap.zeep_client.verify_envelope', return_value=False):
            self.assertRaises(InvalidSignatureResponse, zeep_client.request, 'acknowledgeTransaction', 'token')

    @mock.patch('tbk.soap.zeep_client.verify_envelope', return_value=True)
    def test_request_sent_received_data(self, requests, __):
        zeep_client = ZeepSoapClient(self.wsdl_url, self.key_data, self.cert_data, self.tbk_cert_data)
        expected_response = get_fixture_data('acknowledgeTransaction.response.xml').encode('utf-8')
        requests.register_uri(
            'POST',
            'https://webpay3g.transbank.cl:443/WSWebpayTransaction/cxf/WSWebpayService',
            content=expected_response)

        acknowledgeTransaction = zeep_client.client.service.acknowledgeTransaction

        with mock.patch.object(zeep_client.client.service, 'acknowledgeTransaction') as method:
            method.side_effect = acknowledgeTransaction
            result, last_sent, last_received = zeep_client.request('acknowledgeTransaction', 'token')
            method.assert_called_once_with('token')
        assert_equal_xml(expected_response, last_received)
        assert_equal_xml(requests.request_history[0].text.encode('utf-8'), last_sent)


class ZeepWssePluginTest(unittest.TestCase):

    def setUp(self):
        signer_key_data = get_fixture_data('597020000547.key')
        signer_cert_data = get_fixture_data('597020000547.crt')
        tbk_cert_data = get_fixture_data('tbk.pem')
        self.tbk_cert = load_key_from_data(tbk_cert_data, key_format=xmlsec.KeyFormat.CERT_PEM)
        self.signer_key = load_key_from_data(signer_key_data, signer_cert_data)
        self.signer_cert = load_key_from_data(signer_cert_data, key_format=xmlsec.KeyFormat.CERT_PEM)
        self.envelope = get_xml_envelope('bare.acknowledgeTransaction.response.xml')
        self.signed_envelope = copy.deepcopy(self.envelope)
        sign_envelope(self.signed_envelope, self.signer_key)

    def test_sign_request(self):
        plugin = ZeepWsseSignature(self.signer_key, None)
        headers = mock.Mock()

        result_envelope, result_headers = plugin.apply(self.envelope, headers)

        self.assertEqual(headers, result_headers)
        self.assertTrue(verify_envelope(result_envelope, self.signer_cert))

    def test_verify_response(self):
        plugin = ZeepWsseSignature(None, self.signer_cert)

        plugin.verify(self.signed_envelope)

    def test_do_not_verify_response(self):
        plugin = ZeepWsseSignature(None, self.tbk_cert)

        self.assertRaises(InvalidSignatureResponse, plugin.verify, self.signed_envelope)

    def test_do_not_verify_unsigned_response(self):
        plugin = ZeepWsseSignature(None, self.tbk_cert)

        self.assertRaises(InvalidSignatureResponse, plugin.verify, self.envelope)
