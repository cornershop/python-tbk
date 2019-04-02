# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Commerce(object):
    def __init__(
        self,
        commerce_code,
        key_data,
        cert_data,
        tbk_cert_data,
        environment,
        key_password=None,
    ):
        self.commerce_code = commerce_code
        self.key_data = key_data
        self.cert_data = cert_data
        self.tbk_cert_data = tbk_cert_data
        self.environment = environment
        self.key_password = key_password

    @classmethod
    def init_from_files(
        cls,
        commerce_code,
        key_file,
        cert_file,
        tbk_cert_file,
        environment,
        key_password=None,
    ):
        key_data = _read_file(key_file)
        cert_data = _read_file(cert_file)
        tbk_cert_data = _read_file(tbk_cert_file)
        return cls(
            commerce_code, key_data, cert_data, tbk_cert_data, environment, key_password
        )


def _read_file(f_name):
    with open(f_name, "rb") as f:
        return f.read()
