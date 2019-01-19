import re

import xmlsec
from lxml import etree


def parse_tbk_error_message(raw_message):
    message_match = re.search(r"<!--(.+?)-->", raw_message)
    if message_match:
        message = message_match.group(1).strip()
        match = re.search(r"(.+?)\((\d+?)\)", message)
        if match:
            error = match.group(1)
            code = int(match.group(2))
            return error, code
        return message, -1
    return raw_message, -1


def get_key_format_value(key_format):
    try:
        return getattr(xmlsec.KeyFormat, key_format)
    except AttributeError:
        raise ValueError("Key format {} unsupported".format(key_format))


def load_key_from_data(key_data, cert_data=None, password=None, key_format="PEM"):
    key_format = get_key_format_value(key_format)
    key = xmlsec.Key.from_memory(key_data, key_format, password)
    if cert_data:
        key.load_cert_from_memory(cert_data, key_format)
    return key


def xml_to_string(tree):
    return etree.tostring(tree).decode("utf-8")


def create_xml_element(tag_name, nsmap=None):
    return etree.Element(tag_name, nsmap=nsmap)
