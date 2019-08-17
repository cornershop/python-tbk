import os

import pytest

import zeep.exceptions
from lxml import etree
from requests import RequestException

from tbk.soap.requestor import SoapRequest
from tbk.soap.soap_client import SoapClient
from tbk.soap.exceptions import (
    InvalidSignatureResponse,
    TypeDoesNotExist,
    SoapServerException,
    MethodDoesNotExist,
    SoapRequestException,
)
from tbk.soap.utils import load_key_from_data
from tbk.soap.wsse import sign_envelope, verify_envelope
from tbk.soap.zeep_client import ZeepSoapClient, ZeepWsseSignature


@pytest.fixture()
def signer_keys(commerce_keys_data):
    key_data, cert_data, tbk_cert_data = commerce_keys_data(597020000547)
    return (
        load_key_from_data(key_data, cert_data),
        load_key_from_data(cert_data, key_format="CERT_PEM"),
        load_key_from_data(tbk_cert_data, key_format="CERT_PEM"),
    )


@pytest.fixture()
def zeep_client(fixtures_dir, commerce_keys_data):
    key_data, cert_data, tbk_cert_data = commerce_keys_data(597020000547)
    wsdl_url = "file://{}".format(os.path.join(fixtures_dir, "WsWebpayService.wsdl"))
    return ZeepSoapClient(wsdl_url, key_data, cert_data, tbk_cert_data)


def test_sign_request(signer_keys, xml_envelope, mock):
    envelope = xml_envelope("bare.acknowledgeTransaction.response.xml")
    signer_key, signer_cert, __ = signer_keys

    plugin = ZeepWsseSignature(signer_key, None)
    headers = mock.Mock()

    result_envelope, result_headers = plugin.apply(envelope, headers)

    assert headers == result_headers
    assert verify_envelope(result_envelope, signer_cert)


def test_verify_response(signer_keys, xml_envelope):
    signer_key, signer_cert, __ = signer_keys
    plugin = ZeepWsseSignature(None, signer_cert)
    envelope = xml_envelope("bare.acknowledgeTransaction.response.xml")
    sign_envelope(envelope, signer_key)

    assert plugin.verify(envelope) is envelope


def test_do_not_verify_response(signer_keys, xml_envelope):
    signer_key, __, another_cert = signer_keys
    plugin = ZeepWsseSignature(None, another_cert)
    envelope = xml_envelope("bare.acknowledgeTransaction.response.xml")
    sign_envelope(envelope, signer_key)

    with pytest.raises(InvalidSignatureResponse) as exc_info:
        plugin.verify(envelope)

    assert exc_info.value.envelope is envelope


def test_do_not_verify_unsigned_response(signer_keys, xml_envelope):
    __, __, another_cert = signer_keys
    plugin = ZeepWsseSignature(None, another_cert)
    envelope = xml_envelope("bare.acknowledgeTransaction.response.xml")

    with pytest.raises(InvalidSignatureResponse) as exc_info:
        plugin.verify(envelope)

    assert exc_info.value.envelope is envelope


@pytest.mark.parametrize(
    ["value"], [("TR_NORMAL_WS",), ("TR_NORMAL_WS_WPM",), ("TR_MALL_WS",)]
)
def test_get_enum_value(zeep_client, value):
    enum_value = zeep_client.get_enum_value("wsTransactionType", value)
    assert value == enum_value


def test_baseclass(zeep_client):
    assert isinstance(zeep_client, SoapClient)


@pytest.mark.parametrize(
    ["type_name", "value"],
    [
        ("doesnotexists", "TR_NORMAL_WS"),
        ("Type", "TR_NORMAL_WS_WPM"),
        ("object", "TR_MALL_WS"),
    ],
)
def test_get_enum_value_type_error(zeep_client, type_name, value):
    with pytest.raises(TypeDoesNotExist) as exc_info:
        zeep_client.get_enum_value(type_name, value),
    assert exc_info.value.type_name == type_name


@pytest.mark.parametrize(
    ["type_name", "kwargs"],
    [
        (
            "cardDetail",
            {"cardNumber": "1234 1234 1234 1234", "cardExpirationDate": "12/20"},
        ),
        (
            "wsTransactionDetail",
            {"amount": "1234.01", "commerceCode": "12345", "buyOrder": "12345"},
        ),
        (
            "wsInitTransactionInput",
            {
                "wSTransactionType": "TR_NORMAL",
                "returnURL": "https://example.net/return",
                "finalURL": "https://example.net/final",
            },
        ),
    ],
)
def test_create_object(zeep_client, type_name, kwargs):
    client = zeep_client.client
    card_detail_type = client.get_type("ns0:{}".format(type_name))
    expected = card_detail_type(**kwargs)

    new_object = zeep_client.create_object(type_name, **kwargs)

    assert expected == new_object


@pytest.mark.parametrize(
    ["type_name", "kwargs"],
    [
        (
            "wrongcardDetail",
            {"cardNumber": "1234 1234 1234 1234", "cardExpirationDate": "12/20"},
        ),
        (
            "wrongwsTransactionDetail",
            {"amount": "1234.01", "commerceCode": "12345", "buyOrder": "12345"},
        ),
        (
            "wrongwsInitTransactionInput",
            {
                "wSTransactionType": "TR_NORMAL",
                "returnURL": "https://example.net/return",
                "finalURL": "https://example.net/final",
            },
        ),
    ],
)
def test_create_object_type_error(zeep_client, type_name, kwargs):
    with pytest.raises(TypeDoesNotExist) as exc_info:
        zeep_client.create_object(type_name, **kwargs)

    assert exc_info.value.type_name == type_name


