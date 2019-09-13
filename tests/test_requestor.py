import pytest

from tbk.soap import SoapRequest, SoapRequestor, SoapResponse, create_soap_requestor
from tbk.soap.exceptions import (
    SoapClientException,
    SoapRequestException,
    SoapServerException,
)


@pytest.mark.parametrize(
    ("enum_type", "value"),
    (("EnumType", "value"), ("AnIntValue", 1), ("BooleanValue", True)),
)
def test_get_enum_value(soap_client, enum_type, value):
    requestor = SoapRequestor(soap_client)

    result = requestor.get_enum_value(enum_type, value)

    assert soap_client.get_enum_value.return_value is result


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
def test_request(mock, soap_client, method_name, args, kwargs):
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

    assert expected_response.result == response.result
    assert expected_response.envelope_sent == response.envelope_sent
    assert expected_response.envelope_received == response.envelope_received
    assert expected_response.request.method_name == response.request.method_name
    assert expected_response.request.args == response.request.args
    assert expected_response.request.kwargs == response.request.kwargs


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs", "error", "code"),
    (
        ("method1", ("arg", True, 1), {}, "error1", 1),
        ("method2", (), {"a": "arg", "b": True, "c": 1}, "error2", 2),
        ("methodThree", ("arg1", True), {"a": "kwarg", "c": 1}, "error3", 3),
    ),
)
def test_request_server_exception(
    mock, soap_client, method_name, args, kwargs, error, code
):
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
def test_request_exception(mock, soap_client, method_name, args, kwargs):
    error = Exception()
    request = mock.Mock(spec=SoapRequest)
    soap_client.request.side_effect = SoapRequestException(error, request)
    requestor = SoapRequestor(soap_client)

    with pytest.raises(SoapRequestException) as exc_info:
        requestor.request(method_name, *args, **kwargs)

    assert exc_info.type is SoapRequestException
    assert exc_info.value.error is error
    assert exc_info.value.request is request


@pytest.mark.parametrize(
    ("result"), ({"a": 1, "b": "b", "key": True}, {"a": 1, "b": b"abc"})
)
def test_response_object_getitem(mock, result):
    request = mock.Mock(spec=SoapRequest)
    response = SoapResponse(
        request=request, result=result, envelope_received=None, envelope_sent=None
    )
    for key, value in result.items():
        assert response[key] is value


def test_create_default_soap_requestor(mock, default_commerce):
    wsdl_url = mock.MagicMock(spec=str)
    with mock.patch("tbk.soap.default_client_class", spec=type) as client_class:
        requestor = create_soap_requestor(wsdl_url, default_commerce)
        client_class.assert_called_once_with(
            wsdl_url=wsdl_url,
            key_data=default_commerce.key_data,
            cert_data=default_commerce.cert_data,
            tbk_cert_data=default_commerce.tbk_cert_data,
            password=default_commerce.key_password,
        )
        assert isinstance(requestor, SoapRequestor)
        assert client_class.return_value is requestor.soap_client


def test_create_soap_requestor_with_custom_class(mock, default_commerce):
    client_class = mock.MagicMock(spec=type)
    wsdl_url = mock.MagicMock(spec=str)
    requestor = create_soap_requestor(
        wsdl_url, default_commerce, client_class=client_class
    )
    client_class.assert_called_once_with(
        wsdl_url=wsdl_url,
        key_data=default_commerce.key_data,
        cert_data=default_commerce.cert_data,
        tbk_cert_data=default_commerce.tbk_cert_data,
        password=default_commerce.key_password,
    )
    assert isinstance(requestor, SoapRequestor)
    assert client_class.return_value is requestor.soap_client
