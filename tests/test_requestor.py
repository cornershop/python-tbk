import unittest

import pytest

from tbk.soap import SoapRequestor, SoapRequest, SoapResponse, create_soap_requestor
from tbk.soap.exceptions import (
    SoapClientException,
    SoapServerException,
    SoapRequestException,
)
from tbk.soap.soap_client import SoapClient

from .utils import mock


@pytest.fixture
def soap_client():
    return mock.MagicMock(spec=SoapClient)


def assert_responses(first, second, msg=None):
    assert first.result == second.result, msg
    assert first.envelope_sent == second.envelope_sent, msg
    assert first.envelope_received == second.envelope_received, msg
    assert first.request.method_name == second.request.method_name, msg
    assert first.request.args == second.request.args, msg
    assert first.request.kwargs == second.request.kwargs, msg


@pytest.mark.parametrize(
    ("enum_type", "value"),
    (("EnumType", "value"), ("AnIntValue", 1), ("BooleanValue", True)),
)
def test_get_enum_value(soap_client, enum_type, value):
    requestor = SoapRequestor(soap_client)

    result = requestor.get_enum_value(enum_type, value)

    assert soap_client.get_enum_value.return_value == result


@pytest.mark.parametrize(
    ("enum_type", "value"),
    (("EnumType", "value"), ("AnIntValue", 1), ("BooleanValue", True)),
)
def test_get_enum_value_exception(soap_client, enum_type, value):
    soap_client.get_enum_value.side_effect = SoapClientException
    requestor = SoapRequestor(soap_client)

    with pytest.raises(SoapClientException):
        requestor.get_enum_value(enum_type, value)


@pytest.mark.parametrize(
    ("type_name", "args", "kwargs"),
    (
        ("TypeName", ("arg", True, 1), {}),
        ("AnotherType", (), {"a": "arg", "b": True, "c": 1}),
        ("YetAnotherType", ("arg1", True, 1), {"a": "arg", "b": True, "c": 1}),
    ),
)
def test_create_object(soap_client, type_name, args, kwargs):
    requestor = SoapRequestor(soap_client)
    result = requestor.create_object(type_name, *args, **kwargs)

    soap_client.create_object.assert_called_once_with(type_name, *args, **kwargs)
    assert soap_client.create_object.return_value == result


@pytest.mark.parametrize(
    ("type_name", "args", "kwargs"),
    (
        ("TypeName", ("arg", True, 1), {}),
        ("AnotherType", (), {"a": "arg", "b": True, "c": 1}),
        ("YetAnotherType", ("arg1", True, 1), {"a": "arg", "b": True, "c": 1}),
    ),
)
def test_create_object_exception(soap_client, type_name, args, kwargs):
    soap_client.create_object.side_effect = SoapClientException
    requestor = SoapRequestor(soap_client)

    with pytest.raises(SoapClientException):
        requestor.create_object(type_name, *args, **kwargs)


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs"),
    (
        ("method1", ("arg", True, 1), {}),
        ("method2", (), {"a": "arg", "b": True, "c": 1}),
        ("methodThree", ("arg1", True, 1), {"a": "arg", "b": True, "c": 1}),
    ),
)
def test_request(soap_client, method_name, args, kwargs):
    mocked_result = mock.Mock()
    mocked_envelope_sent = mock.Mock()
    mocked_envelope_received = mock.Mock()
    soap_client.request.return_value = (
        mocked_result,
        mocked_envelope_sent,
        mocked_envelope_received,
    )

    expected_request = SoapRequest(method_name=method_name, args=args, kwargs=kwargs)
    expected_response = SoapResponse(
        request=expected_request,
        result=mocked_result,
        envelope_sent=mocked_envelope_sent,
        envelope_received=mocked_envelope_received,
    )
    requestor = SoapRequestor(soap_client)

    response = requestor.request(method_name, *args, **kwargs)

    assert_responses(expected_response, response)


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs", "error", "code"),
    (
        ("method1", ("arg", True, 1), {}, "error1", 1),
        ("method2", (), {"a": "arg", "b": True, "c": 1}, "error2", 2),
        ("methodThree", ("arg1", True), {"a": "kwarg", "c": 1}, "error3", 3),
    ),
)
def test_request_server_exception(soap_client, method_name, args, kwargs, error, code):
    request = mock.Mock(spec=SoapRequest)
    soap_client.request.side_effect = SoapServerException(error, code, request)
    requestor = SoapRequestor(soap_client)

    with pytest.raises(SoapServerException) as exc_info:
        requestor.request(method_name, *args, **kwargs)

    assert exc_info.type is SoapServerException
    assert exc_info.value.error is error
    assert exc_info.value.code is code
    assert exc_info.value.request is request


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs"),
    (
        ("method1", ("arg", True, 1), {}),
        ("method2", (), {"a": "arg", "b": True, "c": 1}),
        ("methodThree", ("arg1", True, 1), {"a": "arg", "b": True, "c": 1}),
    ),
)
def test_request_exception(soap_client, method_name, args, kwargs):
    error = Exception()
    request = mock.Mock(spec=SoapRequest)
    soap_client.request.side_effect = SoapRequestException(error, request)
    requestor = SoapRequestor(soap_client)

    with pytest.raises(SoapRequestException) as exc_info:
        requestor.request(method_name, *args, **kwargs)

    assert exc_info.type is SoapRequestException
    assert exc_info.value.error is error
    assert exc_info.value.request is request


class SoapResponseTest(unittest.TestCase):
    def test_get_item(self):
        request = mock.Mock(spec=SoapRequest)
        key = mock.Mock(spec=str)
        item = mock.Mock()
        result = {key: item}
        response = SoapResponse(
            request=request, result=result, envelope_received=None, envelope_sent=None
        )
        self.assertEqual(item, response[key])


class CreateSOAPRequestorTest(unittest.TestCase):
    def test_create_soap_requestor_with_custom_class(self):
        client_class = mock.MagicMock(spec=type)
        commerce = mock.Mock()
        wsdl_url = mock.MagicMock(spec=str)
        requestor = create_soap_requestor(wsdl_url, commerce, client_class=client_class)
        client_class.assert_called_once_with(
            wsdl_url=wsdl_url,
            key_data=commerce.key_data,
            cert_data=commerce.cert_data,
            tbk_cert_data=commerce.tbk_cert_data,
            password=commerce.key_password,
        )
        self.assertIsInstance(requestor, SoapRequestor)
        self.assertEqual(client_class.return_value, requestor.soap_client)

    def test_create_soap_requestor(self):
        commerce = mock.Mock()
        wsdl_url = mock.MagicMock(spec=str)
        with mock.patch("tbk.soap.default_client_class", spec=type) as client_class:
            requestor = create_soap_requestor(wsdl_url, commerce)
            client_class.assert_called_once_with(
                wsdl_url=wsdl_url,
                key_data=commerce.key_data,
                cert_data=commerce.cert_data,
                tbk_cert_data=commerce.tbk_cert_data,
                password=commerce.key_password,
            )
            self.assertIsInstance(requestor, SoapRequestor)
            self.assertEqual(client_class.return_value, requestor.soap_client)
