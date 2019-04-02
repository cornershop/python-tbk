from .requestor import SoapRequestor, SoapResponse, SoapRequest  # noqa
from .zeep_client import ZeepSoapClient

default_client_class = ZeepSoapClient


def create_soap_requestor(wsdl_url, commerce, client_class=None, **client_kwargs):
    soap_client_class = default_client_class if client_class is None else client_class
    soap_client = soap_client_class(
        wsdl_url=wsdl_url,
        key_data=commerce.key_data,
        cert_data=commerce.cert_data,
        tbk_cert_data=commerce.tbk_cert_data,
        password=commerce.key_password,
        **client_kwargs
    )
    return SoapRequestor(soap_client)
