
import re

import xmlsec


def parse_tbk_error_message(raw_message):
    message_match = re.search(r'<!--(.+?)-->', raw_message)
    if message_match:
        message = message_match.group(1).strip()
        match = re.search(r'(.+?)\((\d+?)\)', message)
        if match:
            error = match.group(1)
            code = int(match.group(2))
            return error, code
        return message, -1
    return raw_message, -1


def load_key_from_data(key_data, cert_data=None, password=None, key_format=xmlsec.KeyFormat.PEM):
    key = xmlsec.Key.from_memory(key_data, key_format, password)
    if cert_data:
        key.load_cert_from_memory(cert_data, key_format)
    return key
