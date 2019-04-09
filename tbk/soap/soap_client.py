import logging
import abc

try:
    # noinspection PyUnresolvedReferences
    AbstractBaseClass = abc.ABC
except AttributeError:  # pragma: no cover
    AbstractBaseClass = abc.ABCMeta("ABC", (object,), {"__slots__": ()})


class SoapClient(AbstractBaseClass):
    # noinspection PyUnusedLocal
    def __init__(self, wsdl_url, key_data, cert_data, tbk_cert_data, password=None):
        self.logger = logging.getLogger(
            "tbk.soap.client.{}".format(self.__class__.__name__)
        )
        self.logger.info("Initializing soap client for wsdl: %s", wsdl_url)

    @abc.abstractmethod
    def get_enum_value(self, enum_name, value):
        raise NotImplementedError

    @abc.abstractmethod
    def create_object(self, type_name, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def request(self, request, timeout=None):
        raise NotImplementedError
