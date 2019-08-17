import os

import pytest
from lxml import etree

from tbk.commerce import Commerce
from tbk.environments import DEVELOPMENT
from tbk.soap.soap_client import SoapClient


@pytest.fixture()
def mock():
    try:
        import mock
    except ImportError:
        from unittest import mock
    return mock


@pytest.fixture()
def fixtures_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture()
def fixture_data(fixtures_dir):
    def loader(filename):
        try:
            with open(os.path.join(fixtures_dir, filename), "r") as f:
                return f.read()
        except OSError:  # pragma: no cover
            raise LookupError("Cannot find fixture data '{}'".format(filename))

    return loader


@pytest.fixture()
def commerce_keys_data(fixture_data):
    def get_keys(commerce_id):
        key_data = fixture_data("{}.key".format(commerce_id))
        cert_data = fixture_data("{}.crt".format(commerce_id))
        tbk_cert_data = fixture_data("tbk.pem")
        return (key_data, cert_data, tbk_cert_data)

    return get_keys


@pytest.fixture()
def commerce(commerce_keys_data):
    def get_commerce_by_code(commerce_code, environment=DEVELOPMENT):
        key_data, cert_data, tbk_cert_data = commerce_keys_data(commerce_code)
        return Commerce(
            commerce_code=commerce_code,
            key_data=key_data,
            cert_data=cert_data,
            tbk_cert_data=tbk_cert_data,
            environment=environment,
        )

    return get_commerce_by_code


@pytest.fixture()
def default_commerce(commerce):
    commerce_code = "597020000547"
    return commerce(commerce_code)


@pytest.fixture()
def xml_envelope(fixture_data):
    def get_xml_envelope(filename):
        return etree.fromstring(fixture_data(filename).encode("utf-8"))

    return get_xml_envelope


@pytest.fixture
def soap_client(mock):
    mocker_client = mock.MagicMock(spec=SoapClient)
    mocker_client.request.return_value = (
        mock.MagicMock(spec=dict),
        mock.MagicMock(spec=str),
        mock.MagicMock(spec=str),
    )
    return mocker_client
