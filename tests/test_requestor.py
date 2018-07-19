
import unittest

from tbk.soap.exceptions import SoapClientException, SoapServerException
from tbk.soap.requestor import SoapRequestor, SoapClient, SoapRequest, SoapResponse

from .utils import mock


class SoapRequestorTest(unittest.TestCase):

    def setUp(self):
        self.soap_client = mock.MagicMock(spec=SoapClient)

    def test_get_enum_value(self):
        get_enum_value = self.soap_client.get_enum_value

        requestor = SoapRequestor(self.soap_client)
        result = requestor.get_enum_value('EnumType', 'value')

        get_enum_value.assert_called_once_with(
            'EnumType',
            'value')
        self.assertEqual(get_enum_value.return_value, result)

    def test_get_enum_value_exception(self):
        get_enum_value = self.soap_client.get_enum_value
        get_enum_value.side_effect = SoapClientException

        requestor = SoapRequestor(self.soap_client)

        self.assertRaises(
            SoapClientException, requestor.get_enum_value, 'EnumType', 'value')

    def test_create_object(self):
        create_object = self.soap_client.create_object

        requestor = SoapRequestor(self.soap_client)
        result = requestor.create_object('TypeName', 'arg', kw='kw')

        create_object.assert_called_once_with(
            'TypeName',
            'arg',
            kw='kw')
        self.assertEqual(create_object.return_value, result)

    def test_create_object_exception(self):
        create_object = self.soap_client.create_object
        create_object.side_effect = SoapClientException

        requestor = SoapRequestor(self.soap_client)

        self.assertRaises(
            SoapClientException, requestor.create_object, 'TypeName', 'arg', kw='kw')

    def test_request(self):
        request = self.soap_client.request
        mocked_result = mock.Mock()
        mocked_envelope_sent = mock.Mock()
        mocked_envelope_received = mock.Mock()
        request.return_value = (mocked_result, mocked_envelope_sent, mocked_envelope_received)
        args = ('arg')
        kwargs = {'kw': 'kw'}
        expected_request = SoapRequest(
            method_name='methodName',
            args=args,
            kwargs=kwargs)
        expected_response = SoapResponse(
            request=expected_request,
            result=mocked_result,
            envelope_sent=mocked_envelope_sent,
            envelope_received=mocked_envelope_received)

        requestor = SoapRequestor(self.soap_client)
        response = requestor.request('methodName', *args, **kwargs)

        self.assertEqual(expected_response, response)

    def test_request_exception(self):
        request = self.soap_client.request
        request.side_effect = SoapServerException(123, 'code')

        requestor = SoapRequestor(self.soap_client)
        self.assertRaises(SoapServerException, requestor.request, 'methodName', 'arg', kw='kw')