@pytest.mark.parametrize(
    ["type_name", "kwargs"],
    [
        (
            "cardDetail",
            {"amount": "1234.01", "commerceCode": "12345", "buyOrder": "12345"},
        ),
        (
            "wsTransactionDetail",
            {
                "wSTransactionType": "TR_NORMAL",
                "returnURL": "https://example.net/return",
                "finalURL": "https://example.net/final",
            },
        ),
        (
            "wsInitTransactionInput",
            {"cardNumber": "1234 1234 1234 1234", "cardExpirationDate": "12/20"},
        ),
    ],
)
def test_create_object_arguments_error(zeep_client, type_name, kwargs):
    with pytest.raises(TypeError):
        zeep_client.create_object(type_name, **kwargs)


@pytest.mark.parametrize(
    ["method_name", "args", "kwargs"],
    [
        ("wrong_method_name", (1, "args"), {}),
        ("Method", (), {"arg": 1, "argument": "value"}),
        ("mtd", (True,), {"asd": False}),
    ],
)
def test_request_wrong_method(zeep_client, method_name, args, kwargs):
    with pytest.raises(MethodDoesNotExist) as exc_info:
        request = SoapRequest(method_name=method_name, args=args, kwargs=kwargs)
        zeep_client.request(request)

    assert exc_info.value.method_name == method_name


@pytest.mark.parametrize(
    ["method_name", "error", "code"],
    [
        ("methodName", "Invalid amount", 304),
        ("mtd", "Error", 100),
        ("metodo", "ValueError", 101),
    ],
)
def test_request_server_exception(mock, zeep_client, method_name, error, code):
    fault_code = "soap:Server"
    message = "<!-- {error}({code}) -->".format(error=error, code=code)
    method = mock.Mock()
    method.side_effect = zeep.exceptions.Fault(message, fault_code)
    setattr(zeep_client.client.service, method_name, method)
    request = SoapRequest(method_name=method_name, args=(), kwargs={})

    with pytest.raises(SoapServerException) as exc_info:
        zeep_client.request(request)

    assert exc_info.value.error == error
    assert exc_info.value.code == code


@pytest.mark.parametrize(["method_name"], [("methodName",), ("mtd",), ("metodo",)])
def test_request_error(mock, zeep_client, method_name):
    error = Exception()
    request = SoapRequest(method_name=method_name, args=(), kwargs={})
    method = mock.Mock()
    exception = RequestException(error, request=request)
    method.side_effect = exception
    setattr(zeep_client.client.service, method_name, method)

    with pytest.raises(SoapRequestException) as exc_info:
        zeep_client.request(request)

    assert exc_info.value.request is request
    assert exc_info.value.error is exception


def test_request_verified(mock, requests_mock, fixture_data, zeep_client):
    expected_response = fixture_data("acknowledgeTransaction.response.xml").encode()
    requests_mock.register_uri(
        "POST",
        "https://webpay3g.transbank.cl:443/WSWebpayTransaction/cxf/WSWebpayService",
        content=expected_response,
    )
    request = SoapRequest(
        method_name="acknowledgeTransaction", args=("token",), kwargs={}
    )

    with mock.patch(
        "tbk.soap.zeep_client.verify_envelope", return_value=True
    ) as verifier:
        zeep_client.request(request)

    assert 1 == verifier.call_count


def test_request_with_signature(mock, requests_mock, fixture_data, zeep_client):
    expected_response = fixture_data("acknowledgeTransaction.response.xml").encode()
    requests_mock.register_uri(
        "POST",
        "https://webpay3g.transbank.cl:443/WSWebpayTransaction/cxf/WSWebpayService",
        content=expected_response,
    )
    request = SoapRequest(
        method_name="acknowledgeTransaction", args=("token",), kwargs={}
    )

    with mock.patch.multiple(
        "tbk.soap.zeep_client", verify_envelope=mock.DEFAULT, sign_envelope=mock.DEFAULT
    ) as patches:
        patches["verify_envelope"].return_value = True
        zeep_client.request(request)
        assert 1 == patches["sign_envelope"].call_count


def test_request_not_verified(mock, requests_mock, fixture_data, zeep_client):
    expected_response = fixture_data("acknowledgeTransaction.response.xml").encode()
    requests_mock.register_uri(
        "POST",
        "https://webpay3g.transbank.cl:443/WSWebpayTransaction/cxf/WSWebpayService",
        content=expected_response,
    )
    request = SoapRequest(
        method_name="acknowledgeTransaction", args=("token",), kwargs={}
    )

    with mock.patch("tbk.soap.zeep_client.verify_envelope", return_value=False):
        with pytest.raises(InvalidSignatureResponse):
            zeep_client.request(request)


def test_request_sent_received_data(mock, requests_mock, fixture_data, zeep_client):
    expected_response = fixture_data("acknowledgeTransaction.response.xml")
    requests_mock.register_uri(
        "POST",
        "https://webpay3g.transbank.cl:443/WSWebpayTransaction/cxf/WSWebpayService",
        content=expected_response.encode(),
    )
    request = SoapRequest(
        method_name="acknowledgeTransaction", args=("token",), kwargs={}
    )

    with mock.patch("tbk.soap.zeep_client.verify_envelope", return_value=True):
        with mock.patch.object(
            zeep_client.client.service,
            "acknowledgeTransaction",
            side_effect=zeep_client.client.service.acknowledgeTransaction,  # set a sentinel
        ) as method:
            result, last_sent, last_received = zeep_client.request(request)

        method.assert_called_once_with("token")
        assert expected_response.strip() == last_received

        first = etree.tostring(
            etree.fromstring(requests_mock.last_request.text.encode())
        )
        second = etree.tostring(etree.fromstring(last_sent))
        assert first == second
